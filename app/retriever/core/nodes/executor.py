import logging
from shared.interfaces.repository import DocumentRepository
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class ExecutorNode:
    """Executes multi-query retrieval using repository pattern"""

    def __init__(self, document_repository: DocumentRepository, k: int = 2):
        self.repository = document_repository
        self.k = k

    def __call__(self, state: GraphState) -> dict:
        """Performs multi-query retrieval with automatic deduplication"""
        queries = state.get("sub_queries", [state["question"]])

        try:
            documents = self.repository.search_batch(queries, k=self.k)
            context = [doc.content for doc in documents]
            context_metadata = [doc.metadata for doc in documents]
            logger.info(f"Retrieved {len(context)} unique documents")
            return {
                "context": context,
                "context_metadata": context_metadata
            }

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {
                "context": [],
                "context_metadata": []
            }
