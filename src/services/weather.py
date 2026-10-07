import requests
from src.config import OPENWEATHER_API_KEY

class WeatherService:
    def get_weather(self, city: str = "London") -> str:
        # 1. Try OpenWeatherMap if key available
        if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "your_openweather_api_key_here":
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    return f"The current weather in {city} is {temp}°C with {desc}. Humidity is {humidity}%."
            except Exception as e:
                print(f"[WeatherService] OpenWeather error: {e}")

        # 2. Fallback to wttr.in
        try:
            url = f"https://wttr.in/{city}?format=3"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return f"Weather report for {city}: {resp.text.strip()}"
        except Exception as e:
            print(f"[WeatherService] wttr.in error: {e}")

        return f"Unable to fetch current weather data for '{city}' right now."
