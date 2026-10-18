import os
import sys
import logging
import warnings

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
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-pro-latest"
]

class GeminiService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.client = None
        self.sdk_type = None
        self.context_builder = ContextBuilder()
        self._initialize_client()

    def _initialize_client(self):
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("GEMINI_API_KEY is not set or using placeholder. Gemini AI will operate in fallback mode.")
            return

        # 1. Try official new Google GenAI SDK (google-genai)
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.sdk_type = "google-genai"
            logger.info("Initialized Gemini AI client using new 'google-genai' SDK.")
            return
        except (ImportError, Exception) as e:
            logger.debug(f"google-genai import failed: {e}")

        # 2. Fallback to legacy google-generativeai SDK
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=self.api_key)
            self.client = genai_legacy
            self.sdk_type = "google-generativeai"
            logger.info("Initialized Gemini AI client using 'google-generativeai' SDK.")
        except Exception as e:
            logger.error(f"Failed to initialize any Gemini AI SDK: {e}")
            self.client = None

    def generate_response(self, user_prompt: str) -> str:
        """Generate response from Gemini AI model with security guardrails, history, and RAG."""
        # 1. Pre-execution Security Check (Input Guardrail)
        is_blocked, refusal_msg = security_guardrails.inspect_input(user_prompt)
        if is_blocked:
            return refusal_msg

        if not self.client:
            logger.warning("Gemini AI API key missing or uninitialized.")
            return "I am currently running in offline demonstration mode. How can I assist you with information about Li?"

        # Build dynamic system instruction with Profile + Memories + Notes RAG + Multi-Turn History + Live Environment
        sys_instruction = self.context_builder.build_system_instruction(user_prompt)
        last_error = None

        if self.sdk_type == "google-genai":
            for model_name in MODEL_CANDIDATES:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=f"{sys_instruction}\n\nUser: {user_prompt}"
                    )
                    if response and response.text:
                        raw_reply = response.text.strip()
                        # Apply Output Guardrail
                        return security_guardrails.filter_output(raw_reply)
                except Exception as e:
                    last_error = e
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
                        # Apply Output Guardrail
                        return security_guardrails.filter_output(raw_reply)
                except Exception as e:
                    last_error = e
                    continue

        # Error handling - never expose internal stack traces or API details
        return security_guardrails.sanitize_error(
            last_error or Exception("Gemini AI candidate models unreachable"),
            context="GeminiService.generate_response"
        )
