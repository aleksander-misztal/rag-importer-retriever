from typing import List, Dict, Any, TypedDict


class GraphState(TypedDict):
    question: str
    sub_queries: List[str]
    context: List[str]
    answer: str
    is_safe: bool
    models: Dict[str, Any]
