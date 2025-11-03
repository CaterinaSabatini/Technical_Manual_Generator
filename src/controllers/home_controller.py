from flask import render_template, request, jsonify
from .subtitles_controller import get_subtitles
import sqlite3

def formatta_nome(prod, fam, subfam, showsubfam, model):
    pezzi = []
    if prod is not None:
        pezzi.append(prod)
    if fam is not None:
        pezzi.append(fam)
    if subfam is not None and showsubfam != 1:
        pezzi.append(subfam)
    if model is not None:
        pezzi.append(model)
    return ' '.join(map(str, pezzi))


"""
Home controller to render the home page with device models and handle subtitle search requests.
@return HTML template for home page with device models.
"""
def home_controller():
    database = sqlite3.connect("devices_database/modelli.sqlite")
    cur = database.cursor()
    res = cur.execute("SELECT MODEL.prod,MODEL.model,FAMILIES.fam,FAMILIES.subfam,FAMILIES.showsubfam FROM MODEL JOIN FAMILIES ON MODEL.idfam = FAMILIES.id;")
    res = [formatta_nome(x[0],x[2],x[3],x[4],x[1]) for x in res]
    res.sort()
    return render_template('home.html', models=res)

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
        
        database = sqlite3.connect("devices_database/modelli.sqlite")
        cur = database.cursor()
        allowed_names = cur.execute("SELECT MODEL.prod,MODEL.model,FAMILIES.fam,FAMILIES.subfam,FAMILIES.showsubfam FROM MODEL JOIN FAMILIES ON MODEL.idfam = FAMILIES.id;")
        allowed_names = [formatta_nome(x[0],x[2],x[3],x[4],x[1]) for x in allowed_names]

        if device not in allowed_names:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Device name is not a known device'
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
