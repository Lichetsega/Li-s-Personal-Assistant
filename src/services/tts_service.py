import io
import re
import hashlib
import logging
from typing import Optional, Dict

logger = logging.getLogger("CloudTTSService")

class CloudTTSService:
    """
    Cloud Text-to-Speech audio streaming service for mobile visitors.
    Generates natural MP3 audio using gTTS and caches results to guarantee
    instant playback on mobile browsers (iOS Safari, Android Chrome) where
    client-side Web Speech synthesis is blocked by autoplay policies.
    """
    def __init__(self, max_cache_entries: int = 200):
        self._cache: Dict[str, bytes] = {}
        self.max_cache_entries = max_cache_entries

    def _clean_for_speech(self, text: str) -> str:
        """Strips markdown links, emojis, and symbols for pleasant auditory output."""
        # Replace markdown links [Text](URL) with just Text
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove raw URLs
        clean = re.sub(r'https?://[^\s]+', '', clean)
        # Remove bullet markers and asterisks
        clean = re.sub(r'[\*\#\_•]', ' ', clean)
        # Collapse whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        # Cap length to 350 chars for fast streaming response
        if len(clean) > 350:
            clean = clean[:350].rsplit('.', 1)[0] + '.'
        return clean

    def synthesize_audio(self, text: str) -> Optional[bytes]:
        """Synthesizes text to MP3 audio bytes with in-memory caching."""
        clean_text = self._clean_for_speech(text)
        if not clean_text:
            return None

        # Check in-memory cache
        cache_key = hashlib.md5(clean_text.encode('utf-8')).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from gtts import gTTS
            fp = io.BytesIO()
            # Generate natural English voice
            tts = gTTS(text=clean_text, lang='en', slow=False)
            tts.write_to_fp(fp)
            audio_bytes = fp.getvalue()

            # Cache audio if under limit
            if len(self._cache) < self.max_cache_entries:
                self._cache[cache_key] = audio_bytes

            return audio_bytes
        except Exception as e:
            logger.error(f"Cloud TTS synthesis error: {e}")
            return None

cloud_tts_service = CloudTTSService()
