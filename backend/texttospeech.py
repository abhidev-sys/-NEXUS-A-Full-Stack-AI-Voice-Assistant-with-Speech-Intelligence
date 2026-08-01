import asyncio
import edge_tts
import pyttsx3
import pygame
import threading
from pathlib import Path
from dotenv import dotenv_values

# ---------------- CONFIG ----------------

env = dotenv_values(".env")

AssistantVoice = env.get("AssistantVoice", "en-US-GuyNeural")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

AUDIO_PATH = DATA_DIR / "speech.mp3"

print(f"Using Voice : {AssistantVoice}")

# ---------------- INIT ----------------

pygame.mixer.init()

engine = pyttsx3.init(driverName="sapi5")
engine.setProperty("rate", 155)
engine.setProperty("volume", 1.0)

# ---------------- OFFLINE TTS ----------------

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


# ---------------- ONLINE TTS ----------------

async def generate_audio(text):

    # Purani file ko release karo
    pygame.mixer.music.stop()

    try:
        pygame.mixer.music.unload()
    except:
        pass

    if AUDIO_PATH.exists():
        try:
            AUDIO_PATH.unlink()
        except PermissionError:
            pass

    communicate = edge_tts.Communicate(
        text=text,
        voice=AssistantVoice,
        rate="+10%"
    )

    await communicate.save(str(AUDIO_PATH))

# ---------------- ASYNC ----------------

def run_async(coro):
    asyncio.run(coro)


# ---------------- PLAY AUDIO ----------------

def play_audio():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()      # <-- bahut important

    pygame.mixer.music.load(str(AUDIO_PATH))
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()      # <-- file release


# ---------------- MAIN ----------------

def TextToSpeech(text, func=lambda _: None):

    try:

        run_async(generate_audio(text))

        if not AUDIO_PATH.exists():
            raise FileNotFoundError("speech.mp3 not generated")

        if AUDIO_PATH.stat().st_size == 0:
            raise RuntimeError("Generated file is empty")

        play_audio()

    except Exception as e:

        print("Edge TTS Error :", e)
        print("Switching to Offline Voice...")

        offline_tts(text)

    finally:
        func(False)


# ---------------- TEST ----------------

if __name__ == "__main__":

    while True:

        text = input("Enter Text : ")

        if text.lower() == "exit":
            break

        TextToSpeech(text)