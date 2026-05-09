from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, base64, requests, tempfile
from dotenv import load_dotenv
load_dotenv()

from llm import chat, clear_history
from tools import tool_handler

app = FastAPI(title="FRIDAY AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Text chat endpoint ──────────────────────────────────────────────
class MessageRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(req: MessageRequest):
    reply = chat(req.message, tool_handler)
    return {"reply": reply}

# ── Voice endpoint: audio in → audio out ───────────────────────────
@app.post("/voice")
async def voice_endpoint(file: UploadFile = File(...)):
    # 1. Save uploaded audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2. Sarvam STT
    with open(tmp_path, "rb") as f:
        stt_res = requests.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={"API-Subscription-Key": os.getenv("SARVAM_API_KEY")},
            files={"file": ("audio.wav", f, "audio/wav")},
            data={"model": "saarika:v2.5", "language_code": "en-IN"}
        )
    os.unlink(tmp_path)

    if stt_res.status_code != 200:
        return JSONResponse({"error": f"STT failed: {stt_res.text}"}, status_code=400)

    transcript = stt_res.json().get("transcript", "")
    print(f"[STT] {transcript}")

    if not transcript.strip():
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    # 3. Groq LLM
    reply_text = chat(transcript, tool_handler)
    print(f"[LLM] {reply_text}")

    # 4. Sarvam TTS
    tts_res = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={"API-Subscription-Key": os.getenv("SARVAM_API_KEY")},
        json={
            "inputs": [reply_text[:500]],
            "target_language_code": "en-IN",
            "model": "bulbul:v2",
            "speaker": "anushka",
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5
        }
    )

    if tts_res.status_code != 200:
        return JSONResponse({"error": f"TTS failed: {tts_res.text}"}, status_code=400)

    audio_b64 = tts_res.json()["audios"][0]

    return {
        "transcript": transcript,
        "reply": reply_text,
        "audio": audio_b64  # base64 wav
    }

@app.post("/reset")
def reset():
    clear_history()
    return {"status": "cleared"}

# ── Frontend UI ─────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>FRIDAY AI</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #060606;
    color: #fff;
    font-family: -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 24px;
  }
  h1 { font-size: 2.5rem; font-weight: 700; color: #00ff88; letter-spacing: 4px; margin-bottom: 8px; }
  .subtitle { color: #555; font-size: 14px; margin-bottom: 48px; letter-spacing: 2px; }

  /* orb */
  .orb-wrap { position: relative; width: 160px; height: 160px; margin-bottom: 40px; cursor: pointer; }
  .orb {
    width: 160px; height: 160px; border-radius: 50%;
    background: radial-gradient(circle at 40% 35%, #1aff88, #0a4a2a);
    box-shadow: 0 0 40px #00ff8844;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex; align-items: center; justify-content: center;
    font-size: 48px;
  }
  .orb:hover { transform: scale(1.05); box-shadow: 0 0 60px #00ff8866; }
  .orb.listening { animation: pulse 1s infinite; box-shadow: 0 0 80px #00ff88aa; }
  .orb.thinking { animation: spin-glow 2s infinite; }
  .orb.speaking { animation: wave 0.6s infinite alternate; }
  @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
  @keyframes spin-glow { 0%,100%{box-shadow:0 0 40px #00ff8855} 50%{box-shadow:0 0 80px #00ff88cc} }
  @keyframes wave { from{transform:scale(1)} to{transform:scale(1.06)} }

  .status { font-size: 14px; color: #00ff88; letter-spacing: 1px; min-height: 20px; margin-bottom: 32px; }

  /* transcript + reply */
  .bubble-wrap { width: 100%; max-width: 520px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px; min-height: 80px; }
  .bubble { padding: 14px 18px; border-radius: 16px; font-size: 15px; line-height: 1.6; max-width: 90%; }
  .bubble.user { background: #1a1a1a; border: 1px solid #333; align-self: flex-end; color: #ccc; }
  .bubble.friday { background: #0a2a1a; border: 1px solid #00ff8833; align-self: flex-start; color: #00ff88; }

  /* text input row */
  .input-row { display: flex; gap: 8px; width: 100%; max-width: 520px; margin-bottom: 16px; }
  input[type=text] {
    flex: 1; padding: 12px 16px; background: #111; border: 1px solid #333;
    border-radius: 12px; color: #fff; font-size: 15px; outline: none;
  }
  input[type=text]:focus { border-color: #00ff8866; }
  .send-btn {
    padding: 12px 20px; background: #00ff88; color: #000; border: none;
    border-radius: 12px; font-weight: 600; cursor: pointer; font-size: 15px;
  }
  .reset-btn {
    font-size: 12px; color: #444; background: none; border: none;
    cursor: pointer; letter-spacing: 1px; text-decoration: underline;
  }
  .reset-btn:hover { color: #888; }
  .hint { font-size: 12px; color: #444; margin-top: 4px; }
</style>
</head>
<body>
  <h1>FRIDAY</h1>
  <div class="subtitle">PERSONAL AI ASSISTANT</div>

  <div class="orb-wrap" onclick="toggleVoice()">
    <div class="orb" id="orb">🎙️</div>
  </div>
  <div class="status" id="status">Tap the orb to speak</div>

  <div class="bubble-wrap" id="bubbles"></div>

  <div class="input-row">
    <input type="text" id="textInput" placeholder="Or type your message..." onkeydown="if(event.key==='Enter') sendText()"/>
    <button class="send-btn" onclick="sendText()">Send</button>
  </div>

  <button class="reset-btn" onclick="resetChat()">reset conversation</button>
  <div class="hint" style="margin-top:12px">Speak in English, Hindi, Tamil, Telugu or any Indian language</div>

<script>
let mediaRecorder, audioChunks = [], isRecording = false;

const orb = document.getElementById('orb');
const status = document.getElementById('status');
const bubbles = document.getElementById('bubbles');

function setOrb(state, icon, msg) {
  orb.className = 'orb ' + state;
  orb.textContent = icon;
  status.textContent = msg;
}

function addBubble(text, who) {
  const d = document.createElement('div');
  d.className = 'bubble ' + who;
  d.textContent = text;
  bubbles.appendChild(d);
  bubbles.scrollTop = bubbles.scrollHeight;
}

async function toggleVoice() {
  if (isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    setOrb('thinking', '⏳', 'FRIDAY is thinking...');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, { type: 'audio/wav' });
      await sendAudio(blob);
    };
    mediaRecorder.start();
    isRecording = true;
    setOrb('listening', '🔴', 'Listening... tap again to stop');
  } catch(e) {
    status.textContent = 'Microphone access denied';
  }
}

async function sendAudio(blob) {
  const form = new FormData();
  form.append('file', blob, 'audio.wav');
  try {
    const res = await fetch('/voice', { method: 'POST', body: form });
    const data = await res.json();
    if (data.error) { setOrb('', '🎙️', data.error); return; }

    addBubble(data.transcript, 'user');
    addBubble(data.reply, 'friday');
    setOrb('speaking', '🔊', 'FRIDAY is speaking...');

    // play audio
    const audioData = atob(data.audio);
    const arr = new Uint8Array(audioData.length);
    for (let i = 0; i < audioData.length; i++) arr[i] = audioData.charCodeAt(i);
    const audioBlob = new Blob([arr], { type: 'audio/wav' });
    const url = URL.createObjectURL(audioBlob);
    const audio = new Audio(url);
    audio.onended = () => setOrb('', '🎙️', 'Tap the orb to speak');
    audio.play();
  } catch(e) {
    setOrb('', '🎙️', 'Something went wrong, try again');
  }
}

async function sendText() {
  const msg = document.getElementById('textInput').value.trim();
  if (!msg) return;
  document.getElementById('textInput').value = '';
  addBubble(msg, 'user');
  status.textContent = 'FRIDAY is thinking...';
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg })
  });
  const data = await res.json();
  addBubble(data.reply, 'friday');
  status.textContent = 'Tap the orb to speak';
}

async function resetChat() {
  await fetch('/reset', { method: 'POST' });
  bubbles.innerHTML = '';
  status.textContent = 'Conversation reset';
  setTimeout(() => status.textContent = 'Tap the orb to speak', 1500);
}
</script>
</body>
</html>"""