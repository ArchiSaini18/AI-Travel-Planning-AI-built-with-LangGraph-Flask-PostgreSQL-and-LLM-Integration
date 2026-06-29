from typing import Dict, Any
import logging
from agent.tools import llm_api

logger = logging.getLogger(__name__)


def extract_preferences(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Extracting user preferences")
    
    user_input = state.get("user_input", "")
    
    if not user_input:
        state["preferences"] = {
            "budget": "medium",
            "duration": 7,
            "interests": ["culture", "food"],
            "travel_style": "relaxation",
            "companions": "solo",
            "destination_name": None
        }
        state["current_node"] = "preference_extractor"
        return state
    
    try:
        preferences = llm_api.extract_preferences(user_input)
        
        if not preferences.get("duration"):
            preferences["duration"] = 7
        if not preferences.get("budget"):
            preferences["budget"] = "medium"
        if not preferences.get("interests"):
            preferences["interests"] = ["culture", "food", "nature"]
        if "destination_name" not in preferences:
            preferences["destination_name"] = None
        
        # Store destination name in state for use in destination_finder
        if preferences.get("destination_name"):
            state["requested_destination"] = preferences["destination_name"]
            logger.info(f"User requested destination: {preferences['destination_name']}")
        
        state["preferences"] = preferences
        state["current_node"] = "preference_extractor"
        
        logger.info(f"Extracted preferences: {preferences}")
        
    except Exception as e:
        logger.error(f"Error extracting preferences: {e}")
        state["preferences"] = {
            "budget": "medium",
            "duration": 7,
            "interests": ["culture"],
            "travel_style": "relaxation",
            "destination_name": None
        }
        state["error"] = f"Error extracting preferences: {str(e)}"
    
    return state
