import sys
import logging
from src.core.assistant import AssistantCore
from src.voice.stt import STTEngine
from src.voice.tts import HybridTTSEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def main():
    print("=" * 60)
    print(" 🎙️  Li's AI Virtual Voice Assistant ")
    print(" Type 'voice' to speak, type your command, or type 'exit' to quit.")
    print(" Voice responses will only speak aloud when using 'voice' mode!")
    print("=" * 60)

    assistant = AssistantCore()
    tts = HybridTTSEngine()
    stt = STTEngine()

    initial_greeting = "Hello! I am Li's AI voice assistant. How can I help you today?"
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

            is_voice_mode = False

            if user_input.lower() == "voice":
                user_input = stt.listen()
                if not user_input:
                    print("No speech recognized. Returning to text mode.")
                    continue
                is_voice_mode = True

            # Process command
            response = assistant.process_command(user_input)
            print(f"\n[Assistant]: {response}")

            # Speak response ONLY if input was given via voice!
            if is_voice_mode:
                tts.speak(response)

        except KeyboardInterrupt:
            print("\nExiting assistant...")
            sys.exit(0)

if __name__ == "__main__":
    main()
