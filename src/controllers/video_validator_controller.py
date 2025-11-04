import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

# Ollama LLM configuration
OLLAMA_URL = os.getenv('OLLAMA_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
MIN_SCORE_THRESHOLD = float(os.getenv('MIN_SCORE_THRESHOLD'))

# Video validation criteria
MIN_VIEWS = int(os.getenv('MIN_VIEWS'))
MIN_DURATION = int(os.getenv('MIN_DURATION')) 
MAX_DURATION = int(os.getenv('MAX_DURATION'))
MIN_LIKE_RATIO = float(os.getenv('MIN_LIKE_RATIO'))

# Define the prompt template for validating YouTube video titles
PROMPT_TEMPLATE = """
You are a strict validator for YouTube video titles.
Your goal is to decide whether a given title refers to the EXACT computer model specified.
You must consider only video's titles that contain the exact model specified, and reject all the others.

EXAMPLE:
The video's title can be can be accompanied by other words (e.g. If I search 'MacBook Pro 16 2021' and 
the video's title is 'Hey, I show you a MacBook Pro 16 2021 teardown' you have to approve it. 
Otherwise if the video's title contains 'Macbook Pro 16S 2021", the video must be discarded). 
You must consider only video's titles that contain the exact model specified, and reject all the others.

HARD RULES (authoritative, no exceptions):
- The requested model must appear unambiguously in the title, with correct brand and series.
- If the device name contains a screen size in inches (e.g. 15.6), it must match exactly.
  "15" ≠ "15.6".
- If the device name contains a generation (e.g. "Gen 2"), it must match the same generation.
- Treat hyphens, spaces, and punctuation as formatting differences only.
  (e.g. "T16", "T-16", and "T 16" are equivalent)
- Do NOT accept close families or different SKUs (e.g. ThinkPad T16 ≠ T14,
  Latitude 5310 ≠ Inspiron 5310).
- If the device name does NOT specify inches or generation, do not penalize a title
  for missing them.
- The title should clearly describe a teardown, disassembly, or repair of that device.

RETURN JSON with keys:
{
  "match": true|false,
  "score": number,       // confidence 0..1
  "reason": "short explanation"
}

Device: "{device}"
Title: "{title}"
""".strip()

def ask_llm(device, title):

    #try: 
        device = device.lower().strip()
        title = title.lower().strip()

        if not title:
            print("No title was found")
            return {"match": False, "score": 0.0, "reason": "No title was found"}
        
        prompt = PROMPT_TEMPLATE.format(device=device, title=title)
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "score": MIN_SCORE_THRESHOLD,
            "options": {
                "temperature": 0.0,
                "seed": 1,
                "top_k": 1,#?
                "top_p": 0.1, #?
                "min_p": 0, #?
                "repeat_penalty": 1.15,
                "mirostat": 0
            },
            "format": "json",
            "stream": False,
            "keep_alive": "5m",

            # Tokens:
            #   "```"    -> stop if a code fence starts; prevents fenced Markdown around the JSON.
            #   "\n```"  -> also catch a fence that begins on the next line.
            #   "\n\n\n" -> stop on three consecutive newlines; useful to cut off drifting/empty output.
            "stop": ["```", "\n```", "\n\n\n"] 
        }

        r = requests.post(OLLAMA_URL, json=payload, timeoute = 120)
        r.raise_for_status()
        raw = r.json().get("response", "")
        m = re.search(r'\{.*\}', raw, re.DOTALL)

        return json.loads(m.group(0))

    #except Exception:
    #    return {"match": False, "score": 0.0, "reason": "Error communicating with Ollama LLM"}


"""
Check if the video meets all the criteria for selection

@param entry: dictionary containing video information
@return: True if the video is valid, False otherwise
"""
def is_valid_video(entry):
    views = entry.get('view_count', 0)
    duration = entry.get('duration', 0)

    if (like_count := entry.get('like_count')) is None:
        like_count = 0
    if (dislike_count := entry.get('dislike_count')) is None:
        dislike_count = 0
    total_votes = like_count + dislike_count
    ratio_votes = like_count / total_votes if total_votes > 0 else 1

    return (
        views >= MIN_VIEWS and
        MIN_DURATION <= duration <= MAX_DURATION and
        ratio_votes >= MIN_LIKE_RATIO
    )

