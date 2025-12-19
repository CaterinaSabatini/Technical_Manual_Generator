import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
PROMPT_TEMPLATE_MANUAL_PATH = os.getenv('PROMPT_MANUAL')


if not PROMPT_TEMPLATE_MANUAL_PATH:
    raise ValueError("The environment variable for LLM is not set.")


try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_PROMPT_PATH = os.path.join(BASE_DIR, '..', PROMPT_TEMPLATE_MANUAL_PATH) 

    with open(FULL_PROMPT_PATH, 'r', encoding='utf-8') as f:
        FILTER_PROMPT_TEMPLATE = f.read().strip()
    
except FileNotFoundError:
    raise FileNotFoundError(f"Error: Could not find file at path. Check your settings in .env.")

"""
Generate a step-by-step disassembly manual in HTML format for the device name specified by the user.

@param data: list of dictionaries containing video data
@param device_name: name of the device being disassembled
@return: a string of HTML-formatted document
"""
def report_llm(data):

    all_subs = []
    for video in data:
        for sub in video.get("subtitles_data", []):
            all_subs.append(sub["s"])

    subtitles_text = "\n".join(all_subs)

    MAX_CHARS = 50000 
    if len(subtitles_text) > MAX_CHARS:
        subtitles_text = subtitles_text[:MAX_CHARS]
        print(f"DEBUG: Input testo troncato a {MAX_CHARS} caratteri.")

    print("-" * 50)
    print(f"DEBUG: Lunghezza finale subtitles_text: {len(subtitles_text)}")
    print(f"DEBUG: Primi 500 caratteri di subtitles_text:\n{subtitles_text[:500]}")
    print("-" * 50)

    # Assicurati che FILTER_PROMPT_TEMPLATE sia il template che chiede HTML/Markdown!
    prompt = f"""{FILTER_PROMPT_TEMPLATE} {subtitles_text}"""
    prompt = ' '.join(prompt.split(' ')[:3000])


    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "stop": ["```", "\n```", "\n\n\n"] 
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=1200)
        r.raise_for_status()

        response = r.json() 
        manual_text = response.get("response", "")

        print("-" * 50)
        print("DEBUG: Output Grezzo LLM (manual_text):")
        print(manual_text)
        print("-" * 50)

        if not manual_text or manual_text.strip() == "":
            print("DEBUG FALLITO: report_llm ha restituito output vuoto.")
            return None 
        
        html_output = manual_text.strip()
        text_lines = html_output.split('\n')
        start_line_index = -1

        for i, line in enumerate(text_lines):
            line_stripped = line.strip()
            if re.match(r'^\d+\.', line_stripped):
                start_line_index = i
                break
            if re.match(r'^\*\*[^:]+\*\*', line_stripped):
                start_line_index = i
                break

        if start_line_index != -1:
            cleaned_manual_text = '\n'.join(text_lines[start_line_index:])
            print("DEBUG SUCCESSO: Markdown strutturato isolato.")
        else:
            cleaned_manual_text = manual_text.strip()
            print("DEBUG ATTENZIONE: Nessuna struttura Markdown trovata. Usando l'output completo.")
            
        return cleaned_manual_text

    except requests.exceptions.RequestException as e:
        print(f"Network error during Ollama call: {e}")
        return None
    

