from flask import render_template, request, jsonify
from .subtitles_controller import get_subtitles
import sqlite3

def home_controller():
    """Home page controller"""
    database = sqlite3.connect("../modelli.sqlite")
    cur = database.cursor()
    res = cur.execute("SELECT PROD, MODEL, SUBMODEL FROM MODELS ORDER BY PROD,MODEL,SUBMODEL;").fetchall()
    res = [' '.join(x) for x in res]
    return render_template('home.html', models=res)

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
