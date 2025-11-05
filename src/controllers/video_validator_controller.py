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

Device: "SEGNAPOSTO_DISPOSITIVO"
Title: "SEGNAPOSTO_TITOLO"
""".strip()
FILTER_PROMPT_TEMPLATE = """
You are a strict validator for YouTube video titles.
Your goal is to choose the SEGNAPOSTO_NUMERO videos that most likely refer to the EXACT computer model specified.

your are provided a list of ids and titles to choose from, like this:
---- VIDEOS ----
ID_1; TITLE_1
ID_2; TITLE_2
...
ID_N; TITLE_N
---- END VIDEOS ----


EXAMPLE:
The video's title can be can be accompanied by other words (e.g. If I search 'MacBook Pro 16 2021' and 
the video's title is 'Hey, I show you a MacBook Pro 16 2021 teardown' you have to give a high score. 
Otherwise if the video's title contains 'Macbook Pro 16S 2021", the video must be discarded). 
You must consider only video's titles that contain the exact model specified, and reject all the others.
For example, with device, number and videos like these:
Device: "Dell Latitude 5000"
Number: 3
---- VIDEOS ----
JZZgXTg3pPk; Dell Latitude 5000 teardown
GjeaU7N2BfG; Macbook Pro fix fan
8Fh1nAoGmwA; review Dell latitude
iJQmt02NafY; Replacing screen on Dell Latitude 5000
HWnf01jG73A; Just got a new computer
Un26JfniSFa; Dell Latitude 5000 keyboard fix
---- END VIDEOS ----
you should return
{
    "chosen": [
        JZZgXTg3pPk,
        iJQmt02NafY,
        Un26JfniSFa
    ]
}



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
  "chosen": [
  ID_1,
  ID_2,
  ...
  ID_M
  ]
}
where M is the number of videos to choose

Device: "SEGNAPOSTO_DISPOSITIVO"
Number: SEGNAPOSTO_NUMERO
---- VIDEOS ----
LISTA_VIDEO
---- END VIDEOS ----
""".strip()

def ask_llm(device, title):

    #try: 
        device = device.lower().strip()
        title = title.lower().strip()

        if not title:
            print("No title was found")
            return {"match": False, "score": 0.0, "reason": "No title was found"}
        
        prompt = PROMPT_TEMPLATE.replace("SEGNAPOSTO_DISPOSITIVO",device).replace("SEGNAPOSTO_TITOLO", title)
        
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

        r = requests.post(OLLAMA_URL, json=payload, timeout = 120)
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

"""
select the most relevant videos from the list provided

@param videos: list of video ids and titles
@param count: number of videos to choose
@param model: device model to search
@return: a subset of videos of length $count
"""
def filter_llm(videos, count, model):
    l_video = '\n'.join(['; '.join((r['id'],r['title'])) for r in videos]) + '\n'
    prompt = FILTER_PROMPT_TEMPLATE.replace("SEGNAPOSTO_MODELLO",model).replace("SEGNAPOSTO_NUMERO",str(count)).replace("LISTA_VIDEO",l_video)
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
    r = requests.post(OLLAMA_URL, json=payload, timeout = 120)
    r.raise_for_status()
    raw = r.json().get("response", "")
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    resp = json.loads(m.group(0))
    ret = []
    for e in videos:
        if e['id'] in resp['chosen']:
            ret.append(e)
    return ret

