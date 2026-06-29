from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    extract_preferences,
    find_destinations,
    create_itinerary,
    handle_followup
)
import logging

logger = logging.getLogger(__name__)


def route_entry(state: AgentState) -> str:
    is_followup = state.get("is_followup", False)
    if is_followup:
        return "handle_followup"
    return "extract_preferences"


def build_travel_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("extract_preferences", extract_preferences)
    workflow.add_node("find_destinations", find_destinations)
    workflow.add_node("create_itinerary", create_itinerary)
    workflow.add_node("handle_followup", handle_followup)
    
    workflow.add_conditional_edges(
        "__start__",
        route_entry,
        {
            "extract_preferences": "extract_preferences",
            "handle_followup": "handle_followup"
        }
    )
    
    workflow.add_edge("extract_preferences", "find_destinations")
    workflow.add_edge("find_destinations", "create_itinerary")
    workflow.add_edge("create_itinerary", END)
    workflow.add_edge("handle_followup", END)
    
    logger.info("Travel agent workflow built successfully")
    
    return workflow.compile()
