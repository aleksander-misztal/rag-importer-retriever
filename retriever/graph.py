from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from state import GraphState
from nodes.security import security_node
from nodes.generator import generator_node
from nodes.executor import executor_node
from nodes.synthesizer import synthesizer_node


def create_graph() -> CompiledStateGraph:
    workflow = StateGraph(GraphState)

    workflow.add_node("security", security_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("security")

    workflow.add_conditional_edges(
        "security",
        lambda x: "proceed" if x["is_safe"] else "end",
        {"proceed": "generator", "end": END}
    )

    workflow.add_edge("generator", "executor")
    workflow.add_edge("executor", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()
