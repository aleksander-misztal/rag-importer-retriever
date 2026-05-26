from typing import List, Dict, TypedDict


class GraphState(TypedDict):
    """Graph state for RAG pipeline"""
    question: str                          # Original user question
    sub_queries: List[str]                 # Query variants for search
    documents_by_query: Dict[str, list]    # Raw retrieval results grouped by sub-query
    context: List[str]                     # Retrieved document fragments (after reranking)
    context_metadata: List[dict]           # Metadata for each fragment (source, page, etc.)
    answer: str                            # Final LLM-generated answer
    is_safe: bool                          # Security check result
