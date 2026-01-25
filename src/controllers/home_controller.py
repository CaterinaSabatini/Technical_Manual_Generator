from flask import render_template, request, jsonify, send_file, abort
import os
import json
import datetime
from .subtitles_controller import get_subtitles
from .manual_controller import report_llm

"""
Home controller to render the home page with device models and handle subtitle search requests.
@return HTML template for home page with device models.
"""
def home_controller():
    return render_template('home.html')

"""
Handle manual generation requests via API.
@return JSON response with generated HTML manual or error message.
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
                'status': 'error',
                'error': 'No subtitles found for the specified device. Try with a more specific model name'
            }), 404
        
        manual_id = report_llm(subtitles_data, device) 

        # report_llm può ritornare una tupla ("error", None) in caso di errore
        if not manual_id or (isinstance(manual_id, tuple) and manual_id[0] == "error"):
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Failed to generate a valid manual'
            }), 500
        
        # Verify that the file was actually created
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manuals_dir = os.path.join(base_dir, "..", "device_manuals")
        json_path = os.path.join(manuals_dir, manual_id)
        
        if not os.path.exists(json_path):
            print(f"Manual file not found: {json_path}")
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Manual was generated but file could not be saved. Please try again.'
            }), 500

        return jsonify({
            'success': True,
            'manual_id': manual_id
        }), 200

    except Exception as e:
        print(f"Unexpected server error: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': 'An unexpected error occurred. Please try again later'
        }), 500
    

def show_manual(manual_id):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    manuals_dir = os.path.join(base_dir, "..", "device_manuals")
    json_path = os.path.join(manuals_dir, manual_id)

    if not os.path.exists(json_path):
        abort(404)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    return render_template(
        "manual.html",
        device_name=data["device"],
        manual_content=data["manual_text"],
        timestamp=data["timestamp"]
    )


"""
Handle PDF manual download requests via API.
@return PDF file response for download.
"""    
def download_pdf_api():
    
    try:
        device = request.args.get('device', '').strip()

        if not device:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Device parameter is required'
            }), 400

        manuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'manuals')
        
        if not os.path.exists(manuals_dir):
            return jsonify({
                'success': False,
                'status': 'error',
                'error': 'Manuals directory not found'
            }), 500

        safe_device_name = device.replace(' ', '_').replace('/', '_').replace('\\', '_')
        
        # Find all PDFs matching the device name (pick latest if multiple exist)
        pdf_files = [f for f in os.listdir(manuals_dir) if f.startswith(safe_device_name) and f.endswith('.pdf')]

        if not pdf_files:
            return jsonify({
                'success': False,
                'status': 'error',
                'error': f'No manual found for device \'{device}\''
            }), 404

        # Sort by creation time and pick the most recent
        pdf_files.sort(key=lambda f: os.path.getctime(os.path.join(manuals_dir, f)), reverse=True)
        pdf_path = os.path.join(manuals_dir, pdf_files[0])

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"TechGuide_Manual_{safe_device_name}.pdf",
            mimetype='application/pdf'
        )

    except Exception:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': 'An unexpected error occurred. Please try again later'
        }), 500
