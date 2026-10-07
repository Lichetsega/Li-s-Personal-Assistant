class STTEngine:
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self._init_stt()

    def _init_stt(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("[STTEngine] SpeechRecognition initialized with Microphone.")
        except Exception as e:
            print(f"[STTEngine] Warning: SpeechRecognition init failed: {e}")

    def listen(self, timeout: int = 5) -> str:
        if not self.recognizer or not self.microphone:
            return ""

        try:
            import speech_recognition as sr
            print("🎙️ Listening... Speak into your microphone now...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("⚡ Recognizing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"🗣️ You said: '{text}'")
            return text
        except Exception as e:
            print(f"[STTEngine] Listening error / timeout: {e}")
            return ""
