from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Strategy Pattern - swappable embedding providers"""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts"""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed single query"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Returns embedding dimension (e.g., 1536 for text-embedding-3-small)"""
        pass
