# RAG System with Gemini and FAISS

This is a Retrieval-Augmented Generation (RAG) system built using Google's Gemini model and FAISS vector database.

## Features

- PDF document processing and indexing
- Semantic search using FAISS vector database
- Question answering using Gemini model
- DOI link extraction and inclusion
- FastAPI-based REST API

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```
GOOGLE_API_KEY=your_google_api_key_here
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=true
LLM_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=models/embedding-001
```

## Usage

### 1. Building the Vector Database

1. Place your PDF documents in the `data/pdfs` directory.

2. Run the vector database builder script:
```bash
python scripts/build_vector_db.py
```

This script will:
- Process all PDFs in the `data/pdfs` directory
- Extract text content and metadata (title, DOI, keywords)
- Create embeddings using Gemini
- Build and save the FAISS index
- Save document metadata for reference

### 2. Running the RAG API

1. Start the API server:
```bash
python -m app.main
```

2. The API will be available at `http://localhost:8000`

### 3. Making Queries

Use the `/api/v1/query` endpoint to ask questions about your documents:

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Your question here", "top_k": 3}'
```

Response format:
```json
{
    "answer": "Generated answer",
    "documents": [
        {
            "title": "Document title",
            "content": "Document content",
            "doi": "DOI link",
            "keywords": ["keyword1", "keyword2"]
        }
    ],
    "doi_links": ["doi1", "doi2"]
}
```

## Directory Structure

```
rag/
├── app/                     # Application logic
│   ├── main.py             # FastAPI application
│   ├── routes.py           # API routes
│   ├── models.py           # Pydantic models
│   ├── vector_store.py     # FAISS vector store
│   ├── config.py           # Configuration
│   └── logger.py           # Logging setup
├── scripts/                 # Utility scripts
│   └── build_vector_db.py  # PDF processing and indexing
├── data/
│   ├── pdfs/               # PDF documents
│   ├── vector_db/          # FAISS index and metadata
│   └── logs/               # Application logs
└── requirements.txt        # Python dependencies
```

## Updating the Vector Database

To update the vector database with new documents:

1. Add new PDFs to the `data/pdfs` directory
2. Run the vector database builder script again:
```bash
python scripts/build_vector_db.py
```

The script will process all PDFs in the directory and update the vector database accordingly.
