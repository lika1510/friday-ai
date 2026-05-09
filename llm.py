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

def chat(user_text: str, tool_handler) -> str:
    conversation_history.append({
        "role": "user",
        "content": user_text
    })

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
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
            messages=messages
        )
        reply = final.choices[0].message.content
    else:
        reply = msg.content

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply

if __name__ == "__main__":
    def dummy_tool(name, args):
        return "Tool result: test"

    print("Testing Groq LLM...")
    reply = chat("Hey FRIDAY, introduce yourself!", dummy_tool)
    print("FRIDAY:", reply)

    reply2 = chat("What can you help me with?", dummy_tool)
    print("FRIDAY:", reply2)