from langgraph.graph import StateGraph, END
from retriever.core.state import GraphState


def create_graph(executor, flatten, synthesizer):
    """Baseline RAG: executor → flatten → synthesizer"""

    workflow = StateGraph(GraphState)

    workflow.add_node("executor_node", executor)
    workflow.add_node("flatten_node", flatten)
    workflow.add_node("synthesizer_node", synthesizer)

    workflow.set_entry_point("executor_node")
    workflow.add_edge("executor_node", "flatten_node")
    workflow.add_edge("flatten_node", "synthesizer_node")
    workflow.add_edge("synthesizer_node", END)

    return workflow.compile()
