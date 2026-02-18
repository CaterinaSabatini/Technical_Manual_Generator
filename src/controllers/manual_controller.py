import os
import requests
from flask import render_template
import json
import re
import datetime
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
PROMPT_TEMPLATE_MANUAL_PATH = os.getenv('PROMPT_MANUAL')


if not PROMPT_TEMPLATE_MANUAL_PATH:
    raise ValueError("Prompt template path not set in environment variables")

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_PROMPT_PATH = os.path.join(BASE_DIR, '..', PROMPT_TEMPLATE_MANUAL_PATH) 

    with open(FULL_PROMPT_PATH, 'r', encoding='utf-8') as f:
        FILTER_PROMPT_TEMPLATE = f.read().strip()
    
except FileNotFoundError:
    raise FileNotFoundError(f"Error: Could not find file at path.")

"""
Generate device manual using LLM based on subtitles data.
@param data: List of videos with subtitles data.
@param device_name: Name of the device for which manual is generated.
@return: Filename of the saved manual JSON or "error" in case of failure.
"""
def report_llm(data, device_name):


    all_subs = []
    video_channels = []
    video_urls = []

    video = data
    
    if "channel" in video and video["channel"] not in video_channels:
        video_channels.append(video["channel"])
    if "url" in video and video["url"] not in video_urls:
        video_urls.append(video["url"])
        
    for sub in video.get("subtitles_data", []):
        all_subs.append(sub["s"])

    subtitles_text = "\n".join(all_subs)
 

    prompt = f"""{FILTER_PROMPT_TEMPLATE} {subtitles_text}"""


    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 4096,
            "temperature": 0.2
        },
        "stop": ["```", "\n```", "\n\n\n"] 
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=1200)
        r.raise_for_status()
        response = r.json() 
        manual_text = response.get("response", "")

        if not manual_text:
            return "error", None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        manuals_dir = os.path.join(base_dir, '..', 'video_reports')

        if not os.path.exists(manuals_dir):
            os.makedirs(manuals_dir)

        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        safe_device_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', device_name.lower())

        file_name = f"{safe_device_name}_{timestamp}.json"
        file_path = os.path.join(manuals_dir, file_name)

        manual_json = {
            "title": video["title"],
            "device": device_name,
            "manual_text": manual_text,
            "timestamp": timestamp,
            "channels": video_channels,
            "urls": video_urls,
            "score": video["score"]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(manual_json, f, ensure_ascii=False, indent=4)

        return file_name

    except Exception:
        return "error", None

    

    

