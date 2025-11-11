from yt_dlp import YoutubeDL
import os
import json
import re
import tempfile
import datetime
import os
import json
from flask import jsonify
from dotenv import load_dotenv
from .frames_controller import extract_frames, crop_frames
from .video_validator_controller import ask_llm, is_valid_video, filter_llm
from .llm_controller import ensure_ollama_up

load_dotenv()

MAX_VIDEOS = int(os.getenv('MAX_VIDEOS'))
MAX_SEARCH = 50


#Keywords to be reviewed taking into account the sources found on Internet
KEYWORDS = [
    "teardown", "disassembly", "repair"
]

"""
Check if the video info contains any of the specified keywords in title or description

@param info: dictionary containing video information
@return: True if any keyword is found, False otherwise
"""
def contains_keywords(info):
    combined_text= info.get('title', '') 
    return any(k.lower() in combined_text for k in KEYWORDS)

"""
Get subtitles and frames from YouTube videos based on a search term

@param research: search term for finding relevant videos
@return: None (results are saved to a JSON file)
"""
def get_subtitles(research):

    with tempfile.TemporaryDirectory() as tempdir:
        searcher = YoutubeDL({
            "skip_download": True,
        })

        downloader = YoutubeDL({
            "skip_download": False,
            "format": 'sb0',
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitlesformat": "vtt",
            "subtitleslangs": ["en", "-livechat"],
            "outtmpl":{
                'subtitle': f"{tempdir}/%(id)s",
                'default': f"{tempdir}/%(id)s.mhtml"
                }
        })

        search_query = ' '.join([research] + KEYWORDS)
        data = searcher.extract_info(f"ytsearch{MAX_SEARCH}:{search_query}")

        valid_videos = []

        output_foto = "results/frames"
        os.makedirs(output_foto, exist_ok=True)

        video_scelti = []

        for entry in data.get('entries', []):
            if not entry:
                continue

            title = entry.get("title", "")

            #if not ensure_ollama_up():
            #    return jsonify({
             #   'success': False,
              #  'status': 'error',
               # 'message': f'Unexpected error when connecting to Llama. Please try again."',
            #})

            if not is_valid_video(entry):
                print(title)
                continue
            else:
                video_scelti.append(entry)

        video_scelti = filter_llm(video_scelti, MAX_VIDEOS, research)
        print("-------------------")
        print('\n'.join([x['title'] for x in video_scelti]))

        for entry in video_scelti:
            video_id = entry["id"]
            title = entry["title"]
            url = entry["webpage_url"]
            downloader.download(url)
            channel = entry.get("uploader") or entry.get("channel") or "Unknown"
            duration = entry.get("duration", 0)
            views = entry.get("view_count", 0)

            vtt_path = os.path.join(tempdir, f"{video_id}.en.vtt")

            try:
                with open(vtt_path, 'r', encoding='utf-8') as f:
                    subtitles = f.readlines()
            except FileNotFoundError:
                continue

            subtitles = subtitles[3:]
            subtitles = [r for r in subtitles if not re.match("^\\s*\n", r)]
            subtitles = [re.sub("<[^>]*>","",r) for r in subtitles]

            complete = []
            prev = ''
            time = None
            for r in subtitles:
                if r != prev:
                    if mm := re.match("^([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3})", r):
                        time = datetime.datetime.strptime(mm.group(1) + '000', '%H:%M:%S.%f')
                    else:
                        complete.append({
                            'time': time,
                            'text': r
                            })
                        prev = r

            
            output_path = os.path.join(output_foto, video_id)

            try:
                os.mkdir(output_path)
            except FileExistsError:
                for i in os.listdir(output_path):
                    os.remove(os.path.join(output_path, i))

            file_images = open(f"{tempdir}/{video_id}.mhtml", 'rb')
            data_images = file_images.read()
            file_images.close()
            w = 0
            h = 0
            for ff in entry['formats']:
                if ff['format_id'] == "sb0":
                    w = ff['width']
                    h = ff['height']
            images = extract_frames(data_images)
            frames = []
            for t,img in images:
                frames += crop_frames(img, w, h, t['start'], t['end'])

            results = []
            ccc = 0
            while len(complete)>0 or len(frames)>0:
                if len(complete)>0 and (len(frames)==0 or complete[0]['time'] < frames[0][0]):
                    results.append({'type':'text', 'data': complete[0]['text']})
                    complete = complete[1:]
                else:
                    datt = frames[0][1]
                    impath = os.path.join(output_path, f"{ccc:03d}.png")
                    results.append({'type': 'image', 'data': impath})
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
            
        output_dir = "results/subtitles"
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{research.replace(' ', '_')}_subtitles.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_videos, f, ensure_ascii=False, indent=2)
