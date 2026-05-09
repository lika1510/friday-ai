from dotenv import load_dotenv
load_dotenv()

from recorder import record_audio
from stt import transcribe
from tts import speak
from llm import chat
from tools import tool_handler

def main():
    print("=" * 40)
    print("  FRIDAY is online. How can I help?")
    print("  Press Enter to speak. Ctrl+C to quit.")
    print("=" * 40)

    speak("FRIDAY online. How can I help you today?")

    while True:
        try:
            audio_path = record_audio()
            if not audio_path:
                continue

            user_text = transcribe(audio_path)
            if not user_text.strip():
                print("[FRIDAY] Didn't catch that, try again.")
                speak("Sorry, I didn't catch that. Can you say it again?")
                continue

            print(f"\nYou: {user_text}")

            response = chat(user_text, tool_handler)
            print(f"FRIDAY: {response}\n")

            speak(response)

        except KeyboardInterrupt:
            print("\n[FRIDAY] Shutting down. Goodbye!")
            speak("Goodbye! See you soon.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            speak("Something went wrong. Please try again.")

if __name__ == "__main__":
    main()