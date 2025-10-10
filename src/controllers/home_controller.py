from flask import render_template, request, jsonify
from .subtitles_controller import get_subtitles

def home_controller():
    """Home page controller"""
    return render_template('home.html')

def search_subtitles_api():
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
        
        get_subtitles(device)
        
        return jsonify({
            'success': True,
            'status': 'ok',
            'device': device,
            'message': f'Subtitle search completed for "{device}"',
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'{str(e)}'
        }), 500