import logging
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class RerankNode:
    """Reranks retrieved documents per sub-query, then deduplicates across sub-queries"""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_k_per_query: int = 2,
    ):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name)
        self.top_k_per_query = top_k_per_query
        logger.info(f"RerankNode init: model={model_name}, top_k_per_query={top_k_per_query}")

    def __call__(self, state: GraphState) -> dict:
        documents_by_query = state.get("documents_by_query", {})

        if not documents_by_query:
            logger.warning("No documents to rerank")
            return {"context": [], "context_metadata": []}

        seen_contents = set()
        final_context = []
        final_metadata = []

        for sub_query, docs in documents_by_query.items():
            if not docs:
                continue

            pairs = [(sub_query, doc.content) for doc in docs]
            scores = self.model.predict(pairs)

            ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

            added = 0
            for doc, score in ranked:
                if added >= self.top_k_per_query:
                    break
                if doc.content not in seen_contents:
                    seen_contents.add(doc.content)
                    final_context.append(doc.content)
                    final_metadata.append(doc.metadata)
                    added += 1

            logger.debug(f"Sub-query '{sub_query[:50]}': kept {added} docs after reranking")

        logger.info(f"Reranking done: {len(final_context)} unique docs across {len(documents_by_query)} sub-queries")
        return {"context": final_context, "context_metadata": final_metadata}
