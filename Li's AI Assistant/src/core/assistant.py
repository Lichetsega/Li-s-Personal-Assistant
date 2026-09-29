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
from src.memory.memory_store import MemoryStore
from src.memory.memory_extractor import MemoryExtractor
from src.memory.schema import MemoryCategory

logger = logging.getLogger("AssistantCore")

class AssistantCore:
    """
    Central Orchestrator:
    Routes incoming user commands to specific feature services, memory store, or Gemini AI.
    """
    def __init__(self):
        self.gemini = GeminiService()
        self.memory_store = MemoryStore()
        self.memory_extractor = MemoryExtractor(self.memory_store)

    def process_command(self, text: str) -> str:
        """
        Processes text command and returns textual response.
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please repeat?"

        cmd = text.strip().lower()

        # 1. Memory Commands ("remember that...", "what do you remember")
        if cmd.startswith("remember that ") or cmd.startswith("remember "):
            fact = re.sub(r"^(remember that|remember)\s*", "", text.strip(), flags=re.IGNORECASE).strip()
            if fact:
                item = self.memory_store.add_memory(fact, category=MemoryCategory.FACT)
                if item:
                    return f"Got it, Li! I've saved that to my memory: '{fact}'"
            return "What would you like me to remember?"

        if any(phrase in cmd for phrase in ["what do you remember", "show memories", "list memories", "my memories"]):
            memories = self.memory_store.get_all_memories()
            if not memories:
                return "I don't have any specific dynamic memories saved yet, Li."
            mem_list = "\n".join([f"• [{m.category.value}] {m.fact_text}" for m in memories[:10]])
            return f"Here is what I remember about you, Li:\n{mem_list}"

        # 2. Greetings & Time
        if any(w in cmd for w in ["hello", "hi", "hey"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if hour < 12 else ("Good afternoon!" if hour < 18 else "Good evening!")
            return f"{greeting} I am your Gemini AI assistant. How can I assist you today, Li?"

        if "time" in cmd and "what" in cmd:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now_str}."

        if "date" in cmd and "what" in cmd:
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today_str}."

        # 3. Weather Updates
        if "weather" in cmd:
            match = re.search(r"weather (in|for|at) ([a-zA-Z\s]+)", cmd)
            city = match.group(2).strip() if match else "London"
            return get_weather(city)

        # 4. News Updates
        if "news" in cmd or "headline" in cmd:
            return get_news(limit=4)

        # 5. Jokes
        if "joke" in cmd or "tell me something funny" in cmd:
            return get_joke()

        # 6. Music Playback
        if cmd.startswith("play ") or "play music" in cmd or "play song" in cmd:
            topic = re.sub(r"^(play|play music|play song)\s*", "", cmd).strip()
            return play_music(topic)

        # 7. Wikipedia Lookup
        if "wikipedia" in cmd or cmd.startswith("who is ") or cmd.startswith("what is "):
            query = re.sub(r"^(who is|what is|search wikipedia for|wikipedia)\s*", "", cmd).strip()
            if query and not any(k in query for k in ["your name", "time", "date", "weather", "my name", "me"]):
                return search_wikipedia(query)

        # 8. Tasks & Reminders
        if "add task" in cmd or "remind me to" in cmd:
            task_text = re.sub(r"^(add task|remind me to)\s*", "", cmd).strip()
            return add_task(task_text)

        if "show tasks" in cmd or "my tasks" in cmd or "list tasks" in cmd:
            return get_tasks()

        if "clear tasks" in cmd:
            return clear_tasks()

        # Trigger Autonomous Background Fact Extraction
        self.memory_extractor.extract_async(text, self.gemini)

        # 9. Fallback to Gemini AI with dynamic user context & memory
        logger.info("Routing query to Gemini AI with full multi-tier context...")
        return self.gemini.generate_response(text)
