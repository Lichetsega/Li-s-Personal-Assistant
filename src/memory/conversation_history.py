from typing import List, Dict, Any

class ConversationHistory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: List[Dict[str, str]] = []

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant_message(self, message: str):
        self.history.append({"role": "model", "content": message})
        self._trim()

    def _trim(self):
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def clear(self):
        self.history.clear()
