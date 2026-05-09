import requests
import os
import base64
import sounddevice as sd
import soundfile as sf
import io
from dotenv import load_dotenv
load_dotenv()

def speak(text: str, language: str = "en-IN"):
    print(f"[TTS] Speaking: {text}")
    res = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={
            "API-Subscription-Key": os.getenv("SARVAM_API_KEY")
        },
        json={
            "inputs": [text],
            "target_language_code": language,
            "model": "bulbul:v3",
            "speaker": "anushka"
        }
    )

    if res.status_code != 200:
        print(f"[TTS] Error: {res.status_code} — {res.text}")
        return

    audio_b64 = res.json()["audios"][0]
    audio_bytes = base64.b64decode(audio_b64)
    data, sr = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, sr)
    sd.wait()
    print("[TTS] Done speaking.")

if __name__ == "__main__":
    speak("Hello! I am FRIDAY, your personal AI assistant. How can I help you today?")