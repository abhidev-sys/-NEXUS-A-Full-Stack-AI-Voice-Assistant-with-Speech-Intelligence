import asyncio
import edge_tts
import pyttsx3
import pygame
import os
import threading
from dotenv import dotenv_values

# ---------------- CONFIG ----------------
env = dotenv_values(".env")
AssistantVoice = env.get("AssistantVoice") or "hi-IN-SwaraNeural"

AUDIO_PATH = "backend/data/speech.mp3"

# ---------------- INIT PYGAME ONCE ----------------
pygame.mixer.init()

# ---------------- OFFLINE TTS ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

def offline_tts(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 155)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()


# ---------------- ONLINE TTS ----------------
async def generate_audio(text):
    if os.path.exists(AUDIO_PATH):
        os.remove(AUDIO_PATH)

    communicate = edge_tts.Communicate(
        text=text,
        voice=AssistantVoice,
        rate="+10%"
    )
    await communicate.save(AUDIO_PATH)

# ---------------- SAFE ASYNC RUN ----------------
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        future.result()
    else:
        asyncio.run(coro)

# ---------------- PLAY AUDIO ----------------
def play_audio():
    pygame.mixer.music.load(AUDIO_PATH)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# ---------------- MAIN TTS FUNCTION ----------------
def TextToSpeech(text, func=lambda r=None: True):
    try:
        run_async(generate_audio(text))

        if not os.path.exists(AUDIO_PATH) or os.path.getsize(AUDIO_PATH) == 0:
            raise RuntimeError("Edge TTS failed")

        play_audio()

    except Exception:
        print("⚠ Online TTS failed → Offline mode")
        offline_tts(text)

    finally:
        try:
            func(False)
        except:
            pass

def offline_tts(text):
    def speak():
        engine = pyttsx3.init(driverName="sapi5")
        engine.setProperty("rate", 155)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    t = threading.Thread(target=speak)
    t.start()
    t.join()

# ---------------- TEST MODE ----------------
if __name__ == "__main__":
    while True:
        t = input("Enter your text: ")
        if t.lower() == "exit":
            break
        TextToSpeech(t)
