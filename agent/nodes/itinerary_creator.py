from typing import Dict, Any, List
import logging
from agent.tools import weather_api, currency_api, llm_api
import random

logger = logging.getLogger(__name__)


def create_itinerary(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Creating itinerary")
    
    destination = state.get("selected_destination")
    preferences = state.get("preferences", {})
    
    if not destination:
        state["error"] = "No destination selected"
        return state
    
    try:
        duration = preferences.get("duration", 5)
        interests = preferences.get("interests", ["culture", "food"])
        budget_level = preferences.get("budget", "medium")
        
        weather_data = weather_api.get_weather(
            destination["latitude"],
            destination["longitude"],
            days=min(duration, 7)
        )
        state["weather_data"] = weather_data
        
        user_currency = state.get("user_currency", "USD")
        daily_budget = destination["daily_budget_usd"]
        
        if user_currency != "USD":
            daily_budget = currency_api.convert_currency(
                daily_budget,
                "USD",
                user_currency
            )
        
        itinerary_days = []
        attractions = destination.get("attractions", [])
        
        for day in range(1, duration + 1):
            day_activities = _generate_day_activities(
                day, destination, interests, budget_level, attractions
            )
            itinerary_days.append(day_activities)
        
        total_cost = daily_budget * duration
        accommodation_cost = total_cost * 0.4
        food_cost = total_cost * 0.3
        activities_cost = total_cost * 0.2
        transport_cost = total_cost * 0.1
        
        budget_breakdown = {
            "total": round(total_cost, 2),
            "daily_average": round(daily_budget, 2),
            "accommodation": round(accommodation_cost, 2),
            "food": round(food_cost, 2),
            "activities": round(activities_cost, 2),
            "transport": round(transport_cost, 2),
            "currency": user_currency,
            "currency_symbol": currency_api.get_currency_symbol(user_currency)
        }
        
        state["budget_breakdown"] = budget_breakdown
        
        intro = llm_api.generate_itinerary_description(destination, preferences)
        
        itinerary = {
            "destination": destination,
            "duration": duration,
            "days": itinerary_days,
            "budget": budget_breakdown,
            "weather": weather_data,
            "introduction": intro,
            "best_time_to_visit": destination.get("best_seasons", []),
            "tags": destination.get("tags", [])
        }
        
        state["itinerary"] = itinerary
        state["current_node"] = "itinerary_creator"
        
        logger.info(f"Created {duration}-day itinerary for {destination['name']}")
        
    except Exception as e:
        logger.error(f"Error creating itinerary: {e}")
        state["error"] = f"Error creating itinerary: {str(e)}"
    
    return state


def _generate_day_activities(day: int, destination: Dict, interests: List[str], 
                              budget_level: str, attractions: List[str]) -> Dict[str, Any]:
    morning_activities = [
        "Breakfast at local café",
        "Morning market visit",
        "Sunrise viewing",
        "Morning yoga session",
        "Early museum visit",
        "Walking tour of historic district"
    ]
    
    afternoon_activities = [
        "Lunch at traditional restaurant",
        "Cultural workshop",
        "Local cooking class",
        "Shopping at artisan markets",
        "Visit historic landmarks",
        "Explore neighborhoods"
    ]
    
    evening_activities = [
        "Sunset viewing",
        "Dinner at rooftop restaurant",
        "Live music performance",
        "Evening stroll",
        "Local food tour",
        "Traditional cultural show"
    ]
    
    attraction = attractions[min(day - 1, len(attractions) - 1)] if attractions else "Local attractions"
    
    return {
        "day": day,
        "title": f"Day {day}: Exploring {destination['name']}",
        "morning": {
            "activity": random.choice(morning_activities),
            "location": attraction,
            "duration": "3 hours"
        },
        "afternoon": {
            "activity": random.choice(afternoon_activities),
            "location": attraction if day % 2 == 0 else destination.get("name", "City center"),
            "duration": "4 hours"
        },
        "evening": {
            "activity": random.choice(evening_activities),
            "location": "Local area",
            "duration": "3 hours"
        },
        "meals": {
            "breakfast": "Hotel or local café",
            "lunch": "Traditional restaurant",
            "dinner": "Recommended local spot"
        },
        "estimated_cost": destination["daily_budget_usd"],
        "tips": f"Remember to bring comfortable walking shoes. {destination['name']} is best explored on foot!"
    }
