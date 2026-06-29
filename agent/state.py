from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime


class AgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    user_input: str
    preferences: Dict[str, Any]
    destinations: List[Dict[str, Any]]
    selected_destination: Optional[Dict[str, Any]]
    itinerary: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    current_node: str
    is_followup: bool
    weather_data: Optional[Dict[str, Any]]
    currency_rates: Optional[Dict[str, Any]]
    user_currency: str
    session_id: str
    timestamp: str
    comparison_destinations: List[Dict[str, Any]]
    budget_breakdown: Optional[Dict[str, Any]]
    error: Optional[str]
    followup_response: Optional[str]
    requested_destination: Optional[str]


def create_initial_state() -> AgentState:
    return AgentState(
        messages=[],
        user_input="",
        preferences={},
        destinations=[],
        selected_destination=None,
        itinerary={},
        conversation_history=[],
        current_node="",
        is_followup=False,
        weather_data=None,
        currency_rates=None,
        user_currency="USD",
        session_id="",
        timestamp=datetime.now().isoformat(),
        comparison_destinations=[],
        budget_breakdown=None,
        error=None,
        followup_response=None,
        requested_destination=None
    )


def update_conversation_history(state: AgentState, role: str, content: str) -> AgentState:
    if "conversation_history" not in state:
        state["conversation_history"] = []
    
    state["conversation_history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    return state
