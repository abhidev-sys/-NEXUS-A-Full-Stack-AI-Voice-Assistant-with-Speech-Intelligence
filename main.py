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

    SetAssistantStatus("Listening")
    Query = SpeechRecognition()

    if not Query or Query.strip() == "":
        SetAssistantStatus("Available")
        return

    print("🎙 FINAL QUERY:", Query)
    SetAssistantStatus("Thinking")

    Decision = FirstLayerDMM(Query)
    print("\nDecision :", Decision, "\n")



    # 1️ QUESTION → ANSWER ONLY

    if is_question(Query):
        print(" Question detected → answering")

        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        TextToSpeech(Answer)
        SetAssistantStatus("Available")
        return


    # 2️ AUTOMATION COMMANDS
    
    for q in Decision:
        if any(q.startswith(func) for func in Function):
            print("⚙ Automation triggered:", q)
            run(TranslateAndExecute(list(Decision)))
            SetAssistantStatus("Available")
            return

    
    # 3️ GENERAL CHAT
    
    for q in Decision:
        if q.startswith("general"):
            QueryFinal = q.replace("general", "").strip()
            Answer = Chatbot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering")
            TextToSpeech(Answer)
            SetAssistantStatus("Available")
            return


                      
def FirstThread():
    global MIC_BUSY

    while True:
        status = GetMicrophoneStatus().strip().lower()

        if status == "true" and not MIC_BUSY:
            MIC_BUSY = True
            MainExecution()
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

    
                          
                      
                                  
                      

                      
                 
        
                  
                