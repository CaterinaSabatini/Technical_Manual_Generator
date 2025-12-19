from flask import render_template, request, jsonify, send_file
import time
import json
import os
from .subtitles_controller import get_subtitles
from .manual_controller import report_llm

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

        if status != "ok" or not subtitles_data:
            return jsonify({
                'success': False,
                'error': 'No subtitles found for the specified device. Try with a more specific model name.'
            }), 404
        
        html_guide = report_llm(subtitles_data) 

        if not html_guide or not isinstance(html_guide, str):
            print("DEBUG FALLITO: report_llm ha restituito una stringa HTML vuota o non valida.")
            return jsonify({
                'success': False,
                'error': 'Failed to generate a valid manual (HTML expected).'
            }), 500
        
        try:
            escaped_guide = json.dumps(html_guide, ensure_ascii=False)
            #safe_html_guide = escaped_guide[1:-1]
            safe_html_guide = html_guide
            
        except Exception as e:
            print(f"ERRORE DI ESCAPING: {e}. Usando la stringa originale.")
            safe_html_guide = html_guide

        print(f"DEBUG SUCCESSO: Guida HTML generata (lunghezza: {len(html_guide)})")
        
        print(f"DEBUG HTML LENGTH: {len(html_guide)}")
        print(f"DEBUG HTML SAMPLE: {html_guide[:200]}")

        return jsonify({
            'success': True,
            'html': safe_html_guide 
        }), 200

    except Exception as e:
        print(f"Unexpected server error: {e}")
        return jsonify({
            'success': False,
            'error': f'Unexpected server error: {e}' 
        }), 500

"""
Handle PDF download requests via API.

@return PDF file response for download.
"""    
def download_pdf_api():
    
    try:
        device = request.args.get('device', '').strip()
        if not device:
            return {"error": "Device parameter is required"}, 400

        manuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'manuals')
        if not os.path.exists(manuals_dir):
            return {"error": "Manuals directory not found"}, 500

        safe_device_name = device.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # If multiple versions exist, you could pick the latest
        pdf_files = [f for f in os.listdir(manuals_dir) if f.startswith(safe_device_name) and f.endswith('.pdf')]

        if not pdf_files:
            return {"error": f"No manual found for device '{device}'"}, 404

        # Pick the latest file based on creation time
        pdf_files.sort(key=lambda f: os.path.getctime(os.path.join(manuals_dir, f)), reverse=True)
        pdf_path = os.path.join(manuals_dir, pdf_files[0])

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"TechGuide_Manual_{safe_device_name}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error in download_pdf_api: {str(e)}")
        return {"error": str(e)}, 500
