import os
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


messages = []

# -------- PREAMBLE -------------
preamble="""You are a Decision-Making Model. Classify only into these categories:

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

# -------- CHAT HISTORY (FIXED FORMAT) -----------
ChatHistory = [
    {"role": "User", "message": "how are you"},
    {"role": "Chatbot", "message": "general how are you"},
    {"role": "User", "message": "do you like pizza"},
    {"role": "Chatbot", "message": "general do you like pizza"},
    {"role": "User", "message": "open chrome , and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome , general tell me about mahatma gandhi"},
]


# -------- FIRST LAYER DMM ----------
# -------- FIRST LAYER DMM ----------
def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "message": prompt})

    # Use chat() instead of chat_stream() for Cohere v5.x
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        temperature=0.2,
        chat_history=ChatHistory,
        preamble=preamble
    )

     # Clean text
    clean = response.text.replace("\n", "").strip()

    # Split multiple tasks by comma
    parts = [i.strip() for i in clean.split(",")]

    temp = []

    # Match each part with defined functions
    for task in parts:
        for f in func:
            if task.lower().startswith(f):
                temp.append(task)

    # If nothing matches, default to general
    if len(temp) == 0:
        return ["general " + prompt]

    return temp


if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>>")))