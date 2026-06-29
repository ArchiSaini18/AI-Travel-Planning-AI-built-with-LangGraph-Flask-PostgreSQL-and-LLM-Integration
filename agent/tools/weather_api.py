import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class WeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, latitude: float, longitude: float, days: int = 7) -> Optional[Dict[str, Any]]:
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "current_weather": "true",
                "timezone": "auto",
                "forecast_days": days
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_weather_data(data)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_mock_weather()
    
    def _format_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            current = data.get("current_weather", {})
            daily = data.get("daily", {})
            
            forecast = []
            for i in range(len(daily.get("time", []))):
                forecast.append({
                    "date": daily["time"][i],
                    "temp_max": round(daily["temperature_2m_max"][i], 1),
                    "temp_min": round(daily["temperature_2m_min"][i], 1),
                    "precipitation": round(daily["precipitation_sum"][i], 1),
                    "weather_code": daily["weathercode"][i],
                    "condition": self._get_weather_condition(daily["weathercode"][i])
                })
            
            return {
                "current": {
                    "temperature": round(current.get("temperature", 0), 1),
                    "windspeed": round(current.get("windspeed", 0), 1),
                    "condition": self._get_weather_condition(current.get("weathercode", 0))
                },
                "forecast": forecast
            }
        except Exception as e:
            logger.error(f"Error formatting weather data: {e}")
            return self._get_mock_weather()
    
    def _get_weather_condition(self, code: int) -> str:
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Heavy drizzle",
            61: "Light rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Light snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Light showers",
            81: "Moderate showers",
            82: "Heavy showers",
            85: "Light snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def _get_mock_weather(self) -> Dict[str, Any]:
        return {
            "current": {
                "temperature": 22.0,
                "windspeed": 10.0,
                "condition": "Partly cloudy"
            },
            "forecast": [
                {
                    "date": "2025-11-24",
                    "temp_max": 25.0,
                    "temp_min": 18.0,
                    "precipitation": 0.0,
                    "weather_code": 1,
                    "condition": "Mainly clear"
                }
            ] * 7
        }


weather_api = WeatherAPI()
