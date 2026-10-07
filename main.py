import sys
from src.core.assistant import AssistantOrchestrator

def main():
    print("=" * 65)
    print("🎙️  Li's AI Virtual Assistant (Personal Intelligence Engine)")
    print("=" * 65)
    print("Type your message, or type 'voice' to activate microphone mode.")
    print("Type 'exit' or 'quit' to exit.\n")

    assistant = AssistantOrchestrator()

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            voice_mode = False
            if user_input.lower() == "voice":
                voice_mode = True
                user_input = assistant.stt.listen()
                if not user_input:
                    print("[Voice] No speech detected. Please try again.")
                    continue

            result = assistant.process_query(user_input, voice_mode=voice_mode)
            print(f"\nAssistant > {result['response']}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error] {e}\n")

if __name__ == "__main__":
    main()
