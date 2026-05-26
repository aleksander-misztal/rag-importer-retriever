from langgraph.graph import StateGraph, END
from retriever.core.state import GraphState


def create_graph(security, executor, flatten, synthesizer):
    """Baseline RAG: security → executor → flatten → synthesizer"""

    workflow = StateGraph(GraphState)

    workflow.add_node("security_node", security)
    workflow.add_node("executor_node", executor)
    workflow.add_node("flatten_node", flatten)
    workflow.add_node("synthesizer_node", synthesizer)

    workflow.set_entry_point("security_node")

    workflow.add_conditional_edges(
        "security_node",
        lambda state: "continue" if state.get("is_safe") else "end",
        {"continue": "executor_node", "end": END}
    )

    workflow.add_edge("executor_node", "flatten_node")
    workflow.add_edge("flatten_node", "synthesizer_node")
    workflow.add_edge("synthesizer_node", END)

    return workflow.compile()
