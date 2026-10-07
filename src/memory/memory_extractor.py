import re
from src.memory.memory_store import MemoryStore
from src.memory.schema import MemoryCategory

class MemoryExtractor:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def extract_and_store_facts(self, user_input: str, assistant_response: str = ""):
        """
        Analyzes user input for persistent facts, preferences, or goals,
        and saves them automatically into the SQLite memory store.
        """
        text = user_input.strip()
        
        # Rule-based heuristics for quick fact extraction
        patterns = [
            (r"(?:my name is|i am) ([a-zA-Z\s]+)", MemoryCategory.FACT, "User's name is {}"),
            (r"i (?:love|like|prefer) ([^\.\!\?]+)", MemoryCategory.PREFERENCE, "User prefers {}"),
            (r"i (?:hate|dislike|don't like) ([^\.\!\?]+)", MemoryCategory.PREFERENCE, "User dislikes {}"),
            (r"my (?:goal|plan) is to ([^\.\!\?]+)", MemoryCategory.GOAL, "User's goal is to {}"),
            (r"i work as (?:a|an)? ([^\.\!\?]+)", MemoryCategory.FACT, "User works as {}"),
            (r"i live in ([^\.\!\?]+)", MemoryCategory.FACT, "User lives in {}"),
        ]

        for pattern, category, template in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_val = match.group(1).strip()
                if len(extracted_val) > 2:
                    fact_content = template.format(extracted_val)
                    self.memory_store.add_memory(fact_content, category=category)
                    print(f"[MemoryExtractor] Saved fact: {fact_content}")
