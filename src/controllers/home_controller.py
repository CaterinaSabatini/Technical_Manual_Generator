from flask import render_template, request, jsonify, abort
import os
import json
import datetime
from .subtitles_controller import get_subtitles
from .manual_controller import report_llm

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
    try:
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
        
        manual_id = report_llm(subtitles_data, device) 

        if not manual_id or (isinstance(manual_id, tuple) and manual_id[0] == "error"):
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Failed to generate a valid manual'
            }), 500
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manuals_dir = os.path.join(base_dir, "..", "device_manuals")
        json_path = os.path.join(manuals_dir, manual_id)
        
        if not os.path.exists(json_path):
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Manual was generated but file could not be saved. Please try again.'
            }), 500

        return jsonify({
            'success': True,
            'manual_id': manual_id
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': 'An unexpected error occurred. Please try again later'
        }), 500
    

"""
Render the manual page based on manual ID.
@param manual_id: ID of the manual to be displayed.
@return HTML template for manual page.
"""
def show_manual(manual_id):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    manuals_dir = os.path.join(base_dir, "..", "device_manuals")
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

    return render_template(
        "manual.html",
        device_name=data["device"],
        manual_content=data["manual_text"],
        timestamp=data["timestamp"],
        video_sources=video_sources
    )


