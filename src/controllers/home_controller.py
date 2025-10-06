from flask import render_template, request, jsonify, make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from yt_dlp import YoutubeDL
import re
import io
import datetime
import os
import json
import tempfile


# Device data loader functions
def load_device_index():
    """Load device index from JSON file"""
    device_results_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'device_results')
    index_file = os.path.join(device_results_path, 'device_index.json')
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading device index: {e}")
        return {"devices": []}

def load_device_data(device_name):
    """Load specific device data from JSON file"""
    device_results_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'device_results')
    
    # Load index to find the correct file
    index_data = load_device_index()
    device_file = None
    
    for device in index_data['devices']:
        if device['display_name'] == device_name:
            device_file = device['file_name']
            break
    
    if not device_file:
        return None
    
    device_file_path = os.path.join(device_results_path, device_file)
    
    try:
        with open(device_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading device data for {device_name}: {e}")
        return None

def get_supported_devices():
    """Get list of supported device names"""
    index_data = load_device_index()
    return [device['display_name'] for device in index_data['devices']]
    
def home_controller():
    """Home page controller"""
    return render_template('home.html')

def generate_manual_api():
    """API Controller for generating technical manuals with strict device validation"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Check if data exists
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided in request'
            }), 400
        
        device = data.get('device', '').strip()
        
        # Check if device field is empty
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device name is required and cannot be empty'
            }), 400
        
        # Strict validation: device must match exactly
        supported_devices = get_supported_devices()
        if device not in supported_devices:
            return jsonify({
                'success': False,
                'error': f'Device "{device}" not found.'
            }), 404
        
        # Device found - load data and render manual HTML
        
        manual_data = load_device_data(device)
        if not manual_data:
            return jsonify({
                'success': False,
                'error': f'Error loading data for device "{device}"'
            }), 500
            
        timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        manual_html = render_template('manual_partial.html', 
                                    device=device, 
                                    manual=manual_data,
                                    timestamp=timestamp)
        
        return jsonify({
            'success': True,
            'device': device,
            'html': manual_html
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

def generate_pdf_manual(device_name):
    """Generate PDF manual for the specified device"""
    supported_devices = get_supported_devices()
    if device_name not in supported_devices:
        return None
    
    device_data = load_device_data(device_name)
    if not device_data:
        return None
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create PDF document with metadata
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
        title=f"Technical Repair Manual - {device_name}",
        author="TechGuide System",
        subject=f"Repair manual for {device_name}",
        creator="TechGuide PDF Generator",
        keywords=f"repair, manual, {device_name}, technical, guide"
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor='blue'
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(f"Technical Repair Manual", title_style))
    story.append(Paragraph(f"{device_name}", title_style))
    story.append(Spacer(1, 20))
    
    # Device info
    story.append(Paragraph("Device Information", heading_style))
    story.append(Paragraph(f"<b>Model:</b> {device_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Manufacturer:</b> {device_data['manufacturer']}", styles['Normal']))
    story.append(Paragraph(f"<b>Category:</b> {device_data['category'].title()}", styles['Normal']))
    story.append(Paragraph(f"<b>Difficulty:</b> {device_data['difficulty']}", styles['Normal']))
    story.append(Paragraph(f"<b>Estimated Time:</b> {device_data['time_estimate']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Tools
    story.append(Paragraph("Required Tools", heading_style))
    for i, tool in enumerate(device_data['tools'], 1):
        story.append(Paragraph(f"{i}. {tool}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Warnings
    story.append(Paragraph("SAFETY WARNINGS", heading_style))
    for warning in device_data['warnings']:
        story.append(Paragraph(f"• {warning}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Steps
    story.append(Paragraph("Repair Steps", heading_style))
    for i, step in enumerate(device_data['steps'], 1):
        story.append(Paragraph(f"{i}. {step}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph(
        f"Generated on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} by TechGuide",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

def download_pdf_api():
    """API endpoint to download PDF manual and save locally"""
    try:
        device = request.args.get('device', '').strip()
        
        if not device:
            return jsonify({'error': 'Device parameter is required'}), 400
        
        supported_devices = get_supported_devices()
        if device not in supported_devices:
            return jsonify({'error': f'Device "{device}" not supported'}), 404
        
        # Generate PDF
        pdf_buffer = generate_pdf_manual(device)
        
        if not pdf_buffer:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Create manuals directory if it doesn't exist
        manuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'manuals')
        os.makedirs(manuals_dir, exist_ok=True)
        
        # Save PDF to local manuals folder
        filename = f"{device.replace(' ', '_').replace('/', '_')}_manual_{datetime.datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
        local_path = os.path.join(manuals_dir, filename)
        
        # Read buffer content for local saving
        pdf_content = pdf_buffer.read()
        
        # Save to local file
        with open(local_path, 'wb') as f:
            f.write(pdf_content)
        
        # Create response for download with proper filename
        safe_device_name = device.replace(' ', '_').replace('/', '_').replace('\\', '_')
        download_filename = f"TechGuide_Manual_{safe_device_name}.pdf"
        
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        
        print(f"PDF saved locally at: {local_path}")
        
        return response
        
    except Exception as e:
        print(f"Error in download_pdf_api: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_sottotitoli(ricerca):

    dd = tempfile.TemporaryDirectory()
    tempdir = dd.name
    downloader = YoutubeDL({"skip_download": True,
                            "writeautomaticsub": True,
                            "outtmpl": {
                                "subtitle": f"{tempdir}/%(id)s"
                                }
                            })

    data = downloader.extract_info(f"ytsearch1:{ricerca}")

    with open(f"{tempdir}/data.json", "w") as f:
        json.dump(data, f)
    with open(f"{tempdir}/{data['entries'][0]['id']}.en.vtt", 'r') as f:
        sottotitoli = f.readlines()

    sottotitoli = sottotitoli[3:]
    sottotitoli = [r for r in sottotitoli if not re.match("^\\s*\n", r)]
    sottotitoli = [r for r in sottotitoli if not re.match("^[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3} --> [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}", r)]
    sottotitoli = [re.sub("<[^>]*>","",r) for r in sottotitoli]
    prev = ''
    puliti = []

    for r in sottotitoli:
        if r != prev:
            puliti.append(r)
            prev = r
    return ''.join(puliti)

