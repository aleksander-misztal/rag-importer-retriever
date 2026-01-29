"""Abstract interfaces for dependency injection"""

from shared.interfaces.document_loader import DocumentLoaderProvider, RawDocument
from shared.interfaces.embeddings import EmbeddingProvider
from shared.interfaces.llm import LLMProvider
from shared.interfaces.prompts import PromptProvider
from shared.interfaces.repository import DocumentRepository, Document
from shared.interfaces.vectorstore import VectorProvider, VectorStoreProvider, DocumentChunk

__all__ = [
    "DocumentLoaderProvider",
    "RawDocument",
    "EmbeddingProvider",
    "LLMProvider",
    "PromptProvider",
    "DocumentRepository",
    "Document",
    "VectorProvider",
    "VectorStoreProvider",
    "DocumentChunk",
]
