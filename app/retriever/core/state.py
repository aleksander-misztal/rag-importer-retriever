from typing import List, TypedDict


class GraphState(TypedDict):
    """Graph state for RAG pipeline"""
    question: str            # Original user question
    sub_queries: List[str]   # Query variants for search
    context: List[str]       # Retrieved document fragments
    context_metadata: List[dict]  # Metadata for each fragment (source, page, etc.)
    answer: str              # Final LLM-generated answer
    is_safe: bool            # Security check result
