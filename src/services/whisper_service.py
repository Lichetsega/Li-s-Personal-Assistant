import io
import logging
from typing import Optional
from src.config import config

logger = logging.getLogger("GroqWhisperService")

# Natural sentence prompt to condition Whisper's language model for developer & personal queries
DOMAIN_PROMPT = (
    "The following is a spoken conversation with and about Liche Tsegaye, "
    "a software engineer who completed an internship at INSA and developed the Visit Ethiopia Agentic RAG system."
)

class GroqWhisperService:
    """
    High-fidelity Cloud Speech-to-Text service powered by Groq's hosted Whisper-large-v3.
    Uses model-level acoustic metrics and natural contextual priming.
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

    def transcribe(self, audio_bytes: bytes, filename: str = "recording.wav") -> Optional[str]:
        """
        Transcribes audio bytes using Groq Whisper-large-v3.
        Evaluates Whisper's native acoustic segments and confidence scores.
        """
        client = self._get_client()
        if not client:
            logger.warning("Groq Whisper requested but GROQ_API_KEY is not configured.")
            return None

        try:
            audio_file = (filename, audio_bytes)
            result = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                prompt=DOMAIN_PROMPT,
                response_format="verbose_json",
                language="en",
                temperature=0.0
            )

            text = (result.text or "").strip()
            if not text:
                return None

            # Whisper native model metrics: Check if model classified audio as silence/noise
            if hasattr(result, "segments") and result.segments:
                avg_no_speech = sum(getattr(s, "no_speech_prob", 0.0) for s in result.segments) / len(result.segments)
                avg_compression = sum(getattr(s, "compression_ratio", 1.0) for s in result.segments) / len(result.segments)
                
                # If the neural net determines the segment contains no speech (> 65% probability)
                # or entered a repetitive generation loop (compression ratio > 2.4)
                if avg_no_speech > 0.65 or avg_compression > 2.4:
                    logger.info(f"Whisper acoustic evaluation: Non-speech audio detected (no_speech_prob: {avg_no_speech:.2f}).")
                    return None

            logger.info(f"Groq Whisper transcription success: {text}")
            return text
        except Exception as e:
            logger.error(f"Error during Groq Whisper transcription: {e}")
            return None

groq_whisper_service = GroqWhisperService()
