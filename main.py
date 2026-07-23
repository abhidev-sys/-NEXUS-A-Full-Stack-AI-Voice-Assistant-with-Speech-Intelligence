from frontend.GUI import(
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus,
)
from backend.model import FirstLayerDMM   # thiis for the imporitopmn for the import luiavbavry
from backend.RealtimeSearchEngine import RealtimeSearchEngine
from backend.Automation import TranslateAndExecute
from backend.speechtotext import SpeechRecognition
from backend.chatbot import Chatbot
from backend.texttospeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import time
import subprocess
import threading 
import json
import os 
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import sys

MIC_BUSY =  False


# here we trying to load the files for text
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "backend" / ".env"
env_vars = dotenv_values(ENV_PATH)


env_vars = dotenv_values(".env")
Username = env_vars.get("Username") or "User"
Assistantname = env_vars.get("Assistantname") or "Assistant"
DeafaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}.  I am doing well . How may i help you?'''
subprocess = []
Function = ["open", "close", "play" , "system" , "content", "google search" , "youtube search"]


QUESTION_WORDS = [
    "who", "what", "when", "where", "why", "how",
    "kaun", "kya", "kab", "kaha", "kyu", "kaise",
    "prime minister", "president", "time", "date"
]



def is_question(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in QUESTION_WORDS)



WAKE_WORDS = [
    "hey nexus",
    "ok nexus",
    "hello nexus",
    "nexus"
    "wakeup nexus"
]


def has_wake_word(text: str):
    text = text.lower().strip()
    for w in WAKE_WORDS:
        if text.startswith(w):
            return w
    return None



def ShowDeafaultMessage():
    File = open(r'Data\ChatLog.json', "r" , encoding='utf-8')
    if len(File.read())<5:
        with open (TempDirectoryPath('Database.data'), 'w' , encoding = 'utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('RESPONSES.data'), 'w', encoding='utf-8') as file:
            file.write(DeafaultMessage)


def ReadChatLog():
    with open(r'Data\ChatLog.json' , 'r' , encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data
 
 
def ChatLogIntegration():
    json_data = ReadChatLog()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"user: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("user", f"{Username} ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('DATABASE.data'), "w", encoding='utf-8') as file:
        file.write(formatted_chatlog)



def ShowChatOnGUI():
     File = open(TempDirectoryPath('DATABASE.data'), "r" , encoding='utf-8')
     Data = File.read()
     if len(str(Data))>0:
            Lines = Data.split('\n')
            result = '\n' .join(Lines)
            File.close()
            File = open(TempDirectoryPath('RESPONSES.data'), "w" , encoding = 'utf-8') 
            File.write(result)
            File.close()
        
        
def InitialExecution():
     SetMicrophoneStatus("False")
     SetAssistantStatus("Available ")
     ShowTextToScreen("")
     ShowDeafaultMessage() 
     ChatLogIntegration()
     ShowChatOnGUI()
    
InitialExecution()

def MainExecution():
    global MIC_BUSY

    t_start = time.time()

    SetAssistantStatus("Listening")
    Query = SpeechRecognition()
    t_stt = time.time()
    print(f"[TIMING] Speech recognition took {t_stt - t_start:.2f}s")

    if not Query or Query.strip() == "":
        SetAssistantStatus("Available")
        return

    print("🎙 FINAL QUERY:", Query)
    SetAssistantStatus("Thinking")

    # ---------------------------------------------------------
    # ROUTE FIRST, THEN CLASSIFY — instead of always calling
    # FirstLayerDMM up front and then throwing its result away
    # whenever is_question(Query) is True. Questions used to pay
    # for TWO sequential model/network calls (FirstLayerDMM +
    # RealtimeSearchEngine); now they only pay for one.
    # ---------------------------------------------------------

    # 1️ QUESTION → ANSWER ONLY (single call, no FirstLayerDMM needed)
    if is_question(Query):
        print(" Question detected → answering directly (skipping FirstLayerDMM)")

        SetAssistantStatus("Searching...")
        t_call_start = time.time()
        Answer = RealtimeSearchEngine(QueryModifier(Query))
        print(f"[TIMING] RealtimeSearchEngine took {time.time() - t_call_start:.2f}s")

        ShowTextToScreen(f"{Assistantname}: {Answer}")

        t_tts_start = time.time()
        TextToSpeech(Answer)
        print(f"[TIMING] TextToSpeech took {time.time() - t_tts_start:.2f}s")

        SetAssistantStatus("Available")
        print(f"[TIMING] TOTAL turn time: {time.time() - t_start:.2f}s")
        return


    # Not a question → we DO need the decision model to tell us
    # whether this is automation or general chat.
    t_decision_start = time.time()
    Decision = FirstLayerDMM(Query)
    print(f"[TIMING] FirstLayerDMM took {time.time() - t_decision_start:.2f}s")
    print("\nDecision :", Decision, "\n")

    # 2️ AUTOMATION COMMANDS
    for q in Decision:
        if any(q.startswith(func) for func in Function):
            print("⚙ Automation triggered:", q)
            run(TranslateAndExecute(list(Decision)))
            SetAssistantStatus("Available")
            print(f"[TIMING] TOTAL turn time: {time.time() - t_start:.2f}s")
            return

    # 2.5️ REALTIME CATEGORY — previously this was never checked here,
    # so anything the model tagged "realtime" silently fell through
    # to general chat and got an offline/stale answer instead of a
    # real web-search-backed one.
    for q in Decision:
        if q.startswith("realtime"):
            QueryFinal = q.replace("realtime", "", 1).strip()
            print("🌐 Realtime query detected:", QueryFinal)

            SetAssistantStatus("Searching...")
            t_call_start = time.time()
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            print(f"[TIMING] RealtimeSearchEngine took {time.time() - t_call_start:.2f}s")

            ShowTextToScreen(f"{Assistantname}: {Answer}")

            t_tts_start = time.time()
            TextToSpeech(Answer)
            print(f"[TIMING] TextToSpeech took {time.time() - t_tts_start:.2f}s")

            SetAssistantStatus("Available")
            print(f"[TIMING] TOTAL turn time: {time.time() - t_start:.2f}s")
            return


    # 3️ GENERAL CHAT
    for q in Decision:
        if q.startswith("general"):
            QueryFinal = q.replace("general", "").strip()

            t_call_start = time.time()
            Answer = Chatbot(QueryModifier(QueryFinal))
            print(f"[TIMING] Chatbot took {time.time() - t_call_start:.2f}s")

            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering")

            t_tts_start = time.time()
            TextToSpeech(Answer)
            print(f"[TIMING] TextToSpeech took {time.time() - t_tts_start:.2f}s")

            SetAssistantStatus("Available")
            print(f"[TIMING] TOTAL turn time: {time.time() - t_start:.2f}s")
            return

    SetAssistantStatus("Available")


def FirstThread():
    global MIC_BUSY

    while True:
        status = GetMicrophoneStatus().strip().lower()

        if status == "true" and not MIC_BUSY:
            MIC_BUSY = True
            try:
                MainExecution()
            except Exception as e:
                # A single failed API/network call must not kill this
                # thread permanently — without this, one hiccup (like a
                # DNS/connection error) would silently stop the mic from
                # ever responding again until the app is restarted.
                print("[ERROR] MainExecution crashed:", e)
                import traceback
                traceback.print_exc()
                ShowTextToScreen(f"{Assistantname}: Sorry, I hit a connection problem. Please try again.")
            finally:
                MIC_BUSY = False
                SetAssistantStatus("Available")

        sleep(0.2)

                
       
                
def secondThread():
    app = QApplication(sys.argv)
    window = GraphicalUserInterface()   # HOLD REFERENCE
    window.show()                       #  FORCE SHOW
    sys.exit(app.exec_())


    
    
if __name__ == "__main__":
    mic_thread = threading.Thread(target=FirstThread, daemon=True)
    mic_thread.start()
    secondThread()