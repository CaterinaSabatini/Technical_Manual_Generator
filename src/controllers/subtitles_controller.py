from yt_dlp import YoutubeDL
import os
import json
import re
import tempfile
import datetime
from controllers import fotogrammi_controller as fotogrammi


#Keywords to be reviewed taking into account the sources found on Internet
KEYWORDS = [
    "teardown", "disassembly", "repair", "fix", "remove",
    "replace", "replacement", "unscrew","removal", "step by step"
]

#Maximum number of videos to analyze
MAX_VIDEOS = 3

#Validation parameters for video selection
MIN_VIEWS = 10000
MIN_DURATION = 60 # seconds
MAX_DURATION = 3600 # 1h 
MIN_LIKE_RATIO = 0.7 # min 70% likes vs total votes

"""
Check if the video info contains any of the specified keywords in title or description
"""
def contains_keywords(info):
    combined_text= (info.get('title', '') + " " + info.get('description', '')).lower()
    return any(k.lower() in combined_text for k in KEYWORDS)

"""
Check if the video meets all the criteria for selection
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
Get subtitles from YouTube videos based on a search query
"""

def get_sottotitoli(ricerca):

    with tempfile.TemporaryDirectory() as tempdir:

        downloader = YoutubeDL({
            "skip_download": False,
            "format": 'sb0',
            "writesubtitles": True,
            "writeautomaticsub": True,
            #"subtitleslangs": ["en"], # English subtitles for more accuracy
            "outtmpl":{
                'subtitle': f"{tempdir}/%(id)s",
                'default': f"{tempdir}/%(id)s.mhtml"
                }
        })

        print(f"ytsearch{MAX_VIDEOS}:{ricerca}")

        data = downloader.extract_info(f"ytsearch{MAX_VIDEOS}:{ricerca}")

        with open(os.path.join(tempdir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        

        valid_videos = []
        output_foto = "fotogrammi"
        os.makedirs(output_foto, exist_ok=True)

        
        for entry in data.get('entries', []):
            if not entry or not is_valid_video(entry):
                continue
            video_id = entry["id"]
            url = entry["webpage_url"]
            channel = entry.get("uploader") or entry.get("channel") or "Unknown"
            title = entry.get("title", "")
            duration = entry.get("duration", 0)
            views = entry.get("view_count", 0)

            vtt_path = os.path.join(tempdir, f"{video_id}.en.vtt")

            try:
                with open(vtt_path, 'r', encoding='utf-8') as f:
                    sottotitoli = f.readlines()
            except FileNotFoundError:
                continue
            
            sottotitoli = sottotitoli[3:]
            sottotitoli = [r for r in sottotitoli if not re.match("^\\s*\n", r)]
#            sottotitoli = [r for r in sottotitoli if not re.match("^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}", r)]
            sottotitoli = [re.sub("<[^>]*>","",r) for r in sottotitoli]

            
            completi = []
            prev = ''
            time = None
            for r in sottotitoli:
                if r != prev:
                    if mm := re.match("^([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3})", r):
                        time = datetime.datetime.strptime(mm.group(1) + '000', '%H:%M:%S.%f')
                    else:
                        completi.append({
                            'tempo': time,
                            'testo': r
                            })
                        prev = r

            
            output_path = os.path.join(output_foto, video_id)

            try:
                os.mkdir(output_path)
            except FileExistsError:
                for i in os.listdir(output_path):
                    os.remove(os.path.join(output_path, i))

            file_immagini = open(f"{tempdir}/{video_id}.mhtml", 'rb')
            dati_immagini = file_immagini.read()
            file_immagini.close()
            w = 0
            h = 0
            for ff in entry['formats']:
                if ff['format_id'] == "sb0":
                    w = ff['width']
                    h = ff['height']
            immagini = fotogrammi.estrai_fotogrammi(dati_immagini)
            frames = []
            for t,img in immagini:
                frames += fotogrammi.taglia_fotogramma(img, w, h, t['inizio'], t['fine'])

            results = []
            ccc = 0
            while len(completi)>0 or len(frames)>0:
                if len(completi)>0 and (len(frames)==0 or completi[0]['tempo'] < frames[0][0]):
                    results.append({'tipo':'testo', 'dati': completi[0]['testo']})
                    completi = completi[1:]
                else:
                    datt = frames[0][1]
                    impath = os.path.join(output_path, f"{ccc:03d}.png")
                    results.append({'tipo': 'immagine', 'dati': impath})
                    datt.save(impath,"PNG")
                    ccc+=1
                    frames = frames[1:]

            valid_videos.append({
                "video_id": video_id,
                "url": url,
                "channel": channel,
                "title": title,
                "duration": duration,
                "views": views,
                "subtitles": results,
                "copyright_note": f"'{title}' by {channel} on YouTube."
            })
            
        output_dir = "subtitles"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{ricerca.replace(' ', '_')}_subtitles.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_videos, f, ensure_ascii=False, indent=2)
