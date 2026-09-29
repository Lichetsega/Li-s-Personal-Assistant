import os
import sys
import requests
import logging

# Ensure root project path is included in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import config

logger = logging.getLogger("WeatherService")

def get_weather(city: str = "London") -> str:
    """
    Fetch current weather updates for a given city.
    Uses OpenWeatherMap API if key is present, otherwise falls back to wttr.in.
    """
    api_key = config.OPENWEATHER_API_KEY
    if api_key:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            res = requests.get(url, timeout=5)
            data = res.json()
            if res.status_code == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"The current weather in {city} is {temp}°C with {desc}."
        except Exception as e:
            logger.warning(f"OpenWeatherMap API failed: {e}. Trying fallback...")

    # Fallback to wttr.in API (No API key required)
    try:
        url = f"https://wttr.in/{city}?format=3"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.text.strip():
            return f"Weather report: {res.text.strip()}"
    except Exception as e:
        logger.error(f"wttr.in fallback failed: {e}")

    return f"Sorry, I couldn't fetch weather information for {city} right now."
