from langgraph.graph import StateGraph, END
from retriever.core.state import GraphState


def create_graph(security, generator, executor, synthesizer):
    """Builds LangGraph workflow from injected node instances"""

    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("security_node", security)
    workflow.add_node("generator_node", generator)
    workflow.add_node("executor_node", executor)
    workflow.add_node("synthesizer_node", synthesizer)

    # Set entry point
    workflow.set_entry_point("security_node")

    # Conditional routing after security check
    workflow.add_conditional_edges(
        "security_node",
        lambda state: "continue" if state.get("is_safe") else "end",
        {
            "continue": "generator_node",
            "end": END
        }
    )

    # Sequential flow
    workflow.add_edge("generator_node", "executor_node")
    workflow.add_edge("executor_node", "synthesizer_node")
    workflow.add_edge("synthesizer_node", END)

    return workflow.compile()
