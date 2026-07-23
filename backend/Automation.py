from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from pathlib import Path
from dotenv import dotenv_values

# ---------------- ENV SETUP ----------------
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
env_vars = dotenv_values(ENV_PATH)
GroqAPIKey = env_vars.get("GROQ_API_KEY")

client = Groq(api_key=GroqAPIKey)


Professional_response = ["your  satisfaction is my top priority; feel to reach you if there's is anything else i can helo you with,"
                         "iam at your service for any additional question or support you may need-don't hesitate to ask"
                         ]


# Chat memory list
messages = []

SystemChatBot = [
    {
        "role": "system",
        "content": "You are a professional content writer. Write clean and formal letters."
    }
]


#----------------GOOGLE SEARCH---------------
def GoogleSearch(query): 
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        print(f"[green]Google search opened for:[/green] {query}")
        return True
    except Exception as e:
        print("[red]Google Search Error:[/red]", e)
        return False


    
# ---------------- CONTENT GENERATION ----------------
def ContentWriterAI(prompt):
    messages.append({"role": "user", "content": prompt})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1.0,
            stream=False
        )

        content = completion.choices[0].message.content   # FIXED LINE
        content = content.replace("</s>", "")

        messages.append({"role": "assistant", "content": content})

        print("\n[AI OUTPUT]\n")
        print(content)

        return content

    except Exception as e: 
        print("Groq generation error:", e)
        return f"[Generation failed: {e}]"


def Content(Topic):
    Topic = Topic.strip()

    print(f"[cyan]Generating content for:[/cyan] {Topic}")

    content_text = ContentWriterAI(Topic)

    save_path = BASE_DIR / "Data" / f"{Topic.lower().replace(' ','')}.txt"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content_text)

    print(f"[green]Saved to:[/green] {save_path}")

    subprocess.Popen(["notepad.exe", str(save_path)])

    return True
# ---------------- YOUTUBE + GOOGLE ----------------
def YoutubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True



def PlayYoutube(query):
    playonyt(query)
    return True



# ---------------- OPEN APP ----------------
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        pass

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = sess.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
        return None
    def extract_links(html):
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", {"jsname": "UWckNb"})
        return [l.get("href") for l in links]

    html = search_google(app)
    if html:
        links = extract_links(html)
        if links:
            webopen(links[0])
            return True
        else:
            print("No links found opeing google instead")
            webbrowser.open(f"https://www.google.com/search?q={app}")
            return True
        
        

#-------------- CLOSE APP ----------------
def ClosedApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

    
# ---------------- SYSTEM CONTROL -------------
def System(command):
    command = command.lower().strip()
    print("[SYSTEM CHECK] ->", command)

    cmds = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
        "task manager": lambda: keyboard.press_and_release("ctrl+shift+esc"),
        "screenshot": lambda: keyboard.press_and_release("win+print_screen"),
    }

    for key, action in cmds.items():
        if key in command:
            print("[SYSTEM MATCHED] ->", key)
            action()
            return True

    return False

async def TranslateAndExecute(commands: list[str]):
    tasks = []

    for cmd in commands:
        cmd = cmd.lower().strip()
        print("CMD RECIEVED ->" , cmd)

        # 1️⃣ SYSTEM COMMANDS FIRST
        if System(cmd):
            continue

        # 2️⃣ CONTENT
        if cmd.startswith("content "):
            tasks.append(asyncio.to_thread(Content, cmd.replace("content ", "")))

        # 3️⃣ OPEN APP
        elif cmd.startswith("open "):
            tasks.append(asyncio.to_thread(OpenApp, cmd.replace("open ", "")))

        # 4️⃣ CLOSE APP
        elif cmd.startswith("close "):
            tasks.append(asyncio.to_thread(ClosedApp, cmd.replace("close ", "")))

        # 5️⃣ PLAY
        elif cmd.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd.replace("play ", "")))

        # 6️⃣ YOUTUBE SEARCH
        elif cmd.startswith("youtube search "):
            tasks.append(asyncio.to_thread(YoutubeSearch, cmd.replace("youtube search ", "")))

        # 7️⃣ GOOGLE SEARCH
        elif cmd.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd.replace("google search ", "")))

        else:
            print(f"[red]Unknown command:[/red] {cmd}")

    results = await asyncio.gather(*tasks)
    print("[green]Automation results:[/green]", results)
    return results



# ---------------- MAIN TEST ----------------
if __name__ == "__main__":
    print("Running Automations")
    
