from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class Document:
    """Document abstracted from vector store implementation"""
    content: str
    metadata: dict | None = None
    score: float | None = None


class DocumentRepository(ABC):
    """Repository pattern for document retrieval.
    Abstracts vector store details (PGVector, Pinecone, etc.)
    """

    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Semantic search returning top-k documents sorted by relevance"""
        pass
