import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep
import json

# Load .env
load_dotenv() # LOAD THE ENV FILE HERE FOR INTRAACTION


#this will load the API KEY OF THE HUGGING FACE FROMT THE .ENV FILE 

API_KEY = os.getenv("huggingfaceAPIKey")

if not API_KEY:
    raise ValueError("huggingfaceAPIKey not found in .env file")

headers = {"Authorization": f"Bearer {API_KEY}"}

print("Loaded API KEY:", API_KEY)

# API URL 
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

# Debug query
async def query(payload):
    response = await asyncio.to_thread(
        requests.post,
        API_URL,
        headers=headers,
        json=payload
    )
    

    print("STATUS:", response.status_code)
    print("HEAD:", response.content[:200])

    if response.status_code != 200:
        print("HF ERROR:", response.text)
        return None

    return response.content


# Generate images
async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, ultra high detail, 4k resolution, seed={randint(0,999999)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    # Save images
    for i, image_bytes in enumerate(image_bytes_list, start=1):

        if image_bytes is None:
            print(f" Image {i} not generated.")
            continue

        # Check if JSON error instead of image bytes
        try:
            text = image_bytes.decode("utf-8")
            if "error" in text:
                print(f" HF Error in image {i}: {text}")
                continue
        except:
            pass

        filename = f"Data/{prompt.replace(' ', '_')}{i}.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)

        print("✔ Saved:", filename)


def GenerateImages(prompt):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


# Open images
def open_images(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")

    files = [f"{prompt}{i}.png" for i in range(1, 5)]

    for file in files:
        path = os.path.join(folder_path, file)

        try:
            img = Image.open(path)
            print("Opening:", path)
            img.show()
            sleep(1)
        except:
            print("Unable to open:", path)


# Main loop
while True:
    try:
        with open(r"frontend/files/imageGeneration.DATA", "r") as f:
            data = f.read()

        Prompt, Status = data.split(",")
        Prompt = Prompt.strip()
        Status = Status.strip()

        if Status == "True":
            print("Generating Images...")
            GenerateImages(Prompt)
            
            
            with open(r"frontend/files/imageGeneration.DATA", "w") as f:
                f.write("False,False")
                
            break

        sleep(1)

    except :
        pass

print("Prompt:", Prompt)
print("Status:", Status)
