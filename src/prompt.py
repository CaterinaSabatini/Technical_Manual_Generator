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

#---------------------------------------------------
PROMPT_TXT = """You are a highly specialized AI designed to select the most relevant YouTube videos for device repair.
Your goal is to choose the **EXACTLY NUMBER_TO_CHOOSE** best videos from the provided list.

**Decision Criteria (Strict Match Required):**
1.  **Device Match:** The video title must contain the **EXACT** computer model specified (Device: "DEVICE_MODEL_PLACEHOLDER").
2.  **Activity Match:** The title must clearly describe one of these activities: **teardown, disassembly, or repair**.

--- HARD RULES (No Exceptions) ---
* **Exact Model:** The requested model must appear unambiguously in the title, with correct brand and series.
* **Screen Size/Generation:** If the device name specifies a size (e.g., 15.6) or generation (e.g., Gen 2), it must match exactly. **"15" ≠ "15.6"**.
* **Punctuation:** Treat hyphens, spaces, and punctuation as formatting differences only (e.g., "T16", "T-16", and "T 16" are equivalent).
* **SKU/Family Exclusion:** Do **NOT** accept close families or different SKUs (e.g., ThinkPad T16 ≠ T14).
* **Mandatory Keywords:** The title must contain at least one of the keywords: **teardown, disassembly, or repair**.

**Input Data:**
Device Model: "**DEVICE_MODEL_PLACEHOLDER**"
Number to Choose: **NUMBER_TO_CHOOSE**

---- VIDEOS TO EVALUATE ----
VIDEO_LIST_PLACEHOLDER
---- END VIDEOS ----

**Output Format:**
You must only return a single JSON object containing the IDs of the chosen videos.

{
"chosen": [
ID_1,
ID_2,
...
ID_M
]
}"""