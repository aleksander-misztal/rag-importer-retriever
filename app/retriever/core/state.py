from typing import List, Dict, TypedDict


class GraphState(TypedDict):
    """Graph state for baseline RAG pipeline"""
    question: str                        # Original user question
    documents_by_query: Dict[str, list]  # Retrieval results grouped by query
    context: List[str]                   # Retrieved document fragments
    context_metadata: List[dict]         # Metadata for each fragment
    answer: str                          # Final LLM-generated answer
