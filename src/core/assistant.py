from typing import Dict, Any, Optional
from src.memory.profile_manager import ProfileManager
from src.memory.memory_store import MemoryStore
from src.memory.memory_extractor import MemoryExtractor
from src.memory.knowledge_base import KnowledgeBase
from src.memory.conversation_history import ConversationHistory
from src.memory.context_builder import ContextBuilder
from src.ai.tools import ToolRegistry
from src.ai.gemini_service import GeminiService
from src.voice.tts import TTSEngine
from src.voice.stt import STTEngine

class AssistantOrchestrator:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.memory_store = MemoryStore()
        self.memory_extractor = MemoryExtractor(self.memory_store)
        self.knowledge_base = KnowledgeBase()
        self.history = ConversationHistory()
        self.context_builder = ContextBuilder(
            profile_manager=self.profile_manager,
            memory_store=self.memory_store,
            knowledge_base=self.knowledge_base
        )
        self.tool_registry = ToolRegistry()
        self.gemini_service = GeminiService(tool_registry=self.tool_registry)
        self.tts = TTSEngine()
        self.stt = STTEngine()

    def process_query(self, user_input: str, voice_mode: bool = False) -> Dict[str, Any]:
        user_input_clean = user_input.strip()
        if not user_input_clean:
            return {"response": "I didn't catch that. Could you please repeat?", "voice_mode": voice_mode}

        # 1. Record user message in short-term history
        self.history.add_user_message(user_input_clean)

        # 2. Synthesize system prompt with profile, memory DB, & RAG notes
        system_prompt = self.context_builder.build_system_prompt(user_query=user_input_clean)

        # 3. Generate response via Gemini AI
        response_text = self.gemini_service.generate_response(
            system_prompt=system_prompt,
            user_input=user_input_clean,
            conversation_history=self.history.get_history()
        )

        # 4. Record assistant response in history
        self.history.add_assistant_message(response_text)

        # 5. Extract personal facts into memory store asynchronously
        self.memory_extractor.extract_and_store_facts(user_input=user_input_clean, assistant_response=response_text)

        # 6. Speak aloud if in voice mode
        if voice_mode:
            self.tts.speak(response_text)

        return {
            "query": user_input_clean,
            "response": response_text,
            "voice_mode": voice_mode
        }
