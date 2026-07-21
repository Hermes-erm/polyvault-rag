# Poly-vault

A multimodal RAG service that ingests documents, chunks them by meaning, stores them in a vector database, and answers questions grounded strictly in the retrieved context.

![Architecture](/docs/rag-architecture.jpg)

## How it works

**Ingestion**

1. **Parse** — Docling converts each file (PDF, image, DOCX, CSV, XLSX, MD) into Markdown.
2. **Split** — BlingFire breaks the text into sentences.
3. **Chunk** — sentences are grouped into chunks by cosine similarity between sliding windows, so boundaries land where the topic shifts.
4. **Store** — chunks are embedded (MiniLM) and upserted into ChromaDB with metadata.

**Query**

1. Your question is embedded and used to retrieve the top `k × 2` candidate chunks.
2. A Cohere reranker narrows them to the best `k`.
3. Gemini answers from those chunks under a strict "only use the context" prompt.

## Features

- **Multimodal ingestion** — PDF, image, CSV, DOCX, XLSX, Markdown through one converter.
- **Semantic chunking** — meaning-based boundaries instead of fixed lengths.
- **Two-stage retrieval** — fast bi-encoder recall, then a cross-encoder reranker for precision.
- **Grounded answers** — the model can't answer outside the retrieved context.
- **Async ingestion** — uploads are processed in the background.
- **Persistent store** — ChromaDB persists to disk between runs.

## Stack

FastAPI · Docling · BlingFire · ChromaDB · MiniLM embeddings · Cohere reranker · Gemini

## Project structure

```
poly-vault/
├── rag_system/
│   ├── document_processor.py   # Parse → split → chunk → store
│   ├── retriever.py            # ChromaDB store, query, rerank
│   ├── generator.py            # Gemini service + RAG prompt
│   └── utils.py                # Logger, models
├── app/
│   ├── main.py                 # FastAPI app + routers
│   ├── api.py                  # File + query routes
│   └── dependencies.py         # Singleton wiring
├── pipeline/{staging,processed}/
├── chromadb/                   # Vector store
├── docs/architecture.png
└── .env
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env`:

```env
COHERE_API_KEY=your_key
GEMINI_API_KEY=your_key
```

Run:

```bash
polyvault-rag/src/app: fastapi run main.py | uvicorn app.main:app --reload
```

Docs at `http://127.0.0.1:8000/docs`.

## API

| Method   | Endpoint                  | Description                                     |
| -------- | ------------------------- | ----------------------------------------------- |
| `POST`   | `/rag/files/import`       | Upload a document (processed in the background) |
| `GET`    | `/query/search?query=...` | Ask a question, get an answer                   |
| `POST`   | `/query/retrieve/`        | Return the top chunks only                      |
| `DELETE` | `/query/reset-vector/`    | Clear a collection                              |

## Example

```bash
# Upload
curl -X POST http://127.0.0.1:8000/rag/files/import -F "file=@doc.pdf"

# Ask
curl "http://127.0.0.1:8000/query/search?query=What is the refund policy?"
```

## Notes

- Model names (embedder, reranker, LLM) are set in `dependencies.py` — swap them there.
- The tokenizer loads with `local_files_only=True`, so the MiniLM model must be cached locally.
- `reset-vector` wipes data — use with care.
