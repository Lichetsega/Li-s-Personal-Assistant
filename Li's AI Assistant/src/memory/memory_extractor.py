import logging
import threading
from typing import Optional

from src.memory.memory_store import MemoryStore
from src.memory.schema import MemoryCategory

logger = logging.getLogger("MemoryExtractor")

EXTRACTION_PROMPT = """
Analyze the following user input from a conversation with their personal assistant.
Determine if the user stated any NEW personal fact, preference, goal, relationship, or habit about themselves.

Examples of extractable facts:
- "I live in Paris now" -> Fact: User lives in Paris. Category: FACT
- "I prefer green tea over coffee" -> Fact: User prefers green tea over coffee. Category: PREFERENCE
- "I'm launching my app next month" -> Fact: User is launching their app next month. Category: GOAL

If there is a clear personal fact about the user, format your response as:
CATEGORY | Fact summary statement

If there are NO personal facts about the user (e.g., standard questions like 'what is 2+2', 'weather in Tokyo', greetings, or commands), respond with ONLY: NONE

User Input: "{user_input}"
Response:
"""

class MemoryExtractor:
    """
    Autonomous Background Engine:
    Extracts new facts, preferences, and goals from user interactions and stores them in SQLite memory.
    """
    def __init__(self, memory_store: Optional[MemoryStore] = None):
        self.memory_store = memory_store or MemoryStore()

    def extract_async(self, user_input: str, gemini_service):
        """Launches background thread to analyze conversation for personal facts."""
        thread = threading.Thread(
            target=self._run_extraction,
            args=(user_input, gemini_service),
            daemon=True
        )
        thread.start()

    def _run_extraction(self, user_input: str, gemini_service):
        if not user_input or len(user_input.strip()) < 8:
            return

        # Skip generic commands or questions
        lower_input = user_input.lower().strip()
        if any(lower_input.startswith(w) for w in ["what is", "who is", "weather in", "play ", "tell me a joke", "remember that", "show tasks", "clear tasks"]):
            return

        try:
            prompt = EXTRACTION_PROMPT.format(user_input=user_input)
            response = gemini_service.generate_response(prompt)
            
            if not response or "NONE" in response.upper():
                return

            lines = response.strip().split("\n")
            for line in lines:
                if "|" in line:
                    parts = line.split("|", 1)
                    cat_name = parts[0].strip().upper()
                    fact_text = parts[1].strip()

                    try:
                        category = MemoryCategory[cat_name]
                    except KeyError:
                        category = MemoryCategory.FACT

                    if fact_text and len(fact_text) > 5:
                        self.memory_store.add_memory(fact_text, category=category)
                        logger.info(f"Autonomously extracted new memory: [{category.value}] {fact_text}")
        except Exception as e:
            logger.debug(f"Memory extraction process skipped or failed: {e}")
