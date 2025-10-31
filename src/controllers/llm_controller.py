import requests, os
import subprocess
from dotenv import load_dotenv

load_dotenv()

OLLAMA_TEST = os.getenv('OLLAMA_TEST')
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))

def ensure_ollama_up(url=OLLAMA_TEST, timeout=2):

    subprocess.Popen(
        ["ollama", "serve"],
        #stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL,
        #stdin=subprocess.DEVNULL,
        shell=False,
        close_fds=True
    )

    attempt = 0
    for attempt in range(MAX_RETRIES):
            r = requests.get(OLLAMA_TEST, timeout=timeout)
            r.raise_for_status()
            if r.status_code == 200:
                print(f"Llama is running")
                return True
            attempt = attempt + 1
            if attempt > MAX_RETRIES:
                print(f"Error connecting to Llama")
                return False
    

     