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
        """Retrieves documents for the question"""
        question = state["question"]

        try:
            docs = self.repository.search(question, k=self.k)
            logger.info(f"Retrieved {len(docs)} documents")
            return {"documents_by_query": {question: docs}}

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {"documents_by_query": {}}
