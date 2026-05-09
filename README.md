# FRIDAY AI 🤖

A multilingual voice AI assistant inspired by Iron Man's FRIDAY.
Built in public in 3 days using 100% free APIs.

## Demo

> "What's the latest news on AI?" → FRIDAY fetches headlines and speaks them back.

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Speech to Text | Sarvam AI (saarika:v2.5) | Free |
| Text to Speech | Sarvam AI (bulbul:v1) | Free |
| LLM Core | Groq API (llama-3.3-70b) | Free |
| Tools | FastMCP | Free |
| Web Server | FastAPI + Uvicorn | Free |
| Public Hosting | Cloudflared | Free |

## Features

- Speak in any Indian language — FRIDAY understands
- Real-time news via NewsAPI
- Tells current time and date
- Remembers conversation context
- Web interface accessible from any browser
- Shareable public URL via Cloudflared

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/lika1510/friday-ai.git
cd friday-ai
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add API keys

Create a `.env` file:
GROQ_API_KEY=your_groq_key
SARVAM_API_KEY=your_sarvam_key
NEWS_API_KEY=your_newsapi_key

Get free keys at:
- console.groq.com
- dashboard.sarvam.ai
- newsapi.org

### 4. Run voice mode

```bash
python main.py
```

Press Enter to speak, Ctrl+C to quit.

### 5. Run web mode

```bash
uvicorn server:app --port 8000
```

Open http://localhost:8000 in your browser.

### 6. Share publicly

```bash
cloudflared tunnel --url http://localhost:8000
```

## Project Structure
friday-ai/
├── main.py        # voice loop entry point
├── server.py      # FastAPI web server
├── llm.py         # Groq LLM + tool calling + memory
├── tools.py       # FastMCP tools (news, time)
├── stt.py         # Sarvam speech-to-text
├── tts.py         # Sarvam text-to-speech
├── recorder.py    # mic audio capture
└── .env           # API keys (never committed)
## Built by

[@lika1510](https://github.com/lika1510) — built in public in 3 days
