import os
import sys
import logging
import warnings
from typing import Optional, List, Any

# Suppress google.generativeai deprecation warning clutter in terminal logs
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

# Ensure root project path is included in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config import config
from src.memory.context_builder import ContextBuilder
from src.ai.tools import TOOL_FUNCTIONS
from src.security.guardrails import security_guardrails

logger = logging.getLogger("GeminiService")

MODEL_CANDIDATES = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]

class GeminiService:
    def __init__(self, api_key: str = None):
        raw_keys = api_key or config.GEMINI_API_KEY
        if isinstance(raw_keys, str):
            self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip() and k.strip() != "your_gemini_api_key_here"]
        elif isinstance(raw_keys, list):
            self.api_keys = [str(k).strip() for k in raw_keys if str(k).strip()]
        else:
            self.api_keys = []

        self.current_key_index = 0
        self.client = None
        self.sdk_type = None
        self.context_builder = ContextBuilder()
        self._initialize_client(self._get_active_api_key())

    def _get_active_api_key(self) -> Optional[str]:
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_index % len(self.api_keys)]

    def _rotate_to_next_key(self) -> bool:
        """Rotates to the next available API key if multiple keys are provided."""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            new_key = self._get_active_api_key()
            logger.info(f"Rotating to next Gemini API key (index {self.current_key_index})...")
            self._initialize_client(new_key)
            return True
        return False

    def _initialize_client(self, key: Optional[str] = None):
        active_key = key or self._get_active_api_key()
        if not active_key:
            logger.warning("No valid GEMINI_API_KEY available. Operating in local fallback mode.")
            self.client = None
            return

        # 1. Try official new Google GenAI SDK (google-genai)
        try:
            from google import genai
            self.client = genai.Client(api_key=active_key)
            self.sdk_type = "google-genai"
            logger.info("Initialized Gemini AI client using new 'google-genai' SDK.")
            return
        except (ImportError, Exception) as e:
            logger.debug(f"google-genai import failed: {e}")

        # 2. Fallback to legacy google-generativeai SDK
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=active_key)
            self.client = genai_legacy
            self.sdk_type = "google-generativeai"
            logger.info("Initialized Gemini AI client using 'google-generativeai' SDK.")
        except Exception as e:
            logger.error(f"Failed to initialize any Gemini AI SDK: {e}")
            self.client = None

    def generate_response(self, user_prompt: str, conversation_history: Optional[Any] = None) -> str:
        """Generate response with multi-key rotation and automatic local RAG fallback."""
        # 1. Pre-execution Security Check (Input Guardrail)
        is_blocked, refusal_msg = security_guardrails.inspect_input(user_prompt)
        if is_blocked:
            return refusal_msg

        # If no client or API keys configured, immediately use local RAG fallback
        if not self.client:
            logger.info("Gemini AI client unavailable. Answering query via local RAG.")
            local_reply = self.context_builder.knowledge_base.answer_query_locally(
                user_prompt,
                profile_manager=self.context_builder.profile_manager
            )
            return security_guardrails.filter_output(local_reply)

        # Build dynamic system instruction with Profile + Memories + Notes RAG + Multi-Turn History + Live Environment
        sys_instruction = self.context_builder.build_system_instruction(user_prompt, conversation_history=conversation_history)
        last_error = None

        # Attempt generation across available models and keys
        keys_to_try = max(1, len(self.api_keys))
        for _ in range(keys_to_try):
            if self.sdk_type == "google-genai":
                for model_name in MODEL_CANDIDATES:
                    try:
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=f"{sys_instruction}\n\nUser: {user_prompt}"
                        )
                        if response and response.text:
                            raw_reply = response.text.strip()
                            return security_guardrails.filter_output(raw_reply)
                    except Exception as e:
                        last_error = e
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            logger.warning(f"Model {model_name} quota exhausted (429). Trying candidate...")
                        continue

            elif self.sdk_type == "google-generativeai":
                for model_name in MODEL_CANDIDATES:
                    try:
                        model = self.client.GenerativeModel(
                            model_name=model_name,
                            system_instruction=sys_instruction
                        )
                        response = model.generate_content(user_prompt)
                        if response and response.text:
                            raw_reply = response.text.strip()
                            return security_guardrails.filter_output(raw_reply)
                    except Exception as e:
                        last_error = e
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            logger.warning(f"Model {model_name} quota exhausted (429). Trying candidate...")
                        continue

            # If quota exhausted and another key is available, rotate!
            if len(self.api_keys) > 1 and last_error and ("429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error)):
                logger.warning("Active API key quota exhausted. Rotating to next key...")
                self._rotate_to_next_key()
            else:
                break

        # 3. Seamless Local RAG Fallback (When API quota exhausted or network error)
        logger.warning(f"All Gemini models/keys exhausted or unavailable. Triggering Local RAG Fallback.")
        local_reply = self.context_builder.knowledge_base.answer_query_locally(
            user_prompt,
            profile_manager=self.context_builder.profile_manager
        )
        return security_guardrails.filter_output(local_reply)
