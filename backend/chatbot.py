from  groq import Groq #importing the groq libarires the api
from json import load, dump #importing thre function to read write the json file
import datetime # importing the datetime module for real time date and time information
import time
from dotenv import dotenv_values #importing the dotenv_values to read enviorment variables from the .env files



#load the enviorment variavles from the .env files
env_vars = dotenv_values(r"R:\JARVIS AI ASSISTANT\backend\.env")

#retrive the specific enviorment variables for the username assiastant name AND THE API KEY
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GROQ_API_KEY")


# print("loaded API KEY:", GroqAPIKey)

#its shows the entre error

# print("Loaded:", env_vars)
# print("API:", env_vars.get("GROQ_API_KEY"))

#its shows the entre error
from dotenv import dotenv_values

#initilize the groq client using the provied the API key
client = Groq(api_key=GroqAPIKey)

#initilize the an empty list to store chat message
message = []


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


#define the system message that provide context to the AI chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""


#A list of system instruction for the chatbot
SystemChatbot = [
    {"role":"system",  "content":  System}

]

#attempt to load the chat log from the json file
#attempt to load the chat log from the json file
try:
    with open(r"data\Chatlog.json", "r") as f:
        message = load(f)
except FileNotFoundError:
    # file nahi mili toh ek nayi file create kar do
    with open(r"data\Chatlog.json", "w") as f:
        dump([], f)

#function the to get the real time date and time for the informtion
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day  = current_date_time.strftime("%A")
    date  = current_date_time.strftime("%D")
    month = current_date_time.strftime("%B")
    year =  current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")


    #fromat the inforamtion into s string
    data = f"please use this Real-timeInforamtion if needed \n"
    data += f"day :{day}\ndate: {date}\nmonth: {month}\nyear: {year}\n"
    data += f"time: {hour}hour : {minute}minutes : {second} second.\n"
    return data


#fucniton that modify the chatbot resposne
def AnswerModifer(Answer):
    lines = Answer.split("\n") #split the rsponse into lines
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)# joine the cleaned line back together
    return modified_answer


def _call_groq_chat(payload):
    """Runs the Groq streaming completion and collects it into a single
    string. Wrapped by retry_with_backoff — if the connection drops
    mid-stream, we cleanly retry the whole request."""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=payload,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=True
    )

    answer = ""
    for chunks in completion:
        if chunks.choices[0].delta.content:
            answer += chunks.choices[0].delta.content

    return answer


#main chatbot function to handle user query
def Chatbot(Query):
    """
    This function sends the user query to the AI model
    and returns its response.
    """

    try:
        # Load chat history
        try:
            with open(r"data\Chatlog.json", "r") as f:
                messages = load(f)
        except FileNotFoundError:
            messages = []  # empty chat list

        # Add user message
        messages.append({"role": "user", "content": Query})

        env_vars = dotenv_values(".env")
        groq_api_key = env_vars.get("GroqAPIKEY")

        # make the request to Groq api response — now with automatic retry
        payload = SystemChatbot + [{"role": "system", "content": RealtimeInformation()}] + messages
        Answer = retry_with_backoff(_call_groq_chat, payload)

        Answer = Answer.replace("</s", "")

        # append bot message
        messages.append({"role": "assistant", "content": Answer})

        # save updated chat log
        with open(r"data\Chatlog.json", "w") as f:
            dump(messages, f, indent=4)

        # return modified answer
        return AnswerModifer(Answer=Answer)

    except Exception as e:
        print(f"error: {e}")
        with open(r"data\Chatlog.json", "w") as f:
            dump([], f, indent=4)
        return "SOMETHING WENT WRONG PLEASE TRY AGAIN"  # retry THE QUERY RESTING THE LOG



#MAIN PROGRRAM ENTRY POINT
if __name__ ==  "__main__":
    while True:
        user_input = input("ENTER YOUR QUERY: ")#prompt the user for a user question
        print(Chatbot(user_input)) #call the chatbot   function to print its response