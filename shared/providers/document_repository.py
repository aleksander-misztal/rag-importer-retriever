import logging
from typing import List
from shared.interfaces.repository import DocumentRepository, Document
from shared.interfaces.vectorstore import VectorProvider

logger = logging.getLogger(__name__)


class VectorDocumentRepository(DocumentRepository):
    """Repository implementation over VectorProvider"""

    def __init__(self, vector_provider: VectorProvider):
        self.vector_provider = vector_provider

    def search(self, query: str, k: int = 3) -> List[Document]:
        results = self.vector_provider.search_with_metadata(query, k=k)
        documents = [Document(content=r["content"], metadata=r["metadata"]) for r in results]
        logger.debug(f"Found {len(documents)} documents for: '{query[:60]}'")
        return documents
