import time
import logging
from typing import List, Dict, Any

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

    def get_formatted_history((self) -> str:
        """Formats conversation history into structured prompt context."""
        if not self.history:
            return ""

        formatted = "--- RECENT CONVERSATION HISTORY ---\n"
        for msg in self.history[:-1]:  # Exclude current prompt if already added
            role_label = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role_label}: {msg['content']}\n"
        return formatted + "\n"

    def clear(self):
        """Clears active session history."""
        self.history.clear()
        logger.info("Cleared conversation history.")
