from langgraph.graph import StateGraph, END
from retriever.core.state import GraphState


def create_graph(security, generator, executor, synthesizer, reranker=None, flatten=None):
    """Builds LangGraph workflow from injected node instances.

    If reranker is provided: executor → reranker → synthesizer
    Otherwise:               executor → flatten  → synthesizer
    """

    workflow = StateGraph(GraphState)

    workflow.add_node("security_node", security)
    workflow.add_node("generator_node", generator)
    workflow.add_node("executor_node", executor)
    workflow.add_node("synthesizer_node", synthesizer)



    workflow.set_entry_point("security_node")

    workflow.add_conditional_edges(
        "security_node",
        lambda state: "continue" if state.get("is_safe") else "end",
        {"continue": "generator_node", "end": END}
    )

    workflow.add_edge("generator_node", "executor_node")

    if reranker is not None:
        workflow.add_node("reranker_node", reranker)
        workflow.add_edge("executor_node", "reranker_node")
        workflow.add_edge("reranker_node", "synthesizer_node")
    else:
        workflow.add_node("flatten_node", flatten)
        workflow.add_edge("executor_node", "flatten_node")
        workflow.add_edge("flatten_node", "synthesizer_node")

    workflow.add_edge("synthesizer_node", END)

    return workflow.compile()
