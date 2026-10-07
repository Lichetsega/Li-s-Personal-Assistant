import re
import datetime
import logging
from typing import Optional, Callable

from src.ai.gemini_service import GeminiService
from src.services.weather import get_weather
from src.services.news import get_news
from src.services.wikipedia_service import search_wikipedia
from src.services.task_manager import add_task, get_tasks, clear_tasks
from src.services.scheduler import ReminderScheduler
from src.memory.memory_store import MemoryStore
from src.memory.memory_extractor import MemoryExtractor
from src.memory.conversation_history import ConversationHistory
from src.memory.schema import MemoryCategory

logger = logging.getLogger("AssistantCore")

class AssistantCore:
    """
    Central Orchestrator:
    Routes incoming user commands to specific feature services, scheduler, memory store, RAG, or Gemini AI.
    """
    def __init__(self):
        self.gemini = GeminiService()
        self.memory_store = MemoryStore()
        self.memory_extractor = MemoryExtractor(self.memory_store)
        self.scheduler = ReminderScheduler()
        self.history = self.gemini.context_builder.conversation_history

    def register_reminder_callback(self, callback: Callable[[str], None]):
        """Registers a callback for proactive background reminder alerts."""
        self.scheduler.register_callback(callback)

    def process_command(self, text: str) -> str:
        """
        Processes text command and returns textual response.
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please repeat?"

        cmd = text.strip().lower()

        # Add user query to short-term multi-turn history (Option 4)
        self.history.add_user_message(text.strip())

        # 1. Proactive Timers & Reminders (Option 3 Engine)
        match_reminder = re.search(r"(?:remind me in|set a reminder for|alert me in)\s+(\d+(?:\.\d+)?)\s*(minute|minutes|min|mins|hour|hours)\s*(?:to|for)?\s*(.+)", cmd, re.IGNORECASE)
        if match_reminder:
            amount = float(match_reminder.group(1))
            unit = match_reminder.group(2).lower()
            reminder_text = match_reminder.group(3).strip()
            
            if "hour" in unit:
                amount = amount * 60.0

            reply = self.scheduler.set_reminder(reminder_text, delay_minutes=amount)
            self.history.add_assistant_message(reply)
            return reply

        if any(phrase in cmd for phrase in ["my reminders", "show reminders", "list reminders"]):
            reply = self.scheduler.list_reminders_summary()
            self.history.add_assistant_message(reply)
            return reply

        # 2. Dynamic Memory Commands ("remember that...", "what do you remember")
        if cmd.startswith("remember that ") or cmd.startswith("remember "):
            fact = re.sub(r"^(remember that|remember)\s*", "", text.strip(), flags=re.IGNORECASE).strip()
            if fact:
                item = self.memory_store.add_memory(fact, category=MemoryCategory.FACT)
                if item:
                    reply = f"Got it, Li! I've saved that to my memory: '{fact}'"
                    self.history.add_assistant_message(reply)
                    return reply
            return "What would you like me to remember?"

        if any(phrase in cmd for phrase in ["what do you remember", "show memories", "list memories", "my memories"]):
            memories = self.memory_store.get_all_memories()
            if not memories:
                reply = "I don't have any specific dynamic memories saved yet, Li."
            else:
                mem_list = "\n".join([f"• [{m.category.value}] {m.fact_text}" for m in memories[:10]])
                reply = f"Here is what I remember about you, Li:\n{mem_list}"
            self.history.add_assistant_message(reply)
            return reply

        # 3. History Control Commands
        if any(phrase in cmd for phrase in ["clear history", "reset conversation", "forget chat"]):
            self.history.clear()
            return "Cleared our short-term conversation history, Li."

        # 4. Greetings & Time
        if any(w in cmd for w in ["hello", "hi", "hey"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if hour < 12 else ("Good afternoon!" if hour < 18 else "Good evening!")
            reply = f"{greeting} I am your Gemini AI assistant. How can I assist you today, Li?"
            self.history.add_assistant_message(reply)
            return reply

        if "time" in cmd and "what" in cmd:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            reply = f"The current time is {now_str}."
            self.history.add_assistant_message(reply)
            return reply

        if "date" in cmd and "what" in cmd:
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            reply = f"Today is {today_str}."
            self.history.add_assistant_message(reply)
            return reply

        # 5. Weather Updates
        if "weather" in cmd:
            match = re.search(r"weather (in|for|at) ([a-zA-Z\s]+)", cmd)
            city = match.group(2).strip() if match else "London"
            reply = get_weather(city)
            self.history.add_assistant_message(reply)
            return reply

        # 6. News Updates
        if "news" in cmd or "headline" in cmd:
            reply = get_news(limit=4)
            self.history.add_assistant_message(reply)
            return reply

        # 7. Wikipedia Lookup
        if "wikipedia" in cmd or cmd.startswith("who is ") or cmd.startswith("what is "):
            query = re.sub(r"^(who is|what is|search wikipedia for|wikipedia)\s*", "", cmd).strip()
            if query and not any(k in query for k in ["your name", "time", "date", "weather", "my name", "me"]):
                reply = search_wikipedia(query)
                self.history.add_assistant_message(reply)
                return reply

        # 8. Tasks & Reminders List
        if "add task" in cmd or "remind me to" in cmd:
            task_text = re.sub(r"^(add task|remind me to)\s*", "", cmd).strip()
            reply = add_task(task_text)
            self.history.add_assistant_message(reply)
            return reply

        if "show tasks" in cmd or "my tasks" in cmd or "list tasks" in cmd:
            reply = get_tasks()
            self.history.add_assistant_message(reply)
            return reply

        if "clear tasks" in cmd:
            reply = clear_tasks()
            self.history.add_assistant_message(reply)
            return reply

        # Trigger Autonomous Background Fact Extraction (Phase 2)
        self.memory_extractor.extract_async(text, self.gemini)

        # 9. Fallback to Gemini AI with Native Function Calling, RAG, & History Context
        logger.info("Routing query to Gemini AI with full multi-tier context & tools...")
        reply = self.gemini.generate_response(text)
        
        # Save assistant reply to short-term history
        self.history.add_assistant_message(reply)
        return reply
