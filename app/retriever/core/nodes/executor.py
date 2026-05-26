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
        """Performs multi-query retrieval, returning results grouped by sub-query"""
        queries = state.get("sub_queries", [state["question"]])

        try:
            documents_by_query = {}
            for query in queries:
                docs = self.repository.search(query, k=self.k)
                documents_by_query[query] = docs

            total = sum(len(d) for d in documents_by_query.values())
            logger.info(f"Retrieved {total} documents across {len(queries)} sub-queries")
            return {"documents_by_query": documents_by_query}

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {"documents_by_query": {}}
