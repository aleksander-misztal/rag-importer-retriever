import logging
from typing import Any
from concurrent.futures import ThreadPoolExecutor
from state import GraphState
from retrieval import get_vectorstore, search_documents_sync

logger = logging.getLogger(__name__)

RESULTS_PER_QUERY = 2


def executor_node(state: GraphState) -> dict[str, Any]:
    queries = state["sub_queries"]

    vectorstore = get_vectorstore()

    try:
        with ThreadPoolExecutor() as pool:
            results = list(pool.map(
                lambda q: search_documents_sync(vectorstore, q, k=RESULTS_PER_QUERY),
                queries
            ))

        flat_context = list(set(doc for sublist in results for doc in sublist))
        logger.debug(f"Pobrano {len(flat_context)} unikalnych dokumentów")
    except Exception as e:
        logger.error(f"Błąd wyszukiwania: {e}")
        flat_context = []

    return {"context": flat_context}
