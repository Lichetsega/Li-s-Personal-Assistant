import os
import tempfile
import logging
import time

logger = logging.getLogger("TTSEngine")

class HybridTTSEngine:
    """
    Hybrid Text-to-Speech Engine:
    Configured with a preferred Female voice.
    Attempts Online gTTS first, with offline pyttsx3 female voice fallback.
    """
    def __init__(self, voice_rate: int = 175):
        self.voice_rate = voice_rate
        self.pyttsx_engine = None
        self._init_offline_engine()

    def _init_offline_engine(self):
        try:
            import pyttsx3
            self.pyttsx_engine = pyttsx3.init()
            self.pyttsx_engine.setProperty('rate', self.voice_rate)
            
            # Select Female Voice
            voices = self.pyttsx_engine.getProperty('voices')
            female_voice = None
            for v in voices:
                name_lower = v.name.lower()
                if any(k in name_lower for k in ["zira", "hazel", "female", "eva", "samantha", "aria", "jenny"]):
                    female_voice = v
                    break
            
            if female_voice:
                self.pyttsx_engine.setProperty('voice', female_voice.id)
                logger.info(f"Selected Female pyttsx3 Voice: {female_voice.name}")
            elif len(voices) > 1:
                self.pyttsx_engine.setProperty('voice', voices[1].id)
                logger.info(f"Selected fallback secondary pyttsx3 Voice: {voices[1].name}")
            else:
                logger.info("Using default pyttsx3 voice.")
                
        except Exception as e:
            logger.warning(f"Could not initialize pyttsx3 offline engine: {e}")

    def speak_offline(self, text: str):
        """Speak using offline pyttsx3 engine."""
        if self.pyttsx_engine:
            try:
                logger.info("Using OFFLINE pyttsx3 female voice engine...")
                self.pyttsx_engine.say(text)
                self.pyttsx_engine.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Error in pyttsx3 offline TTS: {e}")
        return False

    def speak_online_gtts(self, text: str, lang: str = 'en') -> bool:
        """Speak using online gTTS library with fallback audio players."""
        try:
            from gtts import gTTS
            logger.info("Using ONLINE gTTS engine...")
            tts = gTTS(text=text, lang=lang, slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name

            tts.save(temp_filename)

            # Try playing audio using Pygame
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                pygame.mixer.music.unload()
                pygame.mixer.quit()
            except Exception as pg_err:
                logger.debug(f"Pygame playback failed: {pg_err}. Trying Windows Media Fallback...")
                if os.name == 'nt':
                    os.system(f'start /min "" "{temp_filename}"')
                    time.sleep(2)

            try:
                os.remove(temp_filename)
            except Exception:
                pass

            return True
        except Exception as e:
            logger.warning(f"Online gTTS failed: {e}")
            return False

    def speak(self, text: str):
        """
        Main entry point for speaking text.
        Primary: Online gTTS
        Fallback: Offline pyttsx3 Female Voice
        """
        if not text or not text.strip():
            return

        print(f"Assistant Voice: {text}")
        
        success = self.speak_online_gtts(text)
        if not success:
            logger.info("Switching to offline female TTS fallback...")
            success = self.speak_offline(text)
            if not success:
                logger.error("Both Online gTTS and Offline pyttsx3 failed to speak.")
