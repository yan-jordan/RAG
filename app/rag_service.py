"""RAG pipeline: chunk → embed → FAISS → retrieve → LLM.

The vector index is cached in-process and only rebuilt when the set of
documents (or the chunking/embedding settings) changes, so repeated questions
cost one embedding call instead of re-embedding the whole corpus every time.
"""
import hashlib
import logging
import math
import re
import threading
from dataclasses import dataclass, field

from django.conf import settings
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .models import Document, QAHistory

log = logging.getLogger(__name__)

NO_DOCUMENTS_MESSAGE = "هنوز سندی بارگذاری نشده است. ابتدا یک فایل Word اضافه کنید."
NOT_FOUND_MESSAGE = "اطلاعات کافی برای پاسخ به این سوال در اسناد بارگذاری‌شده وجود ندارد."

SYSTEM_PROMPT = (
    "شما دستیار تحلیل‌گر هوشمند اطلاعات هستید. وظیفه شما پاسخ‌گویی دقیق و مستند به پرسش کاربر "
    "بر اساس بافتار ضمیمه‌شده است.\n\n"
    "قوانین حیاتی عملکرد شما:\n"
    "۱. فقط و فقط از اطلاعات موجود در بخش «بافتار اسناد مرجع» استفاده کنید.\n"
    "۲. اگر پاسخ در متن ضمیمه نیست، با کمال احترام بگویید: "
    f"«{NOT_FOUND_MESSAGE}»\n"
    "۳. تحت هیچ شرایطی از دانش عمومی خود خارج از اسناد استفاده نکنید یا پاسخ حدسی تولید نکنید.\n"
    "۴. پاسخ باید منسجم، فارسی، روان و مختصر باشد؛ در صورت نیاز از فهرست یا Markdown ساده استفاده کنید.\n\n"
    "بافتار اسناد مرجع:\n{context}"
)


class RAGConfigError(Exception):
    """Service isn't configured (e.g. missing API key)."""


class RAGUpstreamError(Exception):
    """The embedding / LLM provider failed."""


@dataclass
class RAGAnswer:
    answer: str
    context: str = ""
    sources: list = field(default_factory=list)
    history: QAHistory | None = None


# ── Offline demo mode ───────────────────────────────────────────────────
class HashingEmbeddings(Embeddings):
    """Tiny lexical embedding (hashed words + char trigrams). No network, no key."""

    DIM = 768
    _token = re.compile(r"\w+", re.UNICODE)

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for word in self._token.findall(text.lower()):
            grams = [(word, 1.0)] + [(word[i : i + 3], 0.35) for i in range(max(len(word) - 2, 0))]
            for gram, weight in grams:
                h = int(hashlib.md5(gram.encode()).hexdigest()[:8], 16)
                vec[h % self.DIM] += weight
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)


_STOPWORDS = {
    "است", "هست", "بود", "چند", "چقدر", "چیه", "چیست", "کدام", "کدوم", "چه", "چطور", "را",
    "آیا", "از", "در", "به", "که", "این", "آن", "با", "برای", "های", "هر", "یا", "تا", "می",
}


def _demo_answer(question: str, passages: list[str]) -> str:
    """Extractive answer: the sentences that best overlap the question's keywords."""
    words = [w for w in re.findall(r"\w+", question.lower()) if len(w) > 2 and w not in _STOPWORDS]
    stems = {w[:4] if len(w) >= 5 else w for w in words}
    sentences = [
        s.strip()
        for p in passages
        for s in re.split(r"(?<=[.!؟?۔\n])\s+", p)
        if len(s.strip()) > 40
    ]

    def score(sentence: str) -> int:
        low = sentence.lower()
        return sum(1 for stem in stems if stem in low)

    ranked = sorted(enumerate(sentences), key=lambda item: (-score(item[1]), item[0]))
    needed = max(1, math.ceil(len(stems) / 3))  # a lone shared word isn't evidence
    picked = [(i, s) for i, s in ranked if score(s) >= needed][:2]
    if not picked:
        return NOT_FOUND_MESSAGE
    return "\n\n".join(f"- {s}" for _, s in sorted(picked))


# ── Providers ───────────────────────────────────────────────────────────
def _require_key() -> str:
    key = settings.OPENROUTER_API_KEY
    if not key:
        raise RAGConfigError("متغیر محیطی OPENROUTER_API_KEY تنظیم نشده است.")
    return key


def _headers() -> dict:
    return {"HTTP-Referer": settings.APP_URL, "X-OpenRouter-Title": "RAG Document Assistant"}


def get_embeddings() -> Embeddings:
    if settings.RAG_DEMO_MODE:
        return HashingEmbeddings()
    return OpenAIEmbeddings(
        model=settings.RAG_EMBEDDING_MODEL,
        openai_api_key=_require_key(),
        openai_api_base=settings.OPENROUTER_BASE_URL,
        default_headers=_headers(),
    )


def get_llm():
    return ChatOpenAI(
        model=settings.RAG_CHAT_MODEL,
        openai_api_key=_require_key(),
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=0.15,
        max_tokens=settings.RAG_MAX_TOKENS,
        default_headers=_headers(),
    )


# ── Index cache ─────────────────────────────────────────────────────────
_lock = threading.Lock()
_cache: dict = {"fingerprint": None, "store": None}


def _ready_documents():
    return list(
        Document.objects.filter(status=Document.Status.READY)
        .exclude(full_text="")
        .only("id", "title", "full_text")
        .order_by("id")
    )


def get_vector_store(documents=None):
    documents = _ready_documents() if documents is None else documents
    if not documents:
        return None

    fingerprint = (
        tuple((d.id, len(d.full_text)) for d in documents),
        settings.RAG_CHUNK_SIZE,
        settings.RAG_CHUNK_OVERLAP,
        "demo" if settings.RAG_DEMO_MODE else settings.RAG_EMBEDDING_MODEL,
    )
    with _lock:
        if _cache["fingerprint"] == fingerprint and _cache["store"] is not None:
            return _cache["store"]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE, chunk_overlap=settings.RAG_CHUNK_OVERLAP
        )
        texts, metadatas = [], []
        for doc in documents:
            for index, chunk in enumerate(splitter.split_text(doc.full_text)):
                texts.append(chunk)
                metadatas.append({"doc_id": doc.id, "title": doc.title, "chunk": index})
        if not texts:
            return None

        try:
            store = FAISS.from_texts(texts=texts, embedding=get_embeddings(), metadatas=metadatas)
        except RAGConfigError:
            raise
        except Exception as exc:
            log.exception("Embedding / indexing failed")
            raise RAGUpstreamError(f"ساخت نمایه برداری ناموفق بود: {str(exc)[:200]}") from exc

        _cache.update(fingerprint=fingerprint, store=store)
        return store


def reset_index_cache():
    with _lock:
        _cache.update(fingerprint=None, store=None)


# ── Public API ──────────────────────────────────────────────────────────
class RAGService:
    @staticmethod
    def ask_question(question: str, document_ids=None) -> RAGAnswer:
        all_documents = _ready_documents()
        documents = all_documents
        if document_ids:
            wanted = set(document_ids)
            documents = [d for d in all_documents if d.id in wanted]
        if not documents:
            return RAGAnswer(answer=NO_DOCUMENTS_MESSAGE)

        # the index always covers every ready document; scoping is a metadata filter
        store = get_vector_store(all_documents)
        search = {"k": settings.RAG_TOP_K}
        if document_ids:
            allowed = {d.id for d in documents}
            search.update(filter=lambda meta: meta.get("doc_id") in allowed, fetch_k=store.index.ntotal)

        try:
            hits = store.similarity_search(question, **search)
        except RAGConfigError:
            raise
        except Exception as exc:
            log.exception("Retrieval failed")
            raise RAGUpstreamError(f"بازیابی از نمایه ناموفق بود: {str(exc)[:200]}") from exc
        if not hits:
            return RAGAnswer(answer=NOT_FOUND_MESSAGE)

        context = "\n\n---\n\n".join(f"[{h.metadata['title']}]\n{h.page_content}" for h in hits)
        sources = [
            {"doc_id": h.metadata["doc_id"], "title": h.metadata["title"], "snippet": h.page_content}
            for h in hits
        ]

        if settings.RAG_DEMO_MODE:
            answer = _demo_answer(question, [h.page_content for h in hits])
        else:
            try:
                chain = ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_PROMPT), ("human", "{question}")]
                ) | get_llm() | StrOutputParser()
                answer = chain.invoke({"context": context, "question": question})
            except RAGConfigError:
                raise
            except Exception as exc:
                log.exception("LLM call failed")
                raise RAGUpstreamError(f"پاسخ‌دهی مدل زبانی ناموفق بود: {str(exc)[:200]}") from exc

        primary = Document.objects.filter(id=sources[0]["doc_id"]).first()
        history = QAHistory.objects.create(
            document=primary,
            question=question,
            answer=answer,
            retrieved_context=context,
            sources=sources,
        )
        return RAGAnswer(answer=answer, context=context, sources=sources, history=history)
