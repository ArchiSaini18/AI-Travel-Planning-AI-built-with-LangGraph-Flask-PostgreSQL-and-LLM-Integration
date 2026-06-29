import requests
import os
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class LLMAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
        self.url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
    
    def generate_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating LLM completion: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    def extract_preferences(self, user_input: str) -> Dict[str, Any]:
        prompt = f"""You are a travel planning assistant. Extract travel preferences from the user's input.
Return ONLY a valid JSON object with these fields (use null if not mentioned):
- destination_name: name of city/country if mentioned (string or null)
- budget: "low", "medium", or "high"
- duration: number of days (integer)
- interests: array of strings (e.g., ["beach", "culture", "adventure"])
- travel_style: "relaxation", "adventure", "culture", "luxury", "budget"
- companions: "solo", "couple", "family", "friends"
- season: "spring", "summer", "fall", "winter" or null

User input: "{user_input}"

JSON:"""

        messages = [
            {"role": "system", "content": "You are a helpful travel assistant that extracts structured information. Return ONLY valid JSON, no markdown formatting."},
            {"role": "user", "content": prompt}
        ]
        
        response = ""
        try:
            response = self.generate_completion(messages, temperature=0.3, max_tokens=500)
            response_clean = response.strip()
            
            # Remove markdown code fence markers
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            elif response_clean.startswith("```"):
                response_clean = response_clean[3:]
            
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            response_clean = response_clean.strip()
            
            # Extract JSON if wrapped in markdown
            if "{" in response_clean:
                start_idx = response_clean.index("{")
                end_idx = response_clean.rfind("}") + 1
                response_clean = response_clean[start_idx:end_idx]
            
            preferences = json.loads(response_clean)
            return preferences
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, Response: {response}")
            return self._get_default_preferences()
        except Exception as e:
            logger.error(f"Error extracting preferences: {e}")
            return self._get_default_preferences()
    
    def generate_itinerary_description(self, destination: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        prompt = f"""Create a brief, engaging introduction for a {preferences.get('duration', 5)}-day trip to {destination['name']}, {destination['country']}.
User preferences: {preferences.get('interests', [])}
Budget level: {preferences.get('budget', 'medium')}

Keep it to 2-3 sentences, enthusiastic and inviting."""

        messages = [
            {"role": "system", "content": "You are an enthusiastic travel writer."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self.generate_completion(messages, temperature=0.8, max_tokens=200)
        except Exception:
            return f"Discover the wonders of {destination['name']}! This {preferences.get('duration', 5)}-day adventure will take you through the best this destination has to offer."
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        return {
            "budget": "medium",
            "duration": 7,
            "interests": ["culture", "food"],
            "travel_style": "relaxation",
            "companions": "solo",
            "season": None
        }


llm_api = LLMAPI()
