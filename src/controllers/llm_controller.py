import requests, os
import subprocess
import time
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError

load_dotenv()

OLLAMA_PATH = os.getenv('OLLAMA_PATH')
OLLAMA_TEST = os.getenv('OLLAMA_TEST')
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))

ollama_process = None

def ensure_ollama_up():
    global ollama_process

    if is_ollama_already_running():
        print("Ollama is already running.")
        return True

    ollama_process = subprocess.Popen(
        [OLLAMA_PATH, "serve"],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        shell=False,
        close_fds=True
    )
    time.sleep(1)
    timeout=10

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(OLLAMA_TEST, timeout=timeout)
            r.raise_for_status() 
            
            if r.status_code == 200:
                print(f"Llama is running (Attempt: {attempt}/{MAX_RETRIES})")
                return True
            
        except (ConnectionError, HTTPError) as e:
            print(f"Attempt: {attempt}/{MAX_RETRIES}: Connection failed. I'll try again in 2 seconds. ({type(e).__name__})")
            if attempt == MAX_RETRIES:
                break 
                
            time.sleep(2)
            
    print(f"Error connecting to Llama dopo {MAX_RETRIES} tentativi.")
    return False
    
def is_ollama_already_running():
    try:
        r = requests.get(OLLAMA_TEST, timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False
    
def terminate_ollama():
    global ollama_process
    if ollama_process:
        print("Ending Ollama process...")
        ollama_process.terminate()
        try:
            ollama_process.wait(timeout=5)
            print("Ollama process ended.")
        except subprocess.TimeoutExpired:
            print("Ollama process did not terminate in time. Killing it.")
            ollama_process.kill()
        ollama_process = None

  

     