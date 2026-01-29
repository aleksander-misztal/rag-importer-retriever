from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class Document:
    """Document representation abstracted from vector store implementation."""
    content: str
    metadata: dict | None = None
    score: float | None = None


class DocumentRepository(ABC):
    """
    Repository pattern for document operations.
    Abstracts vector store details (PGVector, Pinecone, etc.) and handles
    semantic search, deduplication, and scoring logic.
    """

    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Semantic search returning top-k documents sorted by relevance."""
        pass

    @abstractmethod
    def search_batch(self, queries: List[str], k: int = 3) -> List[Document]:
        """Multi-query search with deduplication across results."""
        pass
