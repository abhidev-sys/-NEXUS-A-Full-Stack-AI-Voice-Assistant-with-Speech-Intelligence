from  groq import Groq #importing the groq libarires the api 
from json import load, dump #importing thre function to read write the json file 
import datetime # importing the datetime module for real time date and time information 
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


#define the system message that provide context to the AI chatbot 
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
* Do not tell time until I ask, do not talk too much, just answer the question.*
* Reply in the same language as the user.
If the user speaks Hindi, reply in Hindi.
If the user speaks English, reply in English.
If the user uses Hinglish, reply naturally in Hinglish.
Keep responses conversational and concise.*
* Do not provide notes in the output, just answer the question and never mention your training data. *
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
    day  =  current_date_time.strftime("%A")
    date  = current_date_time.strftime("%D")
    month = current_date_time.strftime("%B")
    year =  current_date_time.strftime("%Y")
    hour =  current_date_time.strftime("%H")
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
        
        # make the request to Groq api response 
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatbot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""  

        # process the stream line response chunks
        for chunks in completion:
            if chunks.choices[0].delta.content: 
                Answer += chunks.choices[0].delta.content

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
if __name__==  "__main__":
    while True:
        user_input = input("ENTER YOUR QUERY: ")#prompt the user for a user question 
        print(Chatbot(user_input)) #call the chatbot   function to print its response   