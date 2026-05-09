# FRIDAY AI 🤖

A multilingual voice AI assistant inspired by Iron Man's FRIDAY.
Built in public in 3 days using 100% free APIs.

## 🌐 Live Demo
**Try FRIDAY here → https://friday-ai-qn1h.onrender.com**

Tap the glowing orb, speak anything, FRIDAY listens and speaks back!

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Speech to Text | Sarvam AI (saarika:v2.5) | Free |
| Text to Speech | Sarvam AI (bulbul:v2) | Free |
| LLM Core | Groq API (llama-3.3-70b) | Free |
| News Tool | NewsAPI | Free |
| Web Server | FastAPI + Uvicorn | Free |
| Hosting | Render | Free |

## Features
- Voice input via browser microphone
- Speaks back in natural Indian English
- Real-time news on any topic
- Tells current time and date
- Full conversation memory
- Works on mobile browser too
- Live 24/7 at https://friday-ai-qn1h.onrender.com

## Setup locally

### 1. Clone
```bash
git clone https://github.com/lika1510/friday-ai.git
cd friday-ai
```

### 2. Virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. API keys — create .env file
GROQ_API_KEY=your_groq_key
SARVAM_API_KEY=your_sarvam_key
NEWS_API_KEY=your_newsapi_key
Get free keys at:
- console.groq.com
- dashboard.sarvam.ai
- newsapi.org

### 4. Run locally
```bash
uvicorn server:app --port 8000 --reload
```
Open http://localhost:8000 — tap the orb to speak!

## Project Structure
friday-ai/
├── main.py        # local voice loop
├── server.py      # FastAPI web server + voice UI
├── llm.py         # Groq LLM + tool calling + memory
├── tools.py       # news and time tools
├── stt.py         # Sarvam speech-to-text
├── tts.py         # Sarvam text-to-speech
├── recorder.py    # mic recording
└── .env           # API keys (never committed)
## Built by
[@lika1510](https://github.com/lika1510) — built in public in 3 days
