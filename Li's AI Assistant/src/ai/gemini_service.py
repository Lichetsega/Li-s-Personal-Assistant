import os
import sys
import logging
import warnings

# Suppress google.generativeai deprecation warning clutter in terminal logs
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

# Ensure root project path is included in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config import config

logger = logging.getLogger("GeminiService")

SYSTEM_INSTRUCTION = (
    "You are Li's Voice AI Assistant, a helpful, polite, and intelligent virtual assistant. "
    "Because your responses will be read aloud via Text-to-Speech, keep your responses concise, "
    "clear, natural, and friendly. Avoid lengthy formatting, markdown tables, or excessive code unless explicitly asked."
)

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-pro"
]

class GeminiService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.client = None
        self.sdk_type = None
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
        """Generate response from Gemini AI model given user prompt."""
        if not self.client:
            return (
                "Gemini AI API key is missing or invalid. "
                "Please add your valid GEMINI_API_KEY in the .env file to enable full AI responses."
            )

        last_error = None

        if self.sdk_type == "google-genai":
            for model_name in MODEL_CANDIDATES:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=f"{SYSTEM_INSTRUCTION}\n\nUser: {user_prompt}"
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_error = e
                    continue

        elif self.sdk_type == "google-generativeai":
            for model_name in MODEL_CANDIDATES:
                try:
                    model = self.client.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                    response = model.generate_content(user_prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_error = e
                    continue

        logger.error(f"All Gemini model candidates failed. Last error: {last_error}")
        return f"I encountered an issue connecting to Gemini AI: {str(last_error)}"
