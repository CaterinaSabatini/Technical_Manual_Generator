from flask import render_template, request, jsonify
from .subtitles_controller import get_subtitles

"""
Home controller to render the home page with device models and handle subtitle search requests.
@return HTML template for home page with device models.
"""
def home_controller():
    return render_template('home.html')

"""
Handle subtitle search requests via API.
@return JSON response indicating success or failure of the subtitle search.
"""
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
        
        (status,search_result) = get_subtitles(device)
        print(f"========={status}===========")
        print(search_result)

        if isinstance(search_result, tuple):
            return search_result
        
        return jsonify({
            'success': True,
            'status': 'ok',
            'device': device,
            'message': f'Subtitle search completed for "{device}"',
            'html': search_result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': f'An error occurred during manual search. Please try again later.'
        }), 500
