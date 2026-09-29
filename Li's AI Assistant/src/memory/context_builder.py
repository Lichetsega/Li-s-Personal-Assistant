import datetime
import logging
from typing import Optional

from src.memory.profile_manager import ProfileManager
from src.memory.memory_store import MemoryStore

logger = logging.getLogger("ContextBuilder")

class ContextBuilder:
    """
    Synthesizes multi-tier user profile, persistent SQLite memories, and real-time
    environmental context into a unified System Instruction for Gemini AI.
    """
    def __init__(
        self,
        profile_manager: Optional[ProfileManager] = None,
        memory_store: Optional[MemoryStore] = None
    ):
        self.profile_manager = profile_manager or ProfileManager()
        self.memory_store = memory_store or MemoryStore()

    def build_system_instruction(self, user_query: str = "") -> str:
        """
        Dynamically constructs the system instruction context.
        """
        profile = self.profile_manager.get_profile()
        identity = profile.identity
        prefs = profile.preferences

        # 1. Base Assistant Identity
        instruction = (
            f"You are the dedicated, highly intelligent personal AI voice assistant for {identity.preferred_name}.\n"
            f"Your voice persona is {prefs.communication_style} and {prefs.voice_tone}.\n"
            "Because your responses are spoken aloud via Text-to-Speech, keep answers concise, clear, natural, and friendly. "
            "Avoid lengthy markdown formatting, code blocks, or heavy lists unless explicitly requested.\n\n"
        )

        # 2. User Profile Summary
        instruction += "--- USER PROFILE ---\n"
        instruction += f"• Name: {identity.name} (Call them '{identity.preferred_name}')\n"
        instruction += f"• Bio: {identity.bio}\n"
        instruction += f"• Location & Timezone: {identity.location} ({identity.timezone})\n"
        instruction += f"• Preferred Units: {prefs.units}\n"
        instruction += f"• Favorite Topics: {', '.join(prefs.favorite_topics)}\n\n"

        # 3. Behavioral Guardrails & Rules
        instruction += "--- BEHAVIORAL RULES ---\n"
        for rule in profile.key_rules:
            instruction += f"• {rule}\n"
        instruction += "\n"

        # 4. Relevant Dynamic Memories (Retrieved from SQLite Store)
        memories = self.memory_store.search_memories(user_query, limit=6) if user_query else self.memory_store.get_all_memories()[:6]
        if memories or profile.custom_facts:
            instruction += "--- MEMORIES & KNOWN FACTS ABOUT USER ---\n"
            for fact in profile.custom_facts:
                instruction += f"• {fact}\n"
            for mem in memories:
                instruction += f"• [{mem.category.value}] {mem.fact_text}\n"
            instruction += "\n"

        # 5. Live Environment Context
        now = datetime.datetime.now()
        instruction += "--- REAL-TIME CONTEXT ---\n"
        instruction += f"• Current Date & Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"

        return instruction
