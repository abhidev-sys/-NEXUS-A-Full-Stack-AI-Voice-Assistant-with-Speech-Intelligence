import os
import json
import time
from dotenv import load_dotenv
from cohere import Client
from rich import print

# -------- LOAD .env CORRECTLY --------
env_path = os.path.join(os.path.dirname(__file__), ".env")

print("ENV PATH:", env_path)

load_dotenv(env_path)

cohereAPIKEY = os.getenv("cohereAPIKEY")
print("Loaded KEY:", cohereAPIKEY)

# -------- CREATE CLIENT ----------
co = Client(api_key=cohereAPIKEY)

# -------- TASK TYPES -------------
func = [
    "exit",
    "general",
    "realtime",
    "open",
    "close",
    "play",
    "generate image",
    "generate the image",
    "generate",
    "system",
    "content",
    "google search",
    "search google",
    "youtube search",
    "search youtube",
    "reminder"
]

# Canonical categories used by the NEW structured-JSON path.
VALID_CATEGORIES = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# -------- OLD TEXT-STYLE PREAMBLE (kept — used only by the fallback) ------
legacy_preamble = """You are a Decision-Making Model. Classify only into these categories:

general
realtime
open
close
play
generate image
system
content
google search
youtube search
reminder
exit
r̥
Rules:
- Respond ONLY as:  category + space + the query
- Do NOT answer the query.
- Do NOT add extra words.
- For image creation: start with "generate image"
- For system tasks like mute, unmute, volume up: start with "system"
- For opening apps: start with "open"
- For searches: start with "google search" or "youtube search"
- If user says bye: respond with "exit"
"""

# -------- NEW JSON PREAMBLE (primary path) ----------
json_preamble = """You are a Decision-Making Model. Classify the user's message into
one or more tasks.

Respond ONLY with valid JSON — no extra words, no markdown fences — in
exactly this shape:

{"tasks": [{"category": "<category>", "text": "<relevant part of the query>"}]}

Valid categories (use exactly one of these per task):
exit, general, realtime, open, close, play, generate image, system,
content, google search, youtube search, reminder

Rules:
- Do NOT answer the query itself — only classify it.
- If the sentence contains multiple actions, add one object per action
  to the "tasks" list, in the order they were said.
- For opening apps -> category "open", text = the app name.
- For closing apps -> category "close", text = the app name.
- For system actions like mute/unmute/volume -> category "system".
- For opening a browser search results page -> category "google search"
  or "youtube search".
- For anything that needs a real, up-to-date answer that could change
  over time — stock/crypto prices, live scores, current events, news,
  weather, "who is the current ___" -> category "realtime".
- If the user is saying goodbye -> category "exit".
- Anything else conversational (opinions, jokes, general knowledge that
  doesn't change over time) -> category "general".
"""

# -------- FEW-SHOT EXAMPLES (kept exactly as before, used by fallback) ---
ChatHistory = [
    {"role": "User", "message": "how are you"},
    {"role": "Chatbot", "message": "general how are you"},
    {"role": "User", "message": "do you like pizza"},
    {"role": "Chatbot", "message": "general do you like pizza"},
    {"role": "User", "message": "open chrome , and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome , general tell me about mahatma gandhi"},
]

# -------- REAL, GROWING CONVERSATION HISTORY (Step 1 fix, unchanged) -----
messages = []
MAX_HISTORY_ENTRIES = 40


# -------- RETRY / BACKOFF HELPER ----------
def retry_with_backoff(func, *args, max_retries=3, base_delay=1, **kwargs):
    """Calls func(*args, **kwargs). If it raises, waits and tries again,
    doubling the wait each time (1s, 2s, 4s). After max_retries failed
    attempts, re-raises the last error so the caller's own error
    handling (e.g. the JSON->legacy fallback, or FirstThread's
    try/except) still gets a chance to react."""
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


def _trim_history():
    global messages
    if len(messages) > MAX_HISTORY_ENTRIES:
        messages = messages[len(messages) - MAX_HISTORY_ENTRIES:]


def _record_exchange(prompt, temp):
    messages.append({"role": "User", "message": prompt})
    messages.append({"role": "Chatbot", "message": ", ".join(temp)})
    _trim_history()


def _legacy_text_parse(prompt: str):
    """Old behaviour, kept as a safety net. Only used if the JSON path
    fails for any reason (older cohere SDK without response_format
    support, an API error, or the model returning invalid JSON)."""

    def _call():
        return co.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            temperature=0.2,
            chat_history=ChatHistory + messages,
            preamble=legacy_preamble
        )

    response = retry_with_backoff(_call)

    clean = response.text.replace("\n", "").strip()
    parts = [i.strip() for i in clean.split(",")]

    temp = []
    for task in parts:
        for f in func:
            if task.lower().startswith(f):
                temp.append(task)

    if len(temp) == 0:
        temp = ["general " + prompt]

    return temp


def _json_parse(prompt: str):
    """New, more reliable path: ask the model for structured JSON
    instead of a free-text 'category query' line."""

    def _call():
        return co.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            temperature=0.2,
            chat_history=ChatHistory + messages,
            preamble=json_preamble,
            response_format={"type": "json_object"},
        )

    response = retry_with_backoff(_call)

    data = json.loads(response.text)
    tasks = data.get("tasks", [])

    temp = []
    for t in tasks:
        category = str(t.get("category", "")).strip().lower()
        text = str(t.get("text", "")).strip()
        if category in VALID_CATEGORIES and text:
            temp.append(f"{category} {text}")

    if not temp:
        temp = ["general " + prompt]

    return temp


# -------- FIRST LAYER DMM ----------
def FirstLayerDMM(prompt: str = "test"):
    try:
        temp = _json_parse(prompt)
    except Exception as e:
        # response_format not supported by this SDK version, API hiccup,
        # or the model didn't return valid JSON -> fall back safely
        # instead of crashing the whole assistant.
        print("[WARN] Structured JSON classification failed, using fallback:", e)
        temp = _legacy_text_parse(prompt)

    _record_exchange(prompt, temp)
    return temp


if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>>")))