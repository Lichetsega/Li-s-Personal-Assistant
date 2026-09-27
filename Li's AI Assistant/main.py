import sys
import logging
from src.core.assistant import AssistantCore
from src.voice.stt import STTEngine
from src.voice.tts import HybridTTSEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def main():
    print("=" * 60)
    print(" 🎙️  Gemini AI Virtual Voice Assistant (CLI Mode)")
    print(" Type 'voice' to speak, type your command, or type 'exit' to quit.")
    print("=" * 60)

    assistant = AssistantCore()
    tts = HybridTTSEngine()
    stt = STTEngine()

    initial_greeting = "Hello! I am your Gemini AI voice assistant. How can I help you today?"
    tts.speak(initial_greeting)

    while True:
        try:
            user_input = input("\n[You] ('voice' / 'exit' / command): ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                farewell = "Goodbye! Have a great day!"
                tts.speak(farewell)
                break

            if user_input.lower() == "voice":
                user_input = stt.listen()
                if not user_input:
                    print("No speech recognized. Returning to text mode.")
                    continue

            # Process command
            response = assistant.process_command(user_input)
            print(f"\n[Assistant]: {response}")

            # Speak response using Hybrid TTS (Online gTTS -> Offline pyttsx3 fallback)
            tts.speak(response)

        except KeyboardInterrupt:
            print("\nExiting assistant...")
            sys.exit(0)

if __name__ == "__main__":
    main()
