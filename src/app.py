import os
from flask import Flask
from flask import request
from flask import Response
from dotenv import load_dotenv
from controllers.home_controller import home_controller, generate_manual_api, download_pdf_api, get_sottotitoli

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return home_controller()

@app.route('/api/generate', methods=['POST'])
def generate_manual():
    return generate_manual_api()

@app.route('/api/download-pdf')
def download_pdf():
    return download_pdf_api()

@app.route('/api/sottotitoli')
def sottotitoli_rotta():
    ricerca = request.args.get('q',"How most 16\" Macbook Pros often kill themselves & why they're unfixable")
    return Response(get_sottotitoli(ricerca), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=os.getenv('FLASK_DEBUG'))
