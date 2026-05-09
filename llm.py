import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = SYSTEM_PROMPT = """You are FRIDAY, a sharp, witty and highly intelligent AI assistant inspired by Iron Man's FRIDAY.
You have deep knowledge across all topics — science, technology, finance, history, culture, coding, medicine, and more.
You can explain complex topics clearly, answer analytical questions, help with coding, writing, math, and creative tasks.

For voice responses: keep it conversational, no bullet points, no markdown, speak naturally.
For detailed questions asked via text: give thorough, intelligent answers.

When asked about real-time data like live stock prices or today's scores, use your news tool to fetch latest info.
When asked general knowledge questions, answer from your own intelligence — don't say you can't help.

Always be confident, friendly, and genuinely useful like a brilliant personal assistant."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_latest_news",
            "description": "Get latest news headlines on any topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search news for"}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current date and time",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# only store simple user/assistant text — no tool messages in history
conversation_history = []
MAX_HISTORY = 10

def chat(user_text: str, tool_handler) -> str:
    global conversation_history

    # build messages fresh each time
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += conversation_history
    messages.append({"role": "user", "content": user_text})

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
            # build a fresh messages list for the tool round-trip
            tool_messages = messages.copy()
            tool_messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"[LLM] Tool: {tc.function.name} args: {args}")
                try:
                    result = tool_handler(tc.function.name, args)
                except Exception as te:
                    result = f"Tool error: {str(te)}"
                print(f"[TOOL] Result preview: {str(result)[:80]}")
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                })

            final = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=tool_messages,
                max_tokens=300
            )
            reply = final.choices[0].message.content

        else:
            reply = msg.content

    except Exception as e:
        print(f"[LLM] Error: {e}")
        return "I ran into an issue. Could you try asking that again?"

    # only save clean user/assistant pairs in history
    conversation_history.append({"role": "user", "content": user_text})
    conversation_history.append({"role": "assistant", "content": reply})

    # trim history
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]

    return reply

def clear_history():
    global conversation_history
    conversation_history = []
    print("[LLM] History cleared.")
