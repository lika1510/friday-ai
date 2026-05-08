import requests
import os
from dotenv import load_dotenv
load_dotenv()

def transcribe(audio_path: str, language: str = "en-IN") -> str:
    print(f"[STT] Transcribing {audio_path}...")
    with open(audio_path, "rb") as f:
        res = requests.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={
                "API-Subscription-Key": os.getenv("SARVAM_API_KEY")
            },
            files={"file": ("audio.wav", f, "audio/wav")},
            data={
                "model": "saarika:v2.5",
                "language_code": language
            }
        )

    if res.status_code != 200:
        print(f"[STT] Error: {res.status_code} — {res.text}")
        return ""

    transcript = res.json().get("transcript", "")
    print(f"[STT] You said: {transcript}")
    return transcript

if __name__ == "__main__":
    from recorder import record_audio
    audio_path = record_audio()
    if audio_path:
        text = transcribe(audio_path)
        print("\nFinal transcript:", text)
