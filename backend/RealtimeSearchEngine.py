from ddgs import DDGS
from groq import Groq
import datetime
import time
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


# -------- RETRY / BACKOFF HELPER ----------
def retry_with_backoff(func, *args, max_retries=3, base_delay=1, **kwargs):
    """Calls func(*args, **kwargs). If it raises, waits and tries again,
    doubling the wait each time (1s, 2s, 4s), instead of failing on the
    first network hiccup."""
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                print(f"[RETRY] Attempt {attempt}/{max_retries} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
    raise last_exception


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
        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=10))

        raw = retry_with_backoff(_search, max_retries=2, base_delay=1)
    except Exception:
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

def _call_groq(messages):
    """Runs the Groq streaming completion and collects it into a single
    string. Wrapped by retry_with_backoff below — if the connection
    drops mid-stream, we cleanly retry the whole request rather than
    returning a half-finished answer."""
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

    return answer


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

    # 4. AI COMPLETION (SCOUT MODEL) — now with automatic retry
    try:
        answer = retry_with_backoff(_call_groq, messages)
    except Exception as e:
        return f"Sorry, I couldn't reach the search engine right now ({e}). Please try again."

    return answer.strip()


# MAIN LOOP

if __name__ == "__main__":
    while True:
        query = input("Enter your query: ")
        response = RealtimeSearchEngine(query)
        print("\n" + response + "\n")