from yt_dlp import YoutubeDL
import json
import re
import tempfile

#Keywords to be reviewed taking into account the sources found on Internet
KEYWORDS = [
    "teardown", "disassembly", "repair", "ifixit", "remove battery",
    "replace screen", "unscrew", "upgrade ram", "ssd removal",
    "keyboard removal", "motherboard", "step by step"
]

#Validation parameters for video selection

MIN_VIEWS = 10000
MIN_DURATION = 60 # seconds
MAX_DURATION = 3600 # 1h
MIN_LIKE_RATIO = 0.7 # min 70% likes vs total votes

#Create a temporary directory to store downloaded subtitles
dd = tempfile.TemporaryDirectory() 

#Path to the temporary directory
tempdir = dd.name

downloader = YoutubeDL({"skip_download": True,
                        "writeautomaticsub": True,
                        "outtmpl": {
                            "subtitle": f"{tempdir}/%(id)s"
                            }
                        })

data = downloader.extract_info("ytsearch1:macbook air 2012 repair")

with open(f"{tempdir}/data.json", "w") as f:
    json.dump(data, f)
with open(f"{tempdir}/{data['entries'][0]['id']}.en.vtt", 'r') as f:
    sottotitoli = f.readlines()

sottotitoli = sottotitoli[3:]
sottotitoli = [r for r in sottotitoli if not re.match("^\\s*\n", r)]
sottotitoli = [r for r in sottotitoli if not re.match("^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}", r)]
sottotitoli = [re.sub("<[^>]*>","",r) for r in sottotitoli]
completi = []
prev = ''
time = (0,0,0)
for r in sottotitoli:
    if r != prev:
        if mm := re.match("^([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3})", r):
            time = (int(mm.group(1)),int(mm.group(2)),int(mm.group(3)))
        else:
            completi.append({
                'tempo': time,
                'testo': r
                })
            prev = r

with open("sottotitoli.json", 'w') as f:
    json.dump(completi, f)
print(completi)

