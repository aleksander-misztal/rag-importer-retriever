# Professional RAG System

A production-grade Retrieval-Augmented Generation (RAG) system built with LangChain, LangGraph, and PostgreSQL with PGVector. Implements enterprise design patterns including Dependency Injection, Repository Pattern, and clean architecture principles.

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Application                       │
│                  (Single Docker Container)                   │
│                                                               │
│  ┌─────────────────────┬──────────────────────────────────┐ │
│  │  Importer Module    │     Retriever Module              │ │
│  │  /importer endpoint │     /retriever endpoint           │ │
│  │                     │                                   │ │
│  │  • PDF Upload       │     • Chat Interface             │ │
│  │  • Chunking         │     • LangGraph Pipeline         │ │
│  │  • Vector Storage   │     • Multi-Query Search         │ │
│  │  • Doc Registry     │     • Source Attribution         │ │
│  └─────────────────────┴──────────────────────────────────┘ │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Shared Library                            │  │
│  │  • Interfaces (ABC)    • Providers (Implementations)  │  │
│  │  • DI Container        • Config & Logger              │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │  PostgreSQL    │
                    │  + PGVector    │
                    │  (Vector DB)   │
                    └────────────────┘
```

### Directory Structure

```
rag-importer-retriever/
├── app/                          # Unified application
│   ├── main.py                   # FastAPI app with both endpoints
│   ├── dependency_container.py   # Unified DI container
│   ├── requirements.txt          # Python dependencies
│   ├── importer/                 # Importer module
│   │   ├── ui.py                 # Gradio interface
│   │   └── services/             # Business logic
│   │       ├── document_processor.py  # Chunking & metadata
│   │       └── ingestion_service.py   # Import orchestration
│   └── retriever/                # Retriever module
│       ├── ui.py                 # Gradio chat interface
│       └── core/                 # RAG pipeline
│           ├── state.py          # LangGraph state
│           ├── graph.py          # Workflow definition
│           └── nodes/            # Processing nodes
│               ├── security.py   # Input validation
│               ├── generator.py  # Query generation
│               ├── executor.py   # Document retrieval
│               └── synthesizer.py # Answer synthesis
├── shared/                       # Shared library (zero duplication)
│   ├── interfaces/               # Abstract interfaces
│   │   ├── document_loader.py   # ABC for document loaders
│   │   ├── vectorstore.py       # ABC for vector stores
│   │   ├── embeddings.py        # ABC for embeddings
│   │   ├── llm.py               # ABC for LLM providers
│   │   ├── prompts.py           # ABC for prompts
│   │   └── repository.py        # ABC for repositories
│   ├── providers/                # Concrete implementations
│   │   ├── pymupdf_loader.py    # PDF loading
│   │   ├── pgvector_store.py    # Vector storage
│   │   ├── openai_embeddings.py # Embeddings
│   │   ├── openai_llm.py        # LLM calls
│   │   ├── local_prompts.py     # Prompt templates
│   │   └── document_repository.py # Repository pattern
│   └── common/                   # Utilities
│       ├── config.py             # Pydantic settings
│       └── logger.py             # Centralized logging
├── Dockerfile                    # Single container build
├── docker-compose.yml            # Orchestration (app + db)
├── .env                          # Environment variables
└── README.md                     # This file
```

## Core Design Patterns

### 1. Dependency Injection (DI)
All dependencies injected via `DependencyContainer`:
```python
class DependencyContainer(containers.DeclarativeContainer):
    # Infrastructure layer
    vector_store = providers.Singleton(
        PGVectorStoreProvider,
        connection_url=CONFIG.DATABASE_URL,
        embedding_provider=embedding_provider
    )

    # Service layer
    ingestion_service = providers.Singleton(
        IngestionService,
        vector_store=vector_store
    )
```

Benefits:
- ✅ Testability (easy mocking)
- ✅ Flexibility (swap implementations)
- ✅ Single Responsibility Principle

### 2. Repository Pattern
Abstract data access through `DocumentRepository`:
```python
class VectorDocumentRepository(DocumentRepository):
    def search_batch(self, queries: List[str]) -> List[Document]:
        # Deduplication, ranking, caching
```

Benefits:
- ✅ Decouples business logic from data source
- ✅ Enables deduplication and ranking
- ✅ Supports multiple vector store backends

### 3. Strategy Pattern
Swappable implementations via interfaces:
- `VectorProvider`: PGVector, Pinecone, Weaviate
- `LLMProvider`: OpenAI, Anthropic, local models
- `EmbeddingProvider`: OpenAI, Hugging Face

### 4. Facade Pattern
`IngestionService` simplifies complex workflow:
```python
result = ingestion_service.ingest_file(file_path)
# Internally: load → chunk → embed → store
```

## Key Components

### Importer Module

**Responsibilities:**
- PDF upload and validation (max 50MB)
- Document chunking (RecursiveCharacterTextSplitter)
- Metadata enrichment (source file, page number)
- Vector embedding and storage
- Document registry management

**UI Features:**
- Upload: Drag-and-drop PDF interface
- Statistics: View uploaded documents with chunk counts
- Admin: Clear database button

**Processing Pipeline:**
```
PDF Upload → Load Pages → Chunk Text → Embed → Store
           ↓            ↓             ↓       ↓
       PyMuPDF   DocumentProcessor  OpenAI  PGVector
```

### Retriever Module

**Responsibilities:**
- Question answering with RAG
- Multi-query retrieval (improves recall)
- Security filtering (malicious input validation)
- Source attribution (file + page number)

**UI Features:**
- Chat: Natural language Q&A interface
- Sources: Shows filename and page for each retrieved chunk

**RAG Pipeline (LangGraph):**
```
Question → Security Check → Query Generation → Retrieval → Answer Synthesis
           ↓                ↓                   ↓            ↓
       GPT-4o-mini      GPT-4o-mini        PGVector      GPT-4o
```

#### LangGraph Workflow

```python
def create_graph(security, generator, executor, synthesizer):
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("security_node", security)
    workflow.add_node("generator_node", generator)
    workflow.add_node("executor_node", executor)
    workflow.add_node("synthesizer_node", synthesizer)

    # Entry point
    workflow.set_entry_point("security_node")

    # Conditional routing
    workflow.add_conditional_edges(
        "security_node",
        lambda state: "continue" if state.get("is_safe") else "end",
        {"continue": "generator_node", "end": END}
    )

    # Sequential flow
    workflow.add_edge("generator_node", "executor_node")
    workflow.add_edge("executor_node", "synthesizer_node")
    workflow.add_edge("synthesizer_node", END)

    return workflow.compile()
```

## Features

### Importer Features
- ✅ **PDF Upload**: Drag-and-drop or file picker
- ✅ **Document Registry**: Track all uploaded files with chunk counts
  Example: `• aircraft.pdf: 45 chunks`
- ✅ **Statistics**: View collection info and uploaded documents
- ✅ **Database Management**: Clear all documents button
- ✅ **Metadata Tracking**: Source file and page number for each chunk
- ✅ **Size Validation**: Max 50MB per file
- ✅ **Format Validation**: PDF only

### Retriever Features
- ✅ **Chat Interface**: Natural language Q&A
- ✅ **Source Attribution**: Shows filename and page for each chunk
  Example: `Fragment 1 (📄 aircraft.pdf, page 42):`
- ✅ **Multi-Query Retrieval**: Generates query variants for better recall
- ✅ **Security Filtering**: Validates questions before processing
- ✅ **Context Display**: Shows retrieved documents alongside answer
- ✅ **Langfuse Integration**: Optional tracing (if credentials provided)
- ✅ **Deduplication**: Automatic removal of duplicate chunks

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Quick Start

1. **Clone repository**
```bash
git clone <repository-url>
cd rag-importer-retriever
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start services**
```bash
docker-compose up --build
```

4. **Access application**
- Importer: http://localhost:7860/importer
- Retriever: http://localhost:7860/retriever

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Database (defaults provided)
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432

# Vector Collection
COLLECTION_NAME=study_docs

# Chunking Parameters
CHUNK_SIZE=250
CHUNK_OVERLAP=50

# Optional: Langfuse Tracing
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | ASGI web server |
| **UI** | Gradio 6.5 | Interactive interfaces |
| **LLM** | OpenAI GPT-4o / GPT-4o-mini | Generation & query expansion |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search |
| **Vector DB** | PostgreSQL + PGVector | Document storage |
| **Orchestration** | LangGraph | RAG workflow |
| **DI** | dependency-injector | Inversion of control |
| **Config** | Pydantic Settings | Type-safe configuration |
| **PDF Processing** | PyMuPDF | Document loading |
| **Chunking** | LangChain Text Splitters | Text segmentation |

## Key Mechanisms

### 1. Document Ingestion

```python
# Pipeline: Load → Chunk → Embed → Store
def ingest_file(file_path: str):
    # 1. Load PDF pages
    raw_docs = document_loader.load(file_path)

    # 2. Chunk with metadata preservation
    chunks = document_processor.process(raw_docs)
    # Each chunk has: content, source, page, chunk_id

    # 3. Embed and store (embeddings generated by PGVector)
    vector_store.add_documents(chunks)
```

### 2. Multi-Query Retrieval

```python
# Improves recall by generating query variants
def search_batch(queries: List[str]):
    all_docs = []
    for query in queries:
        docs = vector_store.search(query, k=3)
        all_docs.extend(docs)

    # Deduplicate by content
    unique_docs = deduplicate(all_docs)
    return unique_docs
```

### 3. Source Attribution

Documents retain metadata through the pipeline:
```python
{
    "content": "F-22 is a stealth fighter...",
    "metadata": {
        "source": "/data/aircraft.pdf",
        "page": 42,
        "chunk_id": 15
    }
}
```

UI displays: `Fragment 1 (📄 aircraft.pdf, page 42):`

### 4. Document Registry

Track all uploaded files with SQL query:
```sql
SELECT
    cmetadata->>'source' as source,
    COUNT(*) as chunks
FROM langchain_pg_embedding
WHERE cmetadata->>'source' IS NOT NULL
GROUP BY cmetadata->>'source'
```

Result:
```
📁 Uploaded Documents:
• document1.pdf: 32 chunks
• document2.pdf: 18 chunks
📦 Total: 2 files, 50 chunks
```

## Development

### Adding a New Vector Store

1. Implement `VectorProvider` interface:
```python
class PineconeProvider(VectorProvider):
    def search(self, query: str, k: int) -> List[str]: ...
    def add_documents(self, docs: List[DocumentChunk]) -> int: ...
    def get_document_registry(self) -> dict: ...
```

2. Register in DI container:
```python
vector_store = providers.Singleton(
    PineconeProvider,
    api_key=CONFIG.PINECONE_API_KEY
)
```

### Adding a New LLM Provider

1. Implement `LLMProvider`:
```python
class AnthropicLLMProvider(LLMProvider):
    def invoke(self, prompt: str, **kwargs) -> str: ...
```

2. Swap in container:
```python
llm_service = providers.Singleton(AnthropicLLMProvider)
```

### Running Tests

```bash
# Unit tests (mocked dependencies)
pytest tests/unit

# Integration tests (requires services)
docker-compose up -d
pytest tests/integration
```

## Performance Considerations

- **Chunking**: 250 chars with 50 overlap balances context vs. precision
- **Embedding**: Batch processing for efficiency (handled by PGVector)
- **Retrieval**: k=3 per query, deduplicated to ~6 unique chunks
- **LLM**: GPT-4o-mini for speed (security, query gen), GPT-4o for quality (synthesis)
- **Connection Pool**: Reuses database connections via SQLAlchemy

## Security

- ✅ Input validation on all endpoints
- ✅ Security node filters malicious questions before processing
- ✅ SQL injection prevention (parameterized queries with SQLAlchemy)
- ✅ File size limits (50MB max)
- ✅ File type validation (PDF only)
- ✅ Environment-based secrets management (.env)

## Monitoring & Observability

### Logging
Centralized structured logging at key points:
```python
logger.info(f"Processing {len(chunks)} chunks")
logger.error(f"Import error: {e}")
```

### Langfuse Tracing (Optional)
- Tracks all LLM calls with inputs/outputs
- Monitors latency and token usage
- Enables debugging and cost analysis
- Enable by setting Langfuse credentials in `.env`

## Troubleshooting

### Importer not showing documents
```bash
# Check database connection
docker-compose logs db

# Verify embeddings generation
docker-compose logs app | grep "Adding"
```

### Retriever returns empty results
```bash
# Check vector store has data
docker exec -it rag_db psql -U postgres -d postgres \
  -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
```

### Statistics not showing uploaded files
```bash
# Check logs for registry errors
docker logs rag_app 2>&1 | grep "Registry"

# Query database directly
docker exec -it rag_db psql -U postgres -d postgres \
  -c "SELECT cmetadata->>'source', COUNT(*) FROM langchain_pg_embedding GROUP BY cmetadata->>'source';"
```

### Out of memory
```bash
# Reduce chunk size in .env
CHUNK_SIZE=150
CHUNK_OVERLAP=25
```

## Production Deployment

### Recommendations

1. **Use managed vector DB**: Pinecone, Weaviate Cloud
2. **Enable authentication**: Add API keys to FastAPI endpoints
3. **Set up monitoring**: Prometheus + Grafana
4. **Configure autoscaling**: Based on request volume
5. **Use CDN**: For static Gradio assets
6. **Enable HTTPS**: Use reverse proxy (nginx/Traefik)
7. **Rate limiting**: Prevent abuse
8. **Backup strategy**: Regular database backups

### Example Production docker-compose.yml

```yaml
services:
  app:
    image: your-registry/rag-app:latest
    environment:
      - LOG_LEVEL=warning
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Follow existing patterns:
   - Use Dependency Injection
   - Implement interfaces for new providers
   - Add type hints
   - Write docstrings
4. Add tests for new functionality
5. Update README if adding features
6. Submit pull request

## License

MIT License

## Acknowledgments

- **LangChain** for RAG primitives and vector store integrations
- **LangGraph** for workflow orchestration and state management
- **PGVector** for efficient vector storage in PostgreSQL
- **OpenAI** for embeddings and language models
- **Gradio** for rapid UI prototyping
- **dependency-injector** for clean DI pattern implementation

## FAQ

**Q: Can I use a different vector database?**
A: Yes, implement the `VectorProvider` interface and swap it in the DI container.

**Q: How do I change the LLM provider?**
A: Implement `LLMProvider` interface (e.g., for Anthropic, Ollama) and configure in DI container.

**Q: What file formats are supported?**
A: Currently PDF only. To add support, implement `DocumentLoaderProvider` for your format.

**Q: How do I clear the database?**
A: Use the Admin tab in the Importer UI, or run:
```bash
docker exec -it rag_db psql -U postgres -d postgres -c "TRUNCATE langchain_pg_embedding;"
```

**Q: Can I run this without Docker?**
A: Yes, but you'll need to set up PostgreSQL with PGVector extension manually and adjust the connection string in `.env`.

## Roadmap

- [ ] Support for additional file formats (Word, TXT, HTML)
- [ ] Hybrid search (keyword + semantic)
- [ ] Chat history persistence
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] API endpoints for programmatic access
- [ ] Fine-tuning embedding models
- [ ] Support for private LLMs (Ollama, vLLM)

---

**Built with ❤️ for enterprise-grade RAG applications**
