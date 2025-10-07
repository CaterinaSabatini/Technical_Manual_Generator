import os
from flask import Flask
from dotenv import load_dotenv
from controllers.home_controller import home_controller, search_subtitles_api

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return home_controller()

@app.route('/api/search-subtitles', methods=['POST'])
def search_subtitles():
    return search_subtitles_api()

"""
@app.route('/api/generate', methods=['POST'])
def generate_manual():
 
return generate_manual_api()

@app.route('/api/download-pdf')
def download_pdf():
    return download_pdf_api()
"""
if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=os.getenv('FLASK_DEBUG'))
