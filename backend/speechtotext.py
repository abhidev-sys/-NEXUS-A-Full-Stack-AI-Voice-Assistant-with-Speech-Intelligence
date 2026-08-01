from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time
 

#load the enviorment varialbles from the env files 
env_vars = dotenv_values(r"R:\JARVIS AI ASSISTANT\.env")


#get the input language settting from the enviorment variables 
InputLanguage = env_vars.get("InputLanguage", "en-IN")

#load the inptus values
print("Loaded Language:" , InputLanguage)

#define the html code fo the speech recoginition interaface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>

    <script>
    const output = document.getElementById('output');
    let recognition;

    function startRecognition() {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "__LANG__";
        recognition.continuous = false;   // 🔥 VERY IMPORTANT

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            output.textContent = transcript;
        };

        recognition.start();
    }

    function stopRecognition() {
        if (recognition) {
            recognition.stop();
        }
    }
</script>

</body>
</html>
'''


#replace the laguage the setting the code with the input lamguage form the enviorment varibles 
HtmlCode = HtmlCode.replace("__LANG__", InputLanguage)

#worte the modified HTML code for the to a file.
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)
    
#get the currrent working the directory 
current_dir = os.getcwd()
#genrate the file path for the html file 
Link = f"{current_dir}/Data/Voice.html"

#set the chrome option for the webdriver
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options = Options()
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")

chrome_prefs = {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1,
    "profile.default_content_setting_values.notifications": 1
}
chrome_options.add_experimental_option("prefs", chrome_prefs)


#define the path for the tempeoray file 
TempDirPath = rf"{current_dir}/Frontend/Files"

#fucntion to set assistant status by writing the it to a file 
def  SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding = 'utf-8') as file:
        file.write(Status)
        
#INITILIZER THE SERVICE MANGER                     
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
        
        
#function to mocdfiy query to ensure proper pucntonation and formatting.
def QueryModifire(Query):
    new_query =  Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how " , "what", "who", "where", "when", "why", "which", "whoes", "whom", "can you", "what's", "where's", "how's" "can you"]
    
    
    #check if any query is the question and add a question mark if necessaery 
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.' , '?' , '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query +=  "?"
    else:
        #ADD THE PERIODS IF THE QUERY IS NOT A QUESTION
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
            
            
    return new_query.capitalize()


#function to traslate the text into speech using the mtralste library
def UniversalTranslator(Text):
    english_translation = mt.translate(Text , "en", "auto")
    return english_translation.capitalize()


#function use to perfoem the speech recogigniton usging the wedriver
def SpeechRecognition(timeout=6):
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            time.sleep(0.2)
            text = driver.find_element(By.ID, "output").text.strip()

            if text:
                print("🟢 STT TEXT:", text)
                driver.find_element(By.ID, "end").click()
                return QueryModifire(text)

        except Exception:
            pass

    driver.find_element(By.ID, "end").click()
    return ""



#mmain the execuiton block 
if __name__ == "__main__":
    while True:
        #continously perform the speech recoginition and print the recognition text 
        print("listening your voice")
        Text = SpeechRecognition()
        print(Text)
        
                         