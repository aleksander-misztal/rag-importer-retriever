from abc import ABC, abstractmethod
from typing import List, Union
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Document chunk ready for vector store"""
    content: str
    metadata: dict | None = None
    embedding: List[float] | None = None


class VectorProvider(ABC):
    """Unified interface for vector stores (PGVector, Pinecone, etc.)"""

    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[str]:
        """Semantic document search"""
        pass

    @abstractmethod
    def add_documents(self, documents: Union[List[DocumentChunk], List]) -> int:
        """Add documents to vector store"""
        pass

    @abstractmethod
    def get_collection_stats(self) -> dict:
        """Returns collection statistics"""
        pass

    @abstractmethod
    def clear_collection(self) -> bool:
        """Clears all documents from collection"""
        pass

    @abstractmethod
    def get_document_registry(self) -> dict:
        """Returns registry of uploaded documents"""
        pass


# Alias for backward compatibility
VectorStoreProvider = VectorProvider
