# Porsand — case study

*A Persian-first RAG app where every answer shows the sentences it came from.*

**Stack:** Django 4.2 · DRF · LangChain · FAISS · Next.js 16 · Tailwind v4 · TypeScript · Docker
**Role:** solo — product, backend, retrieval pipeline, UI design
**Repo:** https://github.com/yan-jordan/RAG · **Demo GIF:** [`demo.gif`](demo.gif)

## The problem

Question-answering over private documents is easy to demo and hard to trust. Typical RAG UIs print an answer and dump the retrieved context underneath, so the reader has to find the supporting text themselves. For contracts, policies and reports — the documents people actually ask about — that last step is the whole point.

## What I built

- A document-grounded Q&A service: upload `.docx`, extract paragraphs and tables, chunk, embed, retrieve with FAISS, answer with an LLM under a strict "only from the context" prompt.
- A Persian, right-to-left web app where retrieved passages are split into sentences and **only the sentences the answer used are highlighted**, so verification takes seconds.
- Scoped questions (restrict retrieval to selected documents), history, light/dark themes, a mobile layout.

## Decisions worth talking about

| Decision | Why |
| --- | --- |
| Cache the FAISS index, keyed by a fingerprint of (document ids + text lengths + chunk/embedding settings) | The original rebuilt and re-embedded the whole corpus on every question. Now it embeds once and again only when something changes; a test asserts the number of index builds. |
| Mark failed extractions as `failed` instead of storing the error text in `full_text` | The original wrote the exception message into the document body, so it was chunked, embedded and could be "retrieved" as evidence. A data migration repairs rows created that way. |
| Evidence highlighting computed on the client from stems of answer vs. sentence | Needs no extra LLM call or provider support for citations, and degrades gracefully: if nothing overlaps strongly, it marks the single best sentence. |
| Offline demo mode (hashed lexical embeddings + extractive answers) | Reviewers can run the project without an API key, and the test-suite exercises the whole pipeline without network access. |
| Removed Django admin, JSON-only API with a throttled `/ask/` endpoint, explicit 502/503 errors | The UI is the product; the API should fail in ways a client can explain to a user. |
| Design: one memorable device (the highlighter), everything else quiet | Blue means "you can act", yellow means "this is from your document". Single typeface (Vazirmatn), no card grid, no gradients. |

## Engineering notes

- 16 backend tests (upload validation, forged `.docx`, table extraction, scoped retrieval, caching, LLM path with a fake chat model, error mapping).
- Frontend passes `tsc`, `eslint` and a production build; layout verified at 390 px with no horizontal overflow.
- Everything configurable through env vars; `SECRET_KEY` is mandatory when `DEBUG=False`.

## Honest limitations

No authentication, single-process index cache, `.docx` only, and the live OpenRouter path is tested with fakes rather than against the provider. The README lists these up front.

## Resume bullets

- Built **Porsand**, a Persian-language RAG web app (Django, LangChain, FAISS, Next.js/Tailwind) that answers questions from uploaded Word documents and highlights the exact source sentences behind each answer.
- Cut redundant embedding work by caching the FAISS index behind a content fingerprint (rebuild only when documents or settings change); fixed a data-integrity bug where extraction errors were being indexed as document text, with a repair migration.
- Designed and shipped an RTL, responsive, light/dark UI; added an offline demo mode and a 16-test suite that runs the full retrieval pipeline without network access.

## LinkedIn post (draft)

> I rebuilt my RAG side project around one idea: **an answer you can't verify isn't an answer.**
> Porsand lets you upload Word files, ask in Persian, and shows the exact sentences each answer was built from — highlighted like a pen on paper.
> Under the hood: Django + LangChain + FAISS, a cached vector index, scoped retrieval, and a Next.js/Tailwind RTL UI.
> Runs offline in demo mode, too. Code + screenshots in the repo.
