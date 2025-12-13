from yt_dlp import YoutubeDL
import os
import json
import re
import tempfile
import sqlite3
import datetime
from flask import jsonify
from dotenv import load_dotenv
from .video_validator_controller import is_valid_video, filter_llm
import requests

load_dotenv()

MAX_VIDEOS = int(os.getenv('MAX_VIDEOS'))
MAX_SEARCH = int(os.getenv('MAX_SEARCH'))
OLLAMA_URL = os.getenv('OLLAMA_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

KEYWORDS = [
    "teardown", "disassembly", "repair"
]

"""
Mapping device research string to possible model names from a local database

@param research: search term for finding relevant models
@return: list of model names
"""
def map_device_to_models(research):
    
    db_path = 'devices_database/device.sqlite'
    models = []
    
    lower_research = research.strip().lower() 

    word_count = len(lower_research.split())

    if len(lower_research) < 4 or word_count < 3:
            return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT DISTINCT DEVICE FROM devices WHERE LOWER(DEVICE) = ? LIMIT 5", 
            (lower_research,) 
        )
        
        results = cursor.fetchall()
        models = [row[0] for row in results]
        
        if models:
            return models
        

        cleaned_research = lower_research.replace(' ', '%')

        if len(cleaned_research.replace('%', '')) < 3:
            return []

        search_term_like = f'%{cleaned_research}%'
        

        cursor.execute(
            "SELECT DISTINCT DEVICE FROM devices WHERE LOWER(DEVICE) LIKE ? LIMIT 5", 
            (search_term_like,)
        )
        
        results = cursor.fetchall()
        models = [row[0] for row in results]
        
    except sqlite3.Error:
        return [research]
        
    finally:
        if conn:
            conn.close()

    if not models:
        return [research]
    
    return models

"""
Check if the video info contains any of the specified keywords in title or description

@param info: dictionary containing video information
@return: True if any keyword is found, False otherwise
"""
def contains_keywords(info):
    combined_text = info.get('title', '') 
    return any(k.lower() in combined_text for k in KEYWORDS)

"""
Get subtitles from YouTube videos based on a search term

@param research: search term for finding relevant videos
@return: tuple (status, subtitles data or error message)
"""
def get_subtitles(research):

    mapped_models = map_device_to_models(research)

    if not mapped_models:
        return jsonify({
            'success': False,
            'status': 'warning',
            'error': f'No models found for device "{research}". Please provide a more specific device name.'
        }), 400
        

    models_query_part = ' | '.join(mapped_models)
    print(f"Mapped models for '{research}': {models_query_part}")

    with tempfile.TemporaryDirectory() as tempdir:

        downloader = YoutubeDL({
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "ignoreerrors": True,
            "subtitlesformat": "vtt",
            "subtitleslangs": ["en", "-livechat"],
            "outtmpl":{
                'subtitle': f"{tempdir}/%(id)s",
                'default': f"{tempdir}/%(id)s.mhtml" 
                }
        })

        search_query = ' '.join([models_query_part] + KEYWORDS)
        data = downloader.extract_info(f"ytsearch{MAX_SEARCH}:{search_query}")

        valid_videos = []
        chosen_videos = []

        for entry in data.get('entries', []):
            if not entry:
                continue

            title = entry.get("title", "")

            if not is_valid_video(entry):
                print(f"Skipping invalid video: {title}")
                continue
            else:
                chosen_videos.append(entry)
            
            if len(chosen_videos) == 0:
                return jsonify({
                    'success': False,
                    'status': 'warning',
                    'error': f'The research for "{research}" did not return any valid videos. Please try with a different device name.'
                }), 404

        
        llm_context_models = ' | '.join(mapped_models)
        chosen_videos = filter_llm(chosen_videos, MAX_VIDEOS, llm_context_models)
        print("-------------------")
        print('\n'.join([x['title'] for x in chosen_videos]))

        for entry in chosen_videos:
            video_id = entry["id"]
            title = entry["title"]
            url = entry["webpage_url"]
            description = entry.get("description", "")

            downloader.download([url])
            
            channel = entry.get("uploader") or entry.get("channel") or "Unknown"
            duration = entry.get("duration", 0)
            views = entry.get("view_count", 0)

            vtt_path = os.path.join(tempdir, f"{video_id}.en.vtt")
            
            try:
                with open(vtt_path, 'r', encoding='utf-8') as f:
                    subtitles = f.readlines()
            except FileNotFoundError:
                print(f"Subtitles not found for {video_id}. Skipping.")
                continue

            subtitles = subtitles[3:]
            subtitles = [r for r in subtitles if not re.match("^\\s*\n", r)]
            subtitles = [re.sub("<[^>]*>","",r) for r in subtitles]

            complete = []
            prev = ''
            time_str = None
            for r in subtitles:
                if r != prev:
                    if mm := re.match("^([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{3})", r):
                        time_str = mm.group(1) 
                    else:
                        complete.append({
                            't': time_str if 'time_str' in locals() else None, 
                            's': r.strip()
                            })
                        prev = r
            
            results = complete

            valid_videos.append({
                "video_id": video_id,
                "title": title,
                "description": description,
                "channel": channel,
                "duration": duration,
                "views": views,
                "url": url,
                "subtitles_data": results, 
                "copyright_note": f"'{title}' by {channel} on YouTube."
            })

        if valid_videos is None or len(valid_videos) == 0:
            return jsonify({
                'success': False,
                'status': 'warning',
                'error': f'The research for "{research}" did not produce any results. Please try with a different device name.'
            }), 404
            
        output_dir = "subtitles"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{research.replace(' ', '_')}_subtitles_{timestamp}.json"
        output_path = os.path.join(output_dir, output_filename)
    
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_videos, f, ensure_ascii=False, indent=2)

        return "ok", valid_videos
