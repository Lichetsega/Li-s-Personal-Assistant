import re
import datetime
import logging
from typing import Optional, Callable

from src.ai.gemini_service import GeminiService
from src.services.weather import get_weather
from src.services.news import get_news
from src.services.task_manager import add_task, get_tasks, clear_tasks
from src.services.scheduler import ReminderScheduler
from src.memory.memory_store import MemoryStore
from src.memory.memory_extractor import MemoryExtractor
from src.memory.conversation_history import ConversationHistory
from src.memory.schema import MemoryCategory
from src.security.guardrails import security_guardrails

logger = logging.getLogger("AssistantCore")

class AssistantCore:
    """
    Central Orchestrator:
    Routes incoming user commands to specific feature services, scheduler, memory store, RAG, or Gemini AI.
    Protected by pre-input inspection, output code leak filtering, and error sanitization.
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
        Processes text command, applies security guardrails, and returns sanitized textual response.
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please repeat?"

        clean_text = text.strip()

        # 1. Pre-execution Security Guardrail (Prompt Injection & Code Probing Defense)
        is_blocked, refusal_msg = security_guardrails.inspect_input(clean_text)
        if is_blocked:
            self.history.add_user_message(clean_text)
            self.history.add_assistant_message(refusal_msg)
            return refusal_msg

        # Add user query to short-term multi-turn history
        self.history.add_user_message(clean_text)

        try:
            # 2. Execute Internal Command Routing
            raw_reply = self._dispatch_command(clean_text)
            
            # 3. Output Guardrail (Filter Out Code Leaks, System Prompts, or Paths)
            safe_reply = security_guardrails.filter_output(raw_reply)
            self.history.add_assistant_message(safe_reply)
            return safe_reply
        except Exception as e:
            # 4. Safe Error Sanitization (Never Leak Stack Traces or File Paths)
            safe_error = security_guardrails.sanitize_error(e, context="AssistantCore.process_command")
            self.history.add_assistant_message(safe_error)
            return safe_error

    def _dispatch_command(self, text: str) -> str:
        """Internal dispatch logic for feature routing."""
        cmd = text.strip().lower()

        # 1. Proactive Timers & Reminders (Option 3 Engine)
        match_reminder = re.search(r"(?:remind me in|set a reminder for|alert me in)\s+(\d+(?:\.\d+)?)\s*(minute|minutes|min|mins|hour|hours)\s*(?:to|for)?\s*(.+)", cmd, re.IGNORECASE)
        if match_reminder:
            amount = float(match_reminder.group(1))
            unit = match_reminder.group(2).lower()
            reminder_text = match_reminder.group(3).strip()
            
            if "hour" in unit:
                amount = amount * 60.0

            return self.scheduler.set_reminder(reminder_text, delay_minutes=amount)

        if any(phrase in cmd for phrase in ["my reminders", "show reminders", "list reminders"]):
            return self.scheduler.list_reminders_summary()

        # 2. Dynamic Memory Commands ("remember that...", "what do you remember")
        if cmd.startswith("remember that ") or cmd.startswith("remember "):
            fact = re.sub(r"^(remember that|remember)\s*", "", text.strip(), flags=re.IGNORECASE).strip()
            if fact:
                item = self.memory_store.add_memory(fact, category=MemoryCategory.FACT)
                if item:
                    return f"Got it! I've noted that down: '{fact}'"
            return "What would you like me to remember?"

        if any(phrase in cmd for phrase in ["what do you remember", "show memories", "list memories", "my memories"]):
            memories = self.memory_store.get_all_memories()
            if not memories:
                return "I don't have any additional notes saved about Li just yet."
            mem_list = "\n".join([f"• [{m.category.value}] {m.fact_text}" for m in memories[:10]])
            return f"Here is what I know about Li:\n{mem_list}"

        # 3. History Control Commands
        if any(phrase in cmd for phrase in ["clear history", "reset conversation", "forget chat"]):
            self.history.clear()
            return "Cleared the short-term conversation history."

        # 4. Greetings & Time (Use word boundaries so 'hi' doesn't match 'shipped' or 'this')
        is_greeting = bool(re.search(r"^(?:hello|hi|hey|greetings)\b", cmd)) or cmd in ["hello", "hi", "hey"]
        if is_greeting and len(cmd.split()) <= 4 and not any(q in cmd for q in ["what", "who", "where", "tell me", "how", "can you", "why", "project", "work", "experience"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if hour < 12 else ("Good afternoon!" if hour < 18 else "Good evening!")
            return f"{greeting} I'm Li's personal AI assistant. Ask me anything about Liche Tsegaye — her skills, projects, background, or how to get in touch!"

        if "time" in cmd and "what" in cmd:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now_str}."

        if "date" in cmd and "what" in cmd:
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today_str}."

        # 5. Weather Updates
        if "weather" in cmd:
            match = re.search(r"weather (in|for|at) ([a-zA-Z\s]+)", cmd)
            city = match.group(2).strip() if match else "London"
            return get_weather(city)

        # 6. Resume & CV Requests
        if any(w in cmd for w in ["resume", "cv", "curriculum vitae"]):
            return "You can view and download Li's CV / Resume directly here: [View & Download Li's Resume](/static/resume.html). You can also reach Li directly at lichetsega@gmail.com or via Telegram at https://t.me/Lichetsega."

        # 7. Live GitHub Commits & Repository Queries
        if any(w in cmd for w in ["recent commit", "latest commit", "recent commits", "latest commits", "git commit"]):
            from src.services.github_service import get_latest_commits
            return get_latest_commits("Li-s-Personal-Assistant", count=3)

        if any(w in cmd for w in ["github repos", "list repos", "my repos", "public repos"]):
            from src.services.github_service import list_user_repos
            return list_user_repos()

        # 8. News Updates
        if "news" in cmd or "headline" in cmd:
            return get_news(limit=4)

        # 7. Pronoun Detection — "she/he/her/his/they" → treat as question about Liche
        LICHE_PRONOUNS = ["she", "her", "he", "his", "they", "their"]
        first_word = cmd.split()[0] if cmd.split() else ""
        if first_word in LICHE_PRONOUNS or any(f" {p} " in f" {cmd} " for p in LICHE_PRONOUNS):
            # Rewrite the query to make it explicitly about Liche for Gemini
            pronoun_note = (
                f"[Note: The visitor used a pronoun (he/she/they/her/his/their). "
                f"They are asking about Liche Tsegaye. Please answer their question about Li in third person, "
                f"and naturally clarify that Li uses she/her pronouns if relevant.] "
                f"Original question: {text.strip()}"
            )
            logger.info("Pronoun detected — routing to Gemini with Liche context...")
            return self.gemini.generate_response(pronoun_note)

        # 8. Tasks & Reminders List
        if "add task" in cmd or "remind me to" in cmd:
            task_text = re.sub(r"^(add task|remind me to)\s*", "", cmd).strip()
            return add_task(task_text)

        if "show tasks" in cmd or "my tasks" in cmd or "list tasks" in cmd:
            return get_tasks()

        if "clear tasks" in cmd:
            return clear_tasks()

        # Autonomous Background Fact Extraction is disabled to preserve Gemini API quota on free tier
        # (Visitors to the portfolio do not need automated personal fact extraction)
        # self.memory_extractor.extract_async(text, self.gemini)

        # 9. Fallback to Gemini AI with Native Function Calling, RAG, & History Context
        logger.info("Routing query to Gemini AI with full multi-tier context & tools...")
        return self.gemini.generate_response(text)
