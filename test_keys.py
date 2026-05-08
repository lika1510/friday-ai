import os
from dotenv import load_dotenv
load_dotenv()

print("Testing Groq...")
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
r = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "just say: GROQ OK"}]
)
print(r.choices[0].message.content)

print("\nTesting NewsAPI...")
import requests
r2 = requests.get(
    "https://newsapi.org/v2/top-headlines",
    params={"country": "in", "apiKey": os.getenv("NEWS_API_KEY"), "pageSize": 1}
)
data = r2.json()
print("NewsAPI status:", data.get("status"))

print("\nAll done!")