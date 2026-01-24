import os
import atexit
from flask import Flask
from dotenv import load_dotenv
from controllers.home_controller import home_controller, manual_generation_api, show_manual, download_pdf_api
from controllers.llm_controller import ensure_ollama_up, terminate_ollama

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# API route for home page
@app.route('/')
def index():
    return home_controller()

# Ensure Ollama LLM service is running before handling requests
if not ensure_ollama_up():
            raise ConnectionError("Unable to connect or start Llama. Please retry later.")

# Ensure Ollama is terminated when the application exits
atexit.register(terminate_ollama)

# Route to display generated manual
@app.route('/api/manual/<manual_id>')
def display_manual(manual_id):
    return show_manual(manual_id)

# API route for manual generation
@app.route('/api/manual-generation', methods=['POST'])
def manual_generation():
    return manual_generation_api()

# API route for downloading PDF
@app.route('/api/download-pdf')
def download_pdf():
    return download_pdf_api()

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'), debug=os.getenv('FLASK_DEBUG'))
