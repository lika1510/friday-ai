import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are FRIDAY, a sharp, witty and helpful voice AI assistant — inspired by Iron Man's FRIDAY.
Keep your replies short and conversational — you are speaking out loud, not writing an essay.
Never use bullet points or markdown. Speak naturally like a human assistant would.
Always address the user in a friendly, confident tone."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Get the latest news headlines on any topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search news for, e.g. AI, cricket, politics"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

conversation_history = []
MAX_HISTORY = 10  # keep last 10 exchanges to avoid token overflow

def chat(user_text: str, tool_handler) -> str:
    global conversation_history

    conversation_history.append({
        "role": "user",
        "content": user_text
    })

    # trim history if too long
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=300
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"[LLM] Calling tool: {tc.function.name} with {args}")
                result = tool_handler(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

            final = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=300
            )
            reply = final.choices[0].message.content
        else:
            reply = msg.content

    except Exception as e:
        print(f"[LLM] Error: {e}")
        reply = "I ran into an issue. Could you try asking that again?"

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply

def clear_history():
    global conversation_history
    conversation_history = []
    print("[LLM] Conversation history cleared.")