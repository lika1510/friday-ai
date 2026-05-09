from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from llm import chat, clear_history
from tools import tool_handler

app = FastAPI(title="FRIDAY AI")

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    reply: str

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>FRIDAY AI</title>
        <style>
            body { font-family: sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; background: #0a0a0a; color: #fff; }
            h1 { color: #00ff88; }
            input { width: 100%; padding: 12px; font-size: 16px; border-radius: 8px; border: 1px solid #333; background: #1a1a1a; color: #fff; margin-bottom: 10px; }
            button { padding: 12px 24px; background: #00ff88; color: #000; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
            #response { margin-top: 24px; padding: 16px; background: #1a1a1a; border-radius: 8px; min-height: 60px; line-height: 1.6; }
            .label { font-size: 12px; color: #888; margin-bottom: 6px; }
        </style>
    </head>
    <body>
        <h1>FRIDAY</h1>
        <p style="color:#888">Your personal AI assistant</p>
        <div class="label">Ask FRIDAY anything</div>
        <input type="text" id="msg" placeholder="What's the latest news on AI?" onkeydown="if(event.key==='Enter') send()"/>
        <button onclick="send()">Ask</button>
        <div class="label" style="margin-top:20px">Response</div>
        <div id="response">Waiting for your question...</div>
        <script>
            async function send() {
                const msg = document.getElementById('msg').value;
                if (!msg) return;
                document.getElementById('response').innerText = 'Thinking...';
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                document.getElementById('response').innerText = data.reply;
                document.getElementById('msg').value = '';
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=MessageResponse)
def chat_endpoint(req: MessageRequest):
    reply = chat(req.message, tool_handler)
    return MessageResponse(reply=reply)

@app.post("/reset")
def reset():
    clear_history()
    return {"status": "conversation cleared"}

@app.get("/health")
def health():
    return {"status": "FRIDAY is online"}