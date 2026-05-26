---
tags: [system, architektura, kod]
---

# Architektura systemu

## Warstwy

```mermaid
flowchart TB
    subgraph UI [Warstwa UI - Streamlit]
        IMP[Importer Page\npages/importer.py]
        RET[Retriever Page\npages/retriever.py]
    end

    subgraph APP [Warstwa aplikacji - app/]
        subgraph IMPORTER [Importer]
            DP[DocumentProcessor\nchunking + embeddings]
            IS[IngestionService\norchestration]
        end
        subgraph RETRIEVER [Retriever - LangGraph]
            SEC2[SecurityNode]
            GEN[GeneratorNode]
            EXE[ExecutorNode]
            RNK[RerankNode\nopcjonalny]
            FLT[FlattenNode]
            SYN[SynthesizerNode]
        end
        DI[DependencyContainer\ndependency-injector]
    end

    subgraph SHARED [Warstwa shared/]
        CFG[Config\nPydantic Settings]
        EMB[OpenAIEmbeddingProvider]
        LLM2[OpenAILLMProvider]
        PGV[PGVectorStoreProvider]
        REPO[VectorDocumentRepository]
        PMP[PyMuPDFLoaderProvider]
        PRP[LocalPromptProvider]
    end

    subgraph INFRA [Infrastruktura]
        DB[(PostgreSQL\n+ PGVector)]
        OAI[OpenAI API]
    end

    subgraph EVAL [Ewaluacja - eval/]
        RUN[runner.py]
        COL[MetricsCollector]
        MET[metrics/]
        STB[stability/]
    end

    UI --> DI
    DI --> IMPORTER
    DI --> RETRIEVER
    APP --> SHARED
    SHARED --> INFRA
    EVAL --> APP
```

## Kluczowe decyzje projektowe

| Decyzja | Uzasadnienie |
|---|---|
| Dependency Injection (`dependency-injector`) | Łatwa podmiana komponentów per architektura |
| LangGraph dla pipeline | Wizualny graf, łatwe dodawanie węzłów |
| Repository Pattern | Odizolowanie logiki retrieval od vector store |
| Strategy Pattern (chunking) | `recursive` / `semantic` przełączane przez env var |
| Lazy import `sentence-transformers` | Działa bez torch (Python 3.13 lokalnie) |

## Konfiguracja (env vars)

| Zmienna | Domyślnie | Opis |
|---|---|---|
| `OPENAI_API_KEY` | wymagany | — |
| `RERANKING_ENABLED` | `true` | Włącza RerankNode w grafie |
| `CHUNKING_STRATEGY` | `recursive` | `recursive` lub `semantic` |
| `CHUNK_SIZE` | `250` | Rozmiar chunku w znakach |
| `CHUNK_OVERLAP` | `50` | Nakładanie się chunków |
| `COLLECTION_NAME` | `study_docs` | Kolekcja PGVector |
| `JUDGE_MODEL` | `gpt-4o` | Model do ewaluacji |
| `DB_HOST` | `db` | Host PostgreSQL |

---

Powiązane: [[pipeline]] | [[01-baseline-rag]]
