import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()


OLLAMA_URL = os.getenv('OLLAMA_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
PROMPT_TEMPLATE_SUBTITLES_PATH = os.getenv('PROMPT_SUBTITLES')

#Validation parameters
MIN_VIEWS = int(os.getenv('MIN_VIEWS'))
MIN_DURATION = int(os.getenv('MIN_DURATION')) 
MAX_DURATION = int(os.getenv('MAX_DURATION'))
MIN_LIKE_RATIO = float(os.getenv('MIN_LIKE_RATIO'))


if not PROMPT_TEMPLATE_SUBTITLES_PATH:
    raise ValueError("Prompt template path not set in environment variables")

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_PROMPT_PATH = os.path.join(BASE_DIR, '..', PROMPT_TEMPLATE_SUBTITLES_PATH) 

    with open(FULL_PROMPT_PATH, 'r', encoding='utf-8') as f:
        FILTER_PROMPT_TEMPLATE = f.read().strip()
    
except FileNotFoundError:
    raise FileNotFoundError(f"Error: Could not find file at path")


"""
Validate if a video entry meets the criteria
@param entry: video metadata dictionary
@return: True if valid, False otherwise
"""
def is_valid_video(entry):
    views = entry.get('view_count', 0)
    duration = entry.get('duration', 0)

    like_count = entry.get('like_count') or 0
    dislike_count = entry.get('dislike_count') or 0
    
    total_votes = like_count + dislike_count
    ratio_votes = like_count / total_votes if total_votes > 0 else 1

    return (
        views >= MIN_VIEWS and
        MIN_DURATION <= duration <= MAX_DURATION and
        ratio_votes >= MIN_LIKE_RATIO
    )

"""
Filter videos using LLM to select the most relevant ones
@param videos: list of video metadata dictionaries
@param count: number of videos to select
@param model: device model name
@return: list of selected video metadata dictionaries
"""
def filter_llm(videos, count, model):
    

    l_video = '\n'.join(['; '.join((r['id'],r['title'])) for r in videos]) + '\n'

    prompt = (
        FILTER_PROMPT_TEMPLATE
        .replace("CONTEXT_MODELS_PLACEHOLDER", model)
        .replace("NUMBER_TO_CHOOSE", str(count))
        .replace("VIDEO_LIST_PLACEHOLDER", l_video)
    )


    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "options": {
            "temperature": 0.0,
            "seed": 1,
            "top_k": 10,
            "top_p": 0.1,
            "min_p": 0,
            "repeat_penalty": 1.15,
            "mirostat": 0
        },
        "format": "json",
        "stream": False,
        "stop": ["```", "\n```", "\n\n\n"] 
    }
    

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status() 
        
        raw = r.json().get("response", "")
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        
        if not m:
            return []
        
        resp = json.loads(m.group(0))
        
    except requests.exceptions.RequestException:
        return []
    except json.JSONDecodeError:
        return []
    
    ret = []
    chosen_ids = resp.get('chosen', [])
    if isinstance(chosen_ids, list):
        for e in videos:
            if e['id'] in chosen_ids:
                ret.append(e)
                
    return ret