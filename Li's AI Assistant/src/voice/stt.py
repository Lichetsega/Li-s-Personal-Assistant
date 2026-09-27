import logging
import speech_recognition as sr

logger = logging.getLogger("STTEngine")

class STTEngine:
    """
    Speech-To-Text engine using SpeechRecognition.
    Listens to microphone input and converts it to recognized text.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """
        Listen to input from default microphone and return recognized text string.
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening for microphone input...")
                print("🎙️ Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("⏳ Recognizing speech...")
            query = self.recognizer.recognize_google(audio, language="en-US")
            print(f"🗣️ User: {query}")
            return query
        except sr.WaitTimeoutError:
            logger.info("Speech recognition timed out (no speech detected).")
            return ""
        except sr.UnknownValueError:
            logger.info("Google Speech Recognition could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error accessing microphone or recognizing speech: {e}")
            return ""
