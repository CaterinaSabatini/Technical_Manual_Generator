import os
import atexit
from flask import Flask
from dotenv import load_dotenv
from controllers.home_controller import home_controller, search_subtitles_api
from controllers.llm_controller import ensure_ollama_up, terminate_ollama

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return home_controller()

if not ensure_ollama_up():
            raise ConnectionError("Unable to connect or start Llama. Please retry later.")

# Ensure Ollama is terminated when the application exits
atexit.register(terminate_ollama)

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
    app.run(host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'), debug=os.getenv('FLASK_DEBUG'))
