import re
import datetime
import logging
from typing import Optional, Callable

from src.ai.gemini_service import GeminiService
from src.services.weather import get_weather
from src.services.news import get_news
from src.memory.memory_store import MemoryStore
from src.memory.conversation_history import ConversationHistory, session_manager
from src.security.guardrails import security_guardrails

logger = logging.getLogger("AssistantCore")

class AssistantCore:
    """
    Central Portfolio Assistant Orchestrator:
    Routes incoming visitor commands to portfolio services, RAG knowledge base, or Gemini AI.
    Protected by pre-input inspection, output code leak filtering, and error sanitization.
    Maintains isolated multi-turn conversation memory per visitor session.
    """
    def __init__(self):
        self.gemini = GeminiService()
        self.memory_store = MemoryStore()

    def _normalize_speech_input(self, text: str) -> str:
        """Corrects common acoustic speech-to-text mishearings for domain terms."""
        normalized = text
        # INSA mishearings: 'party song', 'party saw', 'in saw', 'in sa', 'inside'
        normalized = re.sub(r"\b(?:party\s+song|party\s+saw|in\s+saw|in\s+suh|in\s+sa)\b", "at INSA", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\binternship\s+(?:inside|in\s+sight)\b", "internship at INSA", normalized, flags=re.IGNORECASE)
        # RAG mishearings
        normalized = re.sub(r"\b(?:ragged|raggae)\b(?=\s*(?:agent|retrieval|project|system|chatbot|architecture))", "RAG", normalized, flags=re.IGNORECASE)
        # Li / Liche mishearings
        normalized = re.sub(r"\b(?:reach's|lisa's|lee's)\b", "Li's", normalized, flags=re.IGNORECASE)
        # 'sleep with candidate' / 'make me sleep with' mishearing for 'makes Li a great candidate'
        normalized = re.sub(r"\b(?:makes?\s+me\s+sleep\s+with|sleep\s+with)\b(?=\s*candidate)", "makes Li a great", normalized, flags=re.IGNORECASE)
        return normalized

    def process_command(self, text: str, session_id: str = "default_session") -> str:
        """
        Processes text command, applies security guardrails, and returns sanitized textual response.
        Maintains isolated conversation history for each visitor based on session_id.
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please repeat?"

        clean_text = self._normalize_speech_input(text.strip())
        history = session_manager.get_history(session_id)

        # 1. Pre-execution Security Guardrail (Prompt Injection & Code Probing Defense)
        is_blocked, refusal_msg = security_guardrails.inspect_input(clean_text)
        if is_blocked:
            history.add_user_message(clean_text)
            history.add_assistant_message(refusal_msg)
            return refusal_msg

        # Add visitor query to their session history
        history.add_user_message(clean_text)

        try:
            # 2. Execute Internal Command Routing with isolated visitor history
            raw_reply = self._dispatch_command(clean_text, history)
            
            # 3. Output Guardrail (Filter Out Code Leaks, System Prompts, or Paths)
            safe_reply = security_guardrails.filter_output(raw_reply)
            history.add_assistant_message(safe_reply)
            return safe_reply
        except Exception as e:
            # 4. Safe Error Sanitization (Never Leak Stack Traces or File Paths)
            safe_error = security_guardrails.sanitize_error(e, context="AssistantCore.process_command")
            history.add_assistant_message(safe_error)
            return safe_error

    def _dispatch_command(self, text: str, history: ConversationHistory) -> str:
        """Internal dispatch logic for feature routing."""
        cmd = text.strip().lower()

        # 1. Contact & Socials Queries (LinkedIn, Email, WhatsApp, Telegram)
        if any(w in cmd for w in ["contact", "reach li", "hire li", "email li", "linkedin", "phone", "whatsapp", "telegram"]):
            return (
                "You can reach and connect with Liche Tsegaye through:\n"
                "• **LinkedIn**: [Connect on LinkedIn](https://www.linkedin.com/in/liche-tsegaye-05a25b361)\n"
                "• **Email**: [lichetsega@gmail.com](mailto:lichetsega@gmail.com)\n"
                "• **WhatsApp**: [+251 945 733 554](https://api.whatsapp.com/send/?phone=251945733554)\n"
                "• **Telegram**: [@Lichetsega](https://t.me/Lichetsega)\n"
                "• **GitHub**: [github.com/Lichetsega](https://github.com/Lichetsega)\n"
                "• **Resume / CV**: [View & Download Li's Resume](/static/resume.html)"
            )

        # 2. Resume & CV Requests
        if any(w in cmd for w in ["resume", "cv", "curriculum vitae"]):
            return (
                "You can view and download Li's CV / Resume directly here: [View & Download Li's Resume](/static/resume.html).\n\n"
                "You can also connect with Li on [LinkedIn](https://www.linkedin.com/in/liche-tsegaye-05a25b361) "
                "or email her at [lichetsega@gmail.com](mailto:lichetsega@gmail.com)."
            )

        # 3. Live GitHub Commits & Repository Queries
        if any(w in cmd for w in ["recent commit", "latest commit", "recent commits", "latest commits", "git commit"]):
            from src.services.github_service import get_latest_commits
            return get_latest_commits("Li-s-Personal-Assistant", count=3)

        if any(w in cmd for w in ["github repos", "list repos", "my repos", "public repos"]):
            from src.services.github_service import list_user_repos
            return list_user_repos()

        # 4. History Control Commands (Per-Visitor)
        if any(phrase in cmd for phrase in ["clear history", "reset conversation", "forget chat"]):
            history.clear()
            return "I've reset our conversation history. How can I help you discover Li's portfolio today?"

        # 5. Greetings
        is_greeting = bool(re.search(r"^(?:hello|hi|hey|greetings)\b", cmd)) or cmd in ["hello", "hi", "hey"]
        if is_greeting and len(cmd.split()) <= 4 and not any(q in cmd for q in ["what", "who", "where", "tell me", "how", "can you", "why", "project", "work", "experience"]):
            hour = datetime.datetime.now().hour
            greeting = "Good morning!" if hour < 12 else ("Good afternoon!" if hour < 18 else "Good evening!")
            return f"{greeting} I'm Li's AI portfolio assistant. Ask me anything about Liche Tsegaye — her projects, skills, INSA internship, background, or how to get in touch!"

        # 6. Time & Date
        if re.search(r"\bwhat(?:\s+is|\s+'s)?\s+(?:the\s+)?(?:current\s+)?time\b", cmd) or (cmd.startswith("time") and len(cmd.split()) <= 3):
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current local time is {now_str}."

        if re.search(r"\bwhat(?:\s+is|\s+'s)?\s+(?:the\s+)?(?:current\s+|today's\s+)?date\b", cmd) or (re.search(r"\btoday's\s+date\b", cmd) and len(cmd.split()) <= 4):
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today_str}."

        # 7. Weather Updates
        if "weather" in cmd:
            match = re.search(r"weather (in|for|at) ([a-zA-Z\s]+)", cmd)
            city = match.group(2).strip() if match else "London"
            return get_weather(city)

        # 8. News Updates
        if "news" in cmd or "headline" in cmd:
            return get_news(limit=4)

        # 9. Pronoun Detection — "she/he/her/his/they" → explicitly route about Liche
        LICHE_PRONOUNS = ["she", "her", "he", "his", "they", "their"]
        first_word = cmd.split()[0] if cmd.split() else ""
        if first_word in LICHE_PRONOUNS or any(f" {p} " in f" {cmd} " for p in LICHE_PRONOUNS):
            pronoun_note = (
                f"[Note: The visitor used a pronoun. They are asking about Liche Tsegaye. "
                f"Please answer their question about Li in third person.] "
                f"Original question: {text.strip()}"
            )
            logger.info("Pronoun detected — routing to Gemini with Liche context...")
            return self.gemini.generate_response(pronoun_note, conversation_history=history)

        # 10. Fallback to Gemini AI with isolated visitor history & full portfolio context
        logger.info("Routing query to Gemini AI with visitor session context...")
        return self.gemini.generate_response(text, conversation_history=history)
