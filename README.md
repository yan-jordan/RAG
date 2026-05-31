# 🚀 Django RAG Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![FAISS](https://img.shields.io/badge/Vector_DB-FAISS-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

> A production-ready **Retrieval-Augmented Generation (RAG)** platform built with **Django**, **LangChain**, **FAISS**, and **Large Language Models (LLMs)**. Upload Word documents, automatically extract their content, generate semantic embeddings, and ask intelligent questions grounded entirely in your own data.

---

## 📖 Overview

Django RAG Engine combines document processing, vector search, and modern LLMs to provide accurate, context-aware answers from uploaded documents.

The system automatically:

1. Accepts document uploads (`.docx`)
2. Extracts and cleans text
3. Splits content into semantic chunks
4. Generates embeddings
5. Stores vectors in FAISS
6. Retrieves relevant context for user queries
7. Sends context to an LLM
8. Returns grounded responses

This enables organizations and developers to create private document assistants, knowledge bases, internal search engines, and AI-powered support systems.

---

## ✨ Features

### 📄 Document Management

* Upload Microsoft Word (`.docx`) files
* Automatic text extraction using `python-docx`
* Persistent document storage
* Admin-based document management

### 🧠 Retrieval-Augmented Generation (RAG)

* Intelligent semantic document retrieval
* Context-aware question answering
* Hallucination reduction through document grounding
* Retrieval based on vector similarity search

### 🔍 Semantic Search

* OpenAI Embeddings (`text-embedding-3-large`)
* FAISS vector indexing
* Fast local similarity search
* Highly relevant context retrieval

### 🤖 AI-Powered Responses

* OpenRouter integration
* GPT-4o support
* Easily switch between models
* Context-constrained answers

### ⚙️ Django Admin Integration

* Upload documents directly from Admin
* Query document engine from Admin dashboard
* View retrieval history
* Monitor generated answers

### 🌐 REST API

* Programmatic document querying
* JSON-based responses
* Easy integration with frontend applications
* Suitable for web, mobile, and enterprise systems

### 📊 Interaction Logging

* Stores user questions
* Stores retrieved contexts
* Stores generated answers
* Useful for debugging and evaluation

### 🐳 Containerized Deployment

* Docker support
* Docker Compose support
* Simple deployment workflow
* Environment-based configuration

---

# 🏗 Architecture

```text
                ┌─────────────────┐
                │   DOCX Upload   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Text Extraction │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Text Chunking   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Embeddings      │
                │ text-embedding  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ FAISS Vector DB │
                └────────┬────────┘
                         │
                         ▼
          User Question ───────────► Retrieval
                                        │
                                        ▼
                            Relevant Context
                                        │
                                        ▼
                              GPT-4o / LLM
                                        │
                                        ▼
                                 Final Answer
```

---

# 🛠 Technology Stack

| Component        | Technology                    |
| ---------------- | ----------------------------- |
| Backend          | Django                        |
| API              | Django REST Framework         |
| AI Framework     | LangChain                     |
| Vector Store     | FAISS                         |
| Embeddings       | OpenAI text-embedding-3-large |
| LLM Provider     | OpenRouter                    |
| LLM Models       | GPT-4o and compatible models  |
| Database         | SQLite                        |
| File Processing  | python-docx                   |
| Containerization | Docker                        |
| Orchestration    | Docker Compose                |

---

# 📂 Project Structure

```text
.
├── app/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── rag_service.py
│   ├── urls.py
│   └── ...
│
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── media/
│   └── documents/
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── manage.py
└── README.md
```

---

# ⚡ Installation

## Prerequisites

* Python 3.10+
* Docker
* Docker Compose
* OpenRouter API Key

---

## 1. Clone Repository

```bash
git clone https://github.com/your-username/django-rag-engine.git

cd django-rag-engine
```

---

## 2. Create Environment File

Create a `.env` file in the project root:

```env
DEBUG=True

SECRET_KEY=change_me

OPENROUTER_API_KEY=your_api_key_here

OPENAI_API_BASE=https://openrouter.ai/api/v1
```

---

## 3. Install Dependencies (Local Development)

```bash
pip install -r requirements.txt
```

---

## 4. Run Database Migrations

```bash
python manage.py migrate
```

---

## 5. Create Superuser

```bash
python manage.py createsuperuser
```

---

## 6. Start Development Server

```bash
python manage.py runserver
```

Application:

```text
http://localhost:8000
```

Admin Panel:

```text
http://localhost:8000/admin
```

---

# 🐳 Docker Deployment

## Build Containers

```bash
docker-compose build
```

## Start Services

```bash
docker-compose up -d
```

## View Logs

```bash
docker-compose logs -f
```

## Stop Services

```bash
docker-compose down
```

---

## Create Admin User

```bash
docker-compose exec web python manage.py createsuperuser
```

---

# 📖 Usage

## Upload Documents

1. Open Django Admin.
2. Navigate to **Documents**.
3. Upload a `.docx` file.
4. Save the document.
5. Text extraction and indexing happen automatically.

---

## Ask Questions

Example:

```text
What are the main conclusions of the uploaded report?
```

The system:

* Retrieves relevant chunks
* Sends context to the LLM
* Returns an answer grounded in the document

---

# 🔌 API Reference

## Ask Question

### Endpoint

```http
POST /api/ask/
```

### Request

```json
{
  "question": "What is the summary of document X?"
}
```

### Response

```json
{
  "answer": "The document discusses...",
  "sources": [
    "Relevant retrieved chunk 1",
    "Relevant retrieved chunk 2"
  ]
}
```

---

## Example cURL

```bash
curl -X POST \
http://localhost:8000/api/ask/ \
-H "Content-Type: application/json" \
-d '{
  "question": "Summarize the uploaded document"
}'
```

---

# ⚙️ Configuration

## Change Language

In `settings.py`:

```python
LANGUAGE_CODE = "fa-ir"
```

Examples:

```python
LANGUAGE_CODE = "en-us"
```

```python
LANGUAGE_CODE = "de-de"
```

---

## Change LLM Model

In `rag_service.py`:

```python
model="openai/gpt-4o"
```

Examples:

```python
model="anthropic/claude-sonnet-4"
```

```python
model="google/gemini-2.5-pro"
```

```python
model="meta-llama/llama-4"
```

---

## Change Embedding Model

```python
text-embedding-3-large
```

to:

```python
text-embedding-3-small
```

or another supported embedding model.

---

# 🗄 Database

Default database:

```text
SQLite
```

For production:

```text
PostgreSQL
```

Recommended stack:

* PostgreSQL
* Redis
* Gunicorn
* Nginx

---

# 🔒 Security Recommendations

For production environments:

### Store Secrets in Environment Variables

Never commit:

```env
SECRET_KEY
OPENROUTER_API_KEY
DATABASE_URL
```

---

### Disable Debug

```env
DEBUG=False
```

---

### Configure Allowed Hosts

```python
ALLOWED_HOSTS = [
    "your-domain.com"
]
```

---

### Enable HTTPS

Use:

* Nginx
* Cloudflare
* Traefik
* AWS Load Balancer

---

# 📈 Future Improvements

* PDF support
* Multi-document retrieval
* Hybrid search (BM25 + Vector Search)
* Streaming responses
* Chat history memory
* User authentication
* Multi-tenant architecture
* PostgreSQL pgvector support
* Source citation highlighting
* Frontend dashboard (React / Next.js)
* OpenTelemetry monitoring

---

# 🧪 Development Workflow

### Run Tests

```bash
python manage.py test
```

### Check Migrations

```bash
python manage.py makemigrations
```

### Apply Migrations

```bash
python manage.py migrate
```

### Collect Static Files

```bash
python manage.py collectstatic
```

---

# 📸 Screenshots

## Admin Dashboard

```text
Add screenshot here
```

## Document Upload

```text
Add screenshot here
```

## Ask Document Engine

```text
Add screenshot here
```

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push branch

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# 📝 License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge,
to any person obtaining a copy of this software
and associated documentation files...
```

---

# 🙏 Acknowledgements

* Django
* Django REST Framework
* LangChain
* FAISS
* OpenAI
* OpenRouter
* Python-Docx

---

## ⭐ Support

If you find this project useful, please consider giving it a star on GitHub.

```bash
⭐ Star the repository
🍴 Fork the repository
🚀 Build something awesome
```
