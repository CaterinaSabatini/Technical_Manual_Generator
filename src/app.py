import os
import atexit
from flask import Flask
from dotenv import load_dotenv
from controllers.home_controller import home_controller, manual_generation_api, show_manual
from controllers.llm_controller import start_ollama, stop_ollama

# Load environment variables from .env file
load_dotenv()

OLLAMA_PATH = os.getenv('OLLAMA_PATH')
OLLAMA_TEST = os.getenv('OLLAMA_TEST')
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))
RETRY_DELAY = float(os.getenv('RETRY_DELAY'))
REQUEST_TIMEOUT = float(os.getenv('REQUEST_TIMEOUT'))

app = Flask(__name__)

# Start Ollama LLM service
ollama_process = start_ollama(OLLAMA_PATH, OLLAMA_TEST, MAX_RETRIES, RETRY_DELAY, REQUEST_TIMEOUT)

# Ensure Ollama is terminated when the application exits
atexit.register(lambda: stop_ollama(ollama_process))

# API route for home page
@app.route('/')
def index():
    return home_controller()

# API route for manual generation
@app.route('/api/manual-generation', methods=['POST'])
def manual_generation():
    return manual_generation_api()

# Route to display generated manual
@app.route('/api/manual/<manual_id>')
def display_manual(manual_id):
    return show_manual(manual_id)

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'), debug=os.getenv('FLASK_DEBUG'))
