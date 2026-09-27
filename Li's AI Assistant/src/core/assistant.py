import re
import datetime
import logging

from src.ai.gemini_service import GeminiService
from src.services.weather import get_weather
from src.services.news import get_news
from src.services.wikipedia_service import search_wikipedia
from src.services.music import play_music
from src.services.jokes import get_joke
from src.services.task_manager import add_task, get_tasks, clear_tasks

logger = logging.getLogger("AssistantCore")

class AssistantCore:
    """
    Central Orchestrator:
    Routes incoming user commands to specific feature services or Gemini AI.
    """
    def __init__(self):
        self.gemini = GeminiService()

    def process_command(self, text: str) -> str:
        """
        Processes text command and returns textual response.
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please repeat?"

        cmd = text.strip().lower()

        # 1. Greetings & Time
        if any(w in cmd for w in ["hello", "hi", "hey"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if hour < 12 else ("Good afternoon!" if hour < 18 else "Good evening!")
            return f"{greeting} I am your Gemini AI assistant. How can I assist you today?"

        if "time" in cmd and "what" in cmd:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now_str}."

        if "date" in cmd and "what" in cmd:
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today_str}."

        # 2. Weather Updates
        if "weather" in cmd:
            # Extract city if specified e.g., "weather in Tokyo"
            match = re.search(r"weather (in|for|at) ([a-zA-Z\s]+)", cmd)
            city = match.group(2).strip() if match else "London"
            return get_weather(city)

        # 3. News Updates
        if "news" in cmd or "headline" in cmd:
            return get_news(limit=4)

        # 4. Jokes
        if "joke" in cmd or "tell me something funny" in cmd:
            return get_joke()

        # 5. Music Playback
        if cmd.startswith("play ") or "play music" in cmd or "play song" in cmd:
            topic = re.sub(r"^(play|play music|play song)\s*", "", cmd).strip()
            return play_music(topic)

        # 6. Wikipedia Lookup
        if "wikipedia" in cmd or cmd.startswith("who is ") or cmd.startswith("what is "):
            query = re.sub(r"^(who is|what is|search wikipedia for|wikipedia)\s*", "", cmd).strip()
            if query and not any(k in query for k in ["your name", "time", "date", "weather"]):
                return search_wikipedia(query)

        # 7. Tasks & Reminders
        if "add task" in cmd or "remind me to" in cmd:
            task_text = re.sub(r"^(add task|remind me to)\s*", "", cmd).strip()
            return add_task(task_text)

        if "show tasks" in cmd or "my tasks" in cmd or "list tasks" in cmd:
            return get_tasks()

        if "clear tasks" in cmd:
            return clear_tasks()

        # 8. Fallback to Gemini AI for General Q&A & Complex Queries
        logger.info("Routing query to Gemini AI...")
        return self.gemini.generate_response(text)
