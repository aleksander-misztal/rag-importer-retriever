"""Shared library for RAG system - interfaces, providers, and utilities"""

from shared.common import CONFIG, setup_logger
from shared.interfaces import (
    DocumentLoaderProvider,
    EmbeddingProvider,
    LLMProvider,
    PromptProvider,
    DocumentRepository,
    VectorProvider,
)
from shared.providers import (
    VectorDocumentRepository,
    LocalPromptProvider,
    OpenAIEmbeddingProvider,
    OpenAILLMProvider,
    PGVectorStoreProvider,
    PyMuPDFLoaderProvider,
)

__all__ = [
    "CONFIG",
    "setup_logger",
    "DocumentLoaderProvider",
    "EmbeddingProvider",
    "LLMProvider",
    "PromptProvider",
    "DocumentRepository",
    "VectorProvider",
    "VectorDocumentRepository",
    "LocalPromptProvider",
    "OpenAIEmbeddingProvider",
    "OpenAILLMProvider",
    "PGVectorStoreProvider",
    "PyMuPDFLoaderProvider",
]
