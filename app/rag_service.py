import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .models import Document, QAHistory

class RAGService:
    """
    سرویس مدیریت فرآیند RAG شامل تقسیم‌بندی اسناد، بردارسازی، جستجوی شباهت و استنتاج معنایی.
    """
    
    @staticmethod
    def get_embeddings_model():
        """
        راه‌اندازی مدل بردارسازی با تزریق مستقیم هدرهای احراز هویت پلتفرم OpenRouter.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("تنظیم متغیر محیطی OPENROUTER_API_KEY برای این بخش ضروری است.")
        
        custom_headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost:8000",
            "X-OpenRouter-Title": "Django Doc RAG Engine"
        }
        
        return OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers=custom_headers
        )

    @staticmethod
    def build_local_vector_index():
        """
        پیمایش تمامی اسناد موجود در پایگاه داده جنگو، قطعه‌بندی هوشمند متن و ساخت نمایه برداری با FAISS.
        """
        documents = Document.objects.exclude(full_text="")
        if not documents.exists():
            return None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,       
            chunk_overlap=80      
        )

        all_chunks = []
        metadatas = []

        for doc in documents:
            chunks = text_splitter.split_text(doc.full_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                metadatas.append({
                    "doc_id": doc.id,
                    "title": doc.title
                })

        if not all_chunks:
            return None

        embeddings = RAGService.get_embeddings_model()
        vector_store = FAISS.from_texts(
            texts=all_chunks,
            embedding=embeddings,
            metadatas=metadatas
        )
        return vector_store

    @staticmethod
    def ask_question(question_text):
        """
        انجام فرآیند تولید پاسخ مبتنی بر بازیابی معنایی با استفاده از کلاینت استاندارد OpenAI متصل به OpenRouter.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        vector_store = RAGService.build_local_vector_index()
        
        if not vector_store:
            return "در حال حاضر هیچ سند مرجعی در پایگاه داده سامانه یافت نشد. لطفاً ابتدا اسناد را بارگذاری کنید.", ""

        # استفاده از بازیاب به همراه فیلتر شباهت برای بازیابی ۳ سند برتر مرتبط
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        retrieved_documents = retriever.invoke(question_text)
        
        # ترکیب محتوای قطعات بازیابی شده جهت ایجاد بافتار جامع
        context_content = "\n\n---\n\n".join([doc.page_content for doc in retrieved_documents])

        llm = ChatOpenAI(
            model="openai/gpt-oss-120b:free",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.15,  
            max_tokens=1024,
            default_headers={
                "HTTP-Referer": "https://localhost:8000",       
                "X-OpenRouter-Title": "Django Doc RAG Engine"    
            }
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "شما دستیار تحلیل‌گر هوشمند اطلاعات هستید. وظیفه شما پاسخ‌گویی دقیق و مستند به پرسش کاربر بر اساس بافتار ضمیمه‌شده است.\n\n"
                       "قوانین حیاتی عملکرد شما:\n"
                       "۱. فقط و فقط از اطلاعات موجود در بخش 'بافتار اسناد مرجع' استفاده کنید.\n"
                       "۲. اگر پاسخ در متن ضمیمه نیست، با کمال احترام بگویید: 'اطلاعات کافی برای پاسخ به این سوال در اسناد بارگذاری‌شده وجود ندارد.'\n"
                       "۳. تحت هیچ شرایطی از دانش عمومی خود خارج از اسناد استفاده نکنید یا پاسخ‌های حدسی تولید نکنید.\n"
                       "۴. ساختار خروجی شما باید منسجم، فارسی، روان و بدون استفاده از متون بیهوده باشد.\n\n"
                       "بافتار اسناد مرجع:\n{context}"),
            ("human", "{question}")
        ])

        chain = (
            {"context": lambda x: context_content, "question": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )

        answer = chain.invoke(question_text)

        # 🟢 اصلاح باگ متادیتا: دسترسی به آبجکتِ نخستین داکیومنتِ داخل لیست
        associated_document = None
        if retrieved_documents and len(retrieved_documents) > 0:
            first_document = retrieved_documents[0]
            # مطمئن می‌شویم که شیء حتما متادیتا دارد
            if hasattr(first_document, 'metadata') and first_document.metadata:
                doc_id = first_document.metadata.get("doc_id")
                if doc_id:
                    associated_document = Document.objects.filter(id=doc_id).first()

        # ثبت سوابق پرسش و پاسخ
        QAHistory.objects.create(
            document=associated_document,
            question=question_text,
            answer=answer,
            retrieved_context=context_content
        )

        return answer, context_content