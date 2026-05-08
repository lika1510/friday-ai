import sounddevice as sd
import soundfile as sf
import numpy as np
from dotenv import load_dotenv
load_dotenv()

def record_audio(filename="input.wav", samplerate=16000):
    print("\n[FRIDAY] Listening... speak now. Press Enter to stop.")
    frames = []

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    with sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        callback=callback
    ):
        input()

    if not frames:
        print("[FRIDAY] No audio captured.")
        return None

    audio = np.concatenate(frames, axis=0)
    sf.write(filename, audio, samplerate)
    print(f"[FRIDAY] Audio saved to {filename}")
    return filename

if __name__ == "__main__":
    path = record_audio()
    if path:
        print("Success! File saved:", path)