from ddgs import DDGS
from groq import Groq
import datetime
from dotenv import dotenv_values
from pathlib import Path
from json import load, dump


# LOAD THE ENV  FILE FOR AN API
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
env = dotenv_values(ENV_PATH)


USERNAME = env.get("Username")
ASSISTANT = env.get("Assistantname")
API_KEY = env.get("GROQ_API_KEY")

client = Groq(api_key=API_KEY)
# TIME FUNCTION
def GetTime():
    now = datetime.datetime.now()
    return now.strftime("%A, %d %B %Y, %I:%M:%S %p")

def GetDate():
    now = datetime.datetime.now()
    return now.strftime("%d %B %Y")

# FILTERED REALTIME SEARCH
def GoogleSearch(query):
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=10))
    except:
        return "[start]\nNo results.\n[end]"

    if not raw:
        return "[start]\nNo results.\n[end]"

    # Filter by relevance
    q_words = query.lower().split()
    filtered = []

    for item in raw:
        title = (item.get("title") or "").lower()
        body = (item.get("body") or "").lower()

        if any(word in title or word in body for word in q_words):
            filtered.append(item)

    if not filtered:
        filtered = raw[:3]

    out = "[start]\n"
    for item in filtered:
        out += f"Title: {item.get('title')}\n"
        out += f"Description: {item.get('body')}\n\n"
    out += "[end]"

    return out



SYSTEM_PROMPT = f"""
You are {ASSISTANT}, created by {USERNAME}.
You are a REALTIME AI ASSISTANT.
Strict Rules:
1. Use ONLY realtime data inside [start] and [end].
2. DO NOT use offline or outdated knowledge.
3. DO NOT output <think> or reasoning.
4. Answer clearly, accurately, professionally.
"""

# REALTIME JARVIS ENGINE

def RealtimeSearchEngine(prompt):

    # 1. TIME & DATE HANDLING
    if "time" in prompt.lower():
        return f"The current time is: {GetTime()}"

    if "date" in prompt.lower():
        return f"Today's date is: {GetDate()}"

    # 2. GET REALTIME SEARCH DATA
    search_data = GoogleSearch(prompt)

    # 3. BUILD AI MESSAGE STACK
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": "Use ONLY the data provided below."},
        {"role": "user", "content": f"REALTIME WEB DATA:\n{search_data}\n\nQUESTION: {prompt}"}
    ]

    # 4. AI COMPLETION (SCOUT MODEL)
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=0.2,  
        stream=True
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    return answer.strip()


# MAIN LOOP

if __name__ == "__main__":
    while True:
        query = input("Enter your query: ")
        response = RealtimeSearchEngine(query)
        print("\n" + response + "\n")
