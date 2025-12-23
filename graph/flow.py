from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.planner import planner_agent
from agents.architect import architect_agent
from agents.coder import coder_agent
from agents.validator import validator_agent

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_agent)
    workflow.add_node("architect", architect_agent)
    workflow.add_node("coder", coder_agent)
    workflow.add_node("validator", validator_agent)

    # Define edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "architect")
    workflow.add_edge("architect", "coder")
    workflow.add_edge("coder", "validator")
    workflow.add_edge("validator", END)

    return workflow.compile()
