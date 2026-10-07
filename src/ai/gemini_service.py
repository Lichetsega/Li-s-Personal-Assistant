import os
from typing import List, Optional
from src.config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL
from src.ai.tools import ToolRegistry

class GeminiService:
    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.api_key = GEMINI_API_KEY
        self.model_name = DEFAULT_GEMINI_MODEL
        self.tool_registry = tool_registry or ToolRegistry()
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.startswith("AIzaSy..."):
            print("[GeminiService] Warning: GEMINI_API_KEY not configured in .env.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            print(f"[GeminiService] Successfully initialized Google GenAI Client with model '{self.model_name}'.")
        except Exception as e:
            print(f"[GeminiService] Error initializing Google GenAI client: {e}")

    def generate_response(self, system_prompt: str, user_input: str, conversation_history: List[dict] = None) -> str:
        if not self.client:
            return (
                f"Hello! I am your AI Virtual Assistant. I noticed your GEMINI_API_KEY is not set yet in `.env`.\n"
                f"Please add your actual Gemini API key to `.env` to enable live AI responses!\n\n"
                f"(Your query was: '{user_input}')"
            )

        try:
            # Build full message prompt
            messages_str = f"{system_prompt}\n\nUser Query: {user_input}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages_str,
            )
            return response.text if response.text else "No text response returned."
        except Exception as e:
            print(f"[GeminiService] Error during content generation: {e}")
            return f"I encountered an error processing your query: {e}"
