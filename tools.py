import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

async def get_latest_news(topic: str) -> str:
    print(f"[TOOL] Fetching news for: {topic}")
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": topic,
                "apiKey": os.getenv("NEWS_API_KEY"),
                "pageSize": 5,
                "sortBy": "publishedAt",
                "language": "en"
            }
        )
    data = r.json()
    articles = data.get("articles", [])
    if not articles:
        return f"No news found for {topic}."
    headlines = "\n".join(
        f"{i+1}. {a['title']} — {a['source']['name']}"
        for i, a in enumerate(articles)
    )
    return f"Latest news on {topic}:\n{headlines}"

def get_time() -> str:
    now = datetime.now()
    return now.strftime("It's %A, %d %B %Y, %I:%M %p")

def tool_handler(name: str, args: dict) -> str:
    if name == "get_latest_news":
        return asyncio.run(get_latest_news(**args))
    if name == "get_time":
        return get_time()
    return f"Unknown tool: {name}"

if __name__ == "__main__":
    print(get_time())
    print()
    result = asyncio.run(get_latest_news("artificial intelligence"))
    print(result)