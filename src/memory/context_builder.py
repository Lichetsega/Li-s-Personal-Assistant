from datetime import datetime
from src.memory.profile_manager import ProfileManager
from src.memory.memory_store import MemoryStore
from src.memory.knowledge_base import KnowledgeBase
from src.memory.conversation_history import ConversationHistory

class ContextBuilder:
    def __init__(
        self,
        profile_manager: ProfileManager,
        memory_store: MemoryStore,
        knowledge_base: KnowledgeBase
    ):
        self.profile_manager = profile_manager
        self.memory_store = memory_store
        self.knowledge_base = knowledge_base

    def build_system_prompt(self, user_query: str = "") -> str:
        profile = self.profile_manager.load_profile()
        memories = self.memory_store.search_memories(user_query) if user_query else self.memory_store.get_all_memories()[:5]
        excerpts = self.knowledge_base.search_notes(user_query) if user_query else []

        now_str = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")

        prompt_parts = [
            "### SYSTEM ROLE & INSTRUCTIONS",
            f"You are **{profile.name}'s AI Virtual Assistant** (Li's Personal Assistant).",
            f"Your current local date and time is {now_str}.",
            f"Communication Style: {profile.communication_style}.",
            f"Voice Gender Preference: {profile.preferred_voice}.",
            "",
            "### USER PROFILE & BEHAVIORAL RULES",
            f"- User Name: {profile.name}",
            f"- Bio/Background: {profile.bio if profile.bio else 'Personal assistant user.'}"
        ]

        if profile.interests:
            prompt_parts.append(f"- User Interests: {', '.join(profile.interests)}")

        if profile.custom_rules:
            prompt_parts.append("- Custom Rules:")
            for rule in profile.custom_rules:
                prompt_parts.append(f"  * {rule}")

        if memories:
            prompt_parts.append("")
            prompt_parts.append("### RECALLED USER MEMORIES & PREFERENCES (Relational SQLite)")
            for mem in memories:
                prompt_parts.append(f"- [{mem.category.value.upper()}] {mem.content}")

        if excerpts:
            prompt_parts.append("")
            prompt_parts.append("### RELEVANT LOCAL NOTES & DOCUMENTS (RAG Knowledge Engine)")
            for ex in excerpts:
                prompt_parts.append(f"--- Note File: {ex.file_name} ---")
                prompt_parts.append(ex.content)

        prompt_parts.append("")
        prompt_parts.append("### GENERAL GUIDELINES")
        prompt_parts.append("1. Keep answers concise, direct, helpful, and natural.")
        prompt_parts.append("2. If asked about user notes, preferences, or history, reference the context above.")
        prompt_parts.append("3. Use native function tools (weather, news, wikipedia, tasks) whenever appropriate.")

        return "\n".join(prompt_parts)
