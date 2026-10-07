import datetime
import logging
from typing import Optional

from src.memory.profile_manager import ProfileManager
from src.memory.memory_store import MemoryStore
from src.memory.knowledge_base import KnowledgeBase
from src.memory.conversation_history import ConversationHistory

logger = logging.getLogger("ContextBuilder")

class ContextBuilder:
    """
    Synthesizes multi-tier user profile, persistent SQLite memories,
    local RAG knowledge base notes, multi-turn chat history, and real-time environment
    into a unified System Instruction for Gemini AI.
    """
    def __init__(
        self,
        profile_manager: Optional[ProfileManager] = None,
        memory_store: Optional[MemoryStore] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        conversation_history: Optional[ConversationHistory] = None
    ):
        self.profile_manager = profile_manager or ProfileManager()
        self.memory_store = memory_store or MemoryStore()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.conversation_history = conversation_history or ConversationHistory()

    def build_system_instruction(self, user_query: str = "") -> str:
        """
        Dynamically constructs the system instruction context.
        """
        profile = self.profile_manager.get_profile()
        identity = profile.identity
        prefs = profile.preferences

        # 1. Base Assistant Identity & Voice Persona
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

        # 5. RAG Document & Notes Context (Option 2 Engine)
        if user_query:
            doc_context = self.knowledge_base.search(user_query, top_k=2)
            if doc_context:
                instruction += doc_context + "\n"

        # 6. Multi-Turn Session History (Option 4 Engine)
        history_context = self.conversation_history.get_formatted_history()
        if history_context:
            instruction += history_context

        # 7. Live Environment Context
        now = datetime.datetime.now()
        instruction += "--- REAL-TIME CONTEXT ---\n"
        instruction += f"• Current Date & Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"

        return instruction
