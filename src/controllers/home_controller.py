from flask import render_template, request, jsonify, abort
import os
import json
import datetime
from .subtitles_controller import get_subtitles
from .manual_controller import report_llm

COEF_VIEW = float(os.getenv('COEF_VIEW'))
COEF_LIKE = float(os.getenv('COEF_LIKE'))

"""
Home controller to render the home page.
@return HTML template for home page.
"""
def home_controller():
    return render_template('home.html')

"""
Handle manual generation requests via API.
@return JSON response with manual ID or error message.
"""

def manual_generation_api():
#    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'No data provided in request'
            }), 400
        
        device = data.get('device', '').strip()
        
        if not device:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Device name is required'
            }), 400
        

        status, subtitles_data = get_subtitles(device)

        if status == "device_not_found":
            return jsonify({
                'success': False,
                'status': 'device_not_found',
                'error': 'Device not found in database. Please check the model name and try again.'
            }), 404
        
        if status != "ok" or not subtitles_data:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'No subtitles found for the specified device. Try with a more specific model name'
            }), 404
        
        report_ids = []
        for video in subtitles_data:
            start_time = datetime.datetime.now()
            nuovo_id = report_llm(video, device)
            end_time = datetime.datetime.now()
            report_ids.append(nuovo_id)
            print(len(report_ids),nuovo_id, f"time: {end_time-start_time}")

        for report_id in report_ids:
            if not report_id or (isinstance(report_id, tuple) and report_id[0] == "error"):
                return jsonify({
                    'success': False,
                    'status': 'error',
                    'error': 'Failed to generate a valid manual'
                }), 500
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            reports_dir = os.path.join(base_dir, "..", "video_reports")
            json_path = os.path.join(reports_dir, report_id)
            
            if not os.path.exists(json_path):
                return jsonify({
                    'success': False,
                    'status': 'error',
                    'error': 'Manual was generated but file could not be saved. Please try again.'
                }), 500

        return jsonify({
            'success': True,
            'manual_id': report_ids
        }), 200

#    except Exception:
#        return jsonify({
#            'success': False,
#            'status': 'error',
#            'error': 'An unexpected error occurred. Please try again later'
#        }), 500
    

"""
Render the manual page based on manual ID.
@param manual_id: ID of the manual to be displayed.
@return HTML template for manual page.
"""
def show_manual(manual_id_list):

    max_view = 0
    max_like = 0
    videos = []
    for manual_id in manual_id_list:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manuals_dir = os.path.join(base_dir, "..", "video_reports")
        json_path = os.path.join(manuals_dir, manual_id)

        if not os.path.exists(json_path):
            abort(404)

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        video_sources = []
        channels = data.get("channels", [])
        urls = data.get("urls", [])

        for i in range(max(len(channels), len(urls))):
            channel = channels[i] if i < len(channels) else "Unknown Channel"
            url = urls[i] if i < len(urls) else "#"
            video_sources.append({"channel": channel, "url": url})

        vs = data["view_score"]
        ls = data["like_score"]
        videos.append({
            "device_name": data["device"],
            "manual_content": data["manual_text"],
            "video_sources": video_sources,
            "timestamp": data["timestamp"],
            "title": data["title"],
            "view_score": vs,
            "like_score": ls
            })
        if vs > max_view:
            max_view = vs
        if ls > max_like:
            max_like = ls

    for i in range(len(videos)):
        videos[i]["view_score"] /= max_view
        videos[i]["like_score"] /= max_like
        videos[i]["score"] = (videos[i]["view_score"]*COEF_VIEW + videos[i]["like_score"]*COEF_LIKE)*100/(COEF_VIEW+COEF_LIKE)

    videos.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "manual.html",
        videos=videos
    )


