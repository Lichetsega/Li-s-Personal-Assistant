import time
import threading
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ConversationHistory")

class ConversationHistory:
    """
    Rolling Short-Term Conversation Memory Window (Multi-Turn Context).
    Maintains active session dialogue turns for context-aware multi-turn conversations.
    """
    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []

    def add_user_message(self, message: str):
        """Appends user message to session history."""
        if message and message.strip():
            self.history.append({
                "role": "user",
                "content": message.strip(),
                "timestamp": time.time()
            })
            self._trim_history()

    def add_assistant_message(self, message: str):
        """Appends assistant response to session history."""
        if message and message.strip():
            self.history.append({
                "role": "assistant",
                "content": message.strip(),
                "timestamp": time.time()
            })
            self._trim_history()

    def _trim_history(self):
        """Keeps only the most recent max_turns * 2 messages."""
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def get_formatted_history(self) -> str:
        """Formats conversation history into structured prompt context."""
        if not self.history:
            return ""

        formatted = "--- RECENT CONVERSATION HISTORY ---\n"
        for msg in self.history[:-1]:  # Exclude current prompt if already added
            role_label = "Visitor" if msg["role"] == "user" else "Assistant"
            formatted += f"{role_label}: {msg['content']}\n"
        return formatted + "\n"

    def clear(self):
        """Clears active session history."""
        self.history.clear()
        logger.info("Cleared conversation history.")


class SessionHistoryManager:
    """
    Thread-safe session history manager that isolates conversation context
    per visitor based on a unique session_id.
    Automatically purges expired sessions to prevent memory bloat on deployed servers.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get_history(self, session_id: Optional[str]) -> ConversationHistory:
        """Returns the isolated ConversationHistory for a given visitor session."""
        sid = (session_id or "default_session").strip()
        now = time.time()
        with self._lock:
            self._cleanup_expired(now)
            if sid not in self.sessions:
                self.sessions[sid] = {
                    "history": ConversationHistory(),
                    "last_active": now
                }
            else:
                self.sessions[sid]["last_active"] = now
            return self.sessions[sid]["history"]

    def _cleanup_expired(self, now: float):
        """Removes sessions inactive for longer than TTL."""
        expired = [sid for sid, d in self.sessions.items() if (now - d["last_active"]) > self.ttl]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired visitor sessions.")

session_manager = SessionHistoryManager()
