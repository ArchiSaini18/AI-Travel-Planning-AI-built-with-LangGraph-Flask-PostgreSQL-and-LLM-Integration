from typing import Dict, Any, List
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def find_destinations(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Finding suitable destinations")
    
    preferences = state.get("preferences", {})
    budget = preferences.get("budget", "medium")
    interests = preferences.get("interests", [])
    season = preferences.get("season")
    duration = preferences.get("duration", 7)
    requested_destination = state.get("requested_destination")
    
    try:
        destinations_file = Path(__file__).parent.parent.parent / "data" / "destinations.json"
        with open(destinations_file, 'r') as f:
            all_destinations = json.load(f)
        
        # Check if user requested a specific destination
        if requested_destination:
            for dest in all_destinations:
                if dest["name"].lower() == requested_destination.lower():
                    logger.info(f"Found requested destination: {dest['name']}")
                    state["selected_destination"] = dest
                    state["destinations"] = [dest]
                    state["comparison_destinations"] = [dest]
                    state["current_node"] = "destination_finder"
                    return state
            logger.warning(f"Requested destination '{requested_destination}' not found in database")
        
        scored_destinations = []
        for dest in all_destinations:
            score = 0
            
            if dest["budget_level"] == budget:
                score += 3
            elif budget == "high" and dest["budget_level"] == "medium":
                score += 2
            elif budget == "medium" and dest["budget_level"] in ["low", "high"]:
                score += 1
            
            matching_interests = set(interests) & set(dest["tags"])
            score += len(matching_interests) * 2
            
            if season and season in dest["best_seasons"]:
                score += 2
            
            min_duration, max_duration = dest["ideal_duration"]
            if min_duration <= duration <= max_duration:
                score += 2
            elif duration < min_duration:
                score += 1
            
            if score > 0:
                scored_destinations.append({
                    "destination": dest,
                    "score": score,
                    "match_percentage": min(100, (score / 10) * 100)
                })
        
        scored_destinations.sort(key=lambda x: x["score"], reverse=True)
        
        top_destinations = scored_destinations[:5]
        
        state["destinations"] = [item["destination"] for item in top_destinations]
        state["comparison_destinations"] = [item["destination"] for item in top_destinations[:3]]
        
        if top_destinations:
            state["selected_destination"] = top_destinations[0]["destination"]
        
        state["current_node"] = "destination_finder"
        
        logger.info(f"Found {len(top_destinations)} matching destinations")
        
    except Exception as e:
        logger.error(f"Error finding destinations: {e}")
        state["destinations"] = []
        state["error"] = f"Error finding destinations: {str(e)}"
    
    return state
