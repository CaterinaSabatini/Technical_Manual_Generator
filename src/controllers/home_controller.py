from flask import render_template, request, jsonify
from .subtitles_controller import get_sottotitoli

def home_controller():
    """Home page controller"""
    return render_template('home.html')

def search_subtitles_api():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided in request'
            }), 400
        
        device = data.get('device', '').strip()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device name is required'
            }), 400
        
        get_sottotitoli(device)
        
        return jsonify({
            'success': True,
            'device': device,
            'message': f'Subtitle search completed for "{device}"',
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error during subtitle search: {str(e)}'
        }), 500