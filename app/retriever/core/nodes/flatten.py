import logging
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class FlattenNode:
    """Converts documents_by_query → context when reranker is disabled.
    Preserves insertion order, deduplicates by content."""

    def __call__(self, state: GraphState) -> dict:
        documents_by_query = state.get("documents_by_query", {})

        seen = set()
        context = []
        context_metadata = []

        for docs in documents_by_query.values():
            for doc in docs:
                if doc.content not in seen:
                    seen.add(doc.content)
                    context.append(doc.content)
                    context_metadata.append(doc.metadata)

        logger.info(f"Flatten: {len(context)} unique docs")
        return {"context": context, "context_metadata": context_metadata}
