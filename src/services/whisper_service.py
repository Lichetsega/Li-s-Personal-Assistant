import io
import re
import logging
from typing import Optional
from src.config import config

logger = logging.getLogger("GroqWhisperService")

# Domain vocabulary prompt to prime Whisper with accurate portfolio & technical terms
DOMAIN_PROMPT = (
    "Liche Tsegaye, INSA, Agentic RAG, li's , li ,Python, FastAPI, Woliso, Addis Ababa, "
    "Jimma University, ChromaDB, SQLite, Gemini, Full-Stack, Software Engineer."
)

# Common Whisper hallucinations triggered by silent or truncated audio
HALLUCINATION_PATTERNS = [
    r"^thank\s+you\s+(?:very\s+much\s+)?for\s+(?:watching|listening|running).*$",
    r"^thanks\s+(?:very\s+much\s+)?for\s+(?:watching|listening|running).*$",
    r"^thanks\s+very\s+great.*$",
    r"^click\s+(?:jpeg|here|link|the\s+link).*$",
    r"^please\s+(?:like\s+and\s+)?subscribe.*$",
    r"^thank\s+you[\.\!\s]*$",
    r"^thanks[\.\!\s]*$",
    r"^bye[\.\!\s]*$",
    r"^you[\.\!\s]*$",
]

class GroqWhisperService:
    """
    High-fidelity Cloud Speech-to-Text service powered by Groq's hosted Whisper-large-v3.
    Provides sub-200ms ultra-accurate transcription with custom domain keyword boosting
    and hallucination defense for quiet/truncated audio clips.
    """
    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        self._client = None

    def is_available(self) -> bool:
        """Checks if a valid Groq API key is configured."""
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_groq_api_key_here")

    def _get_client(self):
        if not self._client and self.is_available():
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key.strip())
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self._client = None
        return self._client

    def _is_hallucination(self, text: str) -> bool:
        """Checks if transcription is a generic Whisper artifact from quiet audio."""
        if not text or len(text.strip()) < 3:
            return True
        clean = text.strip().lower()
        for pattern in HALLUCINATION_PATTERNS:
            if re.search(pattern, clean, flags=re.IGNORECASE):
                return True
        return False

    def transcribe(self, audio_bytes: bytes, filename: str = "recording.webm") -> Optional[str]:
        """
        Transcribes raw audio bytes using Groq whisper-large-v3 with domain vocabulary priming.
        Filters out silence-induced subtitle hallucinations.
        """
        client = self._get_client()
        if not client:
            logger.warning("Groq Whisper requested but GROQ_API_KEY is not configured.")
            return None

        try:
            audio_file = (filename, audio_bytes)
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                prompt=DOMAIN_PROMPT,
                response_format="json",
                language="en",
                temperature=0.0
            )
            text = transcription.text.strip()
            
            # Defense against Whisper silence hallucination
            if self._is_hallucination(text):
                logger.warning(f"Discarded Whisper silence hallucination: '{text}'")
                return None

            logger.info(f"Groq Whisper transcription success: {text}")
            return text
        except Exception as e:
            logger.error(f"Error during Groq Whisper transcription: {e}")
            return None

groq_whisper_service = GroqWhisperService()
