import logging
from typing import List
from shared.interfaces.repository import DocumentRepository, Document
from shared.interfaces.vectorstore import VectorProvider

logger = logging.getLogger(__name__)


class VectorDocumentRepository(DocumentRepository):
    """Repository pattern implementation over vector store with deduplication"""

    def __init__(self, vector_provider: VectorProvider):
        self.vector_provider = vector_provider

    def search(self, query: str, k: int = 3) -> List[Document]:
        """Semantic document search"""
        try:
            results = self.vector_provider.search_with_metadata(query, k=k)

            documents = [
                Document(content=result["content"], metadata=result["metadata"])
                for result in results
            ]

            logger.debug(f"Found {len(documents)} documents for query: '{query[:50]}...'")
            return documents

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def search_batch(self, queries: List[str], k: int = 3) -> List[Document]:
        """Multi-query retrieval with deduplication"""
        try:
            all_documents = []

            for query in queries:
                docs = self.search(query, k=k)
                all_documents.extend(docs)

            # Deduplicate by content
            seen_contents = set()
            unique_documents = []

            for doc in all_documents:
                if doc.content not in seen_contents:
                    seen_contents.add(doc.content)
                    unique_documents.append(doc)

            logger.info(
                f"Multi-query: {len(queries)} queries, "
                f"{len(all_documents)} results, "
                f"{len(unique_documents)} unique"
            )

            return unique_documents

        except Exception as e:
            logger.error(f"Batch search error: {e}")
            return []
