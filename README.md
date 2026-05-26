# RAG Importer & Retriever

Baseline RAG system — upload PDFs, ask questions. Built with LangGraph, LangChain, PGVector and Streamlit.

## Architecture

```
Question → Executor (PGVector) → Flatten → Synthesizer → Answer
```

```
app/
├── streamlit_app.py          # entry point
├── dependency_container.py   # DI wiring
├── pages/
│   ├── importer.py           # PDF upload UI
│   └── retriever.py          # Q&A UI
├── importer/services/
│   ├── document_processor.py # chunking + chunk_id
│   └── ingestion_service.py  # load → chunk → embed → store
└── retriever/core/
    ├── graph.py              # LangGraph pipeline
    ├── state.py              # pipeline state
    └── nodes/
        ├── executor.py       # vector search
        ├── flatten.py        # dedup
        └── synthesizer.py    # answer generation

shared/
├── interfaces/               # ABCs (VectorProvider, LLMProvider, …)
└── providers/                # implementations (OpenAI, PGVector, PyMuPDF)
```

**Stack:** Streamlit · LangGraph · LangChain · OpenAI · PostgreSQL + PGVector · Docker

## Setup

### Prerequisites
- Docker + Docker Compose
- OpenAI API key

### Unix / macOS

```bash
git clone https://github.com/aleksander-misztal/rag-importer-retriever
cd rag-importer-retriever
cp .env.example .env          # add your OPENAI_API_KEY
docker compose up --build
```

### Windows (PowerShell)

```powershell
git clone https://github.com/aleksander-misztal/rag-importer-retriever
cd rag-importer-retriever
Copy-Item .env.example .env   # add your OPENAI_API_KEY
docker compose up --build
```

App runs at **http://localhost:8502**

## Usage

1. **Importer tab** — upload a PDF, it gets chunked and embedded into PGVector
2. **Retriever tab** — ask a question, get an answer with source chunks

## Extending

Swap any provider by implementing the relevant interface in `shared/interfaces/` and registering it in `dependency_container.py`:

| Interface | Default | Swap example |
|---|---|---|
| `VectorProvider` | PGVector | Pinecone, Weaviate |
| `LLMProvider` | OpenAI | Anthropic, Ollama |
| `EmbeddingProvider` | OpenAI | local model |
| `DocumentLoaderProvider` | PyMuPDF | Docx, HTML |
