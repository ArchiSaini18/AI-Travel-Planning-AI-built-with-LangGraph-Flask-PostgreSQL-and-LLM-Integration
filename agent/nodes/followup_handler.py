from typing import Dict, Any
import logging
from agent.tools import llm_api

logger = logging.getLogger(__name__)


def handle_followup(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Handling follow-up question")
    logger.info(f"User input: {state.get('user_input', '')}")
    
    user_input = state.get("user_input", "")
    itinerary = state.get("itinerary", {})
    destination = state.get("selected_destination", {})
    preferences = state.get("preferences", {})
    conversation_history = state.get("conversation_history", [])
    
    logger.info(f"Has itinerary: {bool(itinerary)}")
    logger.info(f"Has destination: {bool(destination)}")
    logger.info(f"Conversation history length: {len(conversation_history)}")
    
    try:
        # Build context from available information
        context = "You are a helpful travel assistant who has been helping the user plan their trip."
        
        dest_name = destination.get('name', 'Unknown') if destination else 'Unknown'
        dest_country = destination.get('country', '') if destination else ''
        
        context += f"\n\nTrip Details:"
        context += f"\nDestination: {dest_name}"
        if dest_country:
            context += f", {dest_country}"
        
        if preferences:
            context += f"\nTrip duration: {preferences.get('duration', 'Not specified')} days"
            context += f"\nBudget level: {preferences.get('budget', 'Not specified')}"
            if preferences.get('interests'):
                context += f"\nTraveler interests: {', '.join(preferences.get('interests', []))}"
            if preferences.get('travel_style'):
                context += f"\nTravel style: {preferences.get('travel_style')}"
        
        if itinerary and itinerary.get('days'):
            context += f"\n\nItinerary Status:"
            context += f"\nA {len(itinerary.get('days', []))}-day itinerary for {dest_name} has been created."
            if itinerary.get('budget'):
                context += f"\nTotal budget: {itinerary['budget'].get('total', 'Not specified')} {itinerary['budget'].get('currency', 'USD')}"
        
        # Build message history, including conversation history for better context
        messages = []
        messages.append({"role": "system", "content": context})
        
        # Include recent conversation history (last 6 messages) for context
        recent_history = conversation_history[-6:] if len(conversation_history) > 0 else []
        logger.info(f"Recent history messages: {len(recent_history)}")
        for msg in recent_history:
            messages.append(msg)
        
        # Add the current user input
        messages.append({"role": "user", "content": user_input})
        
        logger.info(f"Sending {len(messages)} messages to LLM for follow-up")
        response = llm_api.generate_completion(messages, temperature=0.7, max_tokens=800)
        logger.info(f"LLM response length: {len(response) if response else 0}")
        logger.info(f"LLM response preview: {response[:100] if response else 'EMPTY'}")
        
        state["followup_response"] = response
        state["current_node"] = "followup_handler"
        
        logger.info(f"Generated follow-up response - stored in state")
        
    except Exception as e:
        logger.error(f"Error handling follow-up: {e}", exc_info=True)
        state["followup_response"] = "I apologize, but I'm having trouble answering your question. Could you please rephrase it?"
        state["error"] = f"Error in follow-up handler: {str(e)}"
    
    return state
