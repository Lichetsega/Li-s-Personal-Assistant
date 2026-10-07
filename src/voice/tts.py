import threading

class TTSEngine:
    def __init__(self, preferred_voice_gender: str = "Female"):
        self.preferred_voice_gender = preferred_voice_gender
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty("voices")
            
            # Select female voice if available
            female_voice = None
            for v in voices:
                v_name_lower = v.name.lower()
                if "zira" in v_name_lower or "hazel" in v_name_lower or "female" in v_name_lower or "samantha" in v_name_lower:
                    female_voice = v.id
                    break
            
            if female_voice:
                self.engine.setProperty("voice", female_voice)
                print(f"[TTSEngine] Bound to female voice: {female_voice}")
            elif voices:
                self.engine.setProperty("voice", voices[0].id)
                
            self.engine.setProperty("rate", 175)  # Speaking rate
        except Exception as e:
            print(f"[TTSEngine] Warning: PyTTSx3 initialization failed: {e}")

    def speak(self, text: str):
        if not text or not self.engine:
            return

        def _run_speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[TTSEngine] Speak error: {e}")

        # Run TTS in background thread so it doesn't block main loop
        threading.Thread(target=_run_speak, daemon=True).start()
