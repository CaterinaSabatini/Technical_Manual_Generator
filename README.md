<h1 align="center">Technical Manual Generator</h1>


<div align="center">

[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/stable/)
[![GitHub](https://img.shields.io/badge/GitHub-121011?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Jinja](https://img.shields.io/badge/Jinja-000000?style=for-the-badge&logo=jinja&logoColor=white)](https://jinja.palletsprojects.com/en/stable/templates/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![Python](https://img.shields.io/badge/Python-0376D6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![VSCode](https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![yt_dlp](https://img.shields.io/badge/yt_dlp-%23000000?style=for-the-badge&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
</div>

## 📖 Introduction 
**Technical Manual Generator** is an intelligent system that automatically creates comprehensive disassembly manuals for laptops by analyzing YouTube teardown videos. The application searches for relevant videos, extracts and validates content, and uses Large Language Models (LLMs) to synthesize technical documentation.

### ✨ Main Features

- **Automated Subtitle Extraction**: downloads and processes subtitles from YouTube teardown videos
- **AI-Powered Content Validation**: uses LLM to analyze and select the most relevant content from multiple video sources
- **Intelligent Manual Generation**: synthesizes technical disassembly manuals using Ollama LLMs
- **Web Interface**: clean, responsive UI for easy device search and manual viewing
- **Archive**: all video subtitles and generated manuals are saved in JSON format

### 🔄 How It Works

1. **User Input**: user enters a device name (e.g., "MacBook Pro 14")
2. **Database Matching**: system matches the searched device with the database to find the correct subtitles.
3. **Video Discovery**: searches YouTube for teardown videos for the searched device
4. **Content Validation**: filters videos based on configurable criteria (views, duration, like ratio)
5. **LLM Filtering**: uses AI to select the most relevant videos from candidates
6. **Subtitle Processing**: extracts and cleans subtitles from chosen videos
7. **Manual Synthesis**: LLM generates a structured technical manual from the subtitle content
8. **Output**: returns a manual viewable in the browser

### 🛠️ Technologies Used
The application is developed using the following technologies:

- [Python](https://www.python.org/) as the main programming language
- [Flask](https://flask.palletsprojects.com/en/stable/) as the web framework for building the REST API and serving the web interface
- [Ollama](https://ollama.com) for running Large Language Models locally
- [SQLite](https://www.sqlite.org/) for storing and querying the device database
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading video metadata and subtitles from YouTube
- [HTML5](https://developer.mozilla.org/en-US/docs/Web/HTML), [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS), and [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) for the frontend user interface

## 📁 Project Structure

```
Technical_Manual_Generator/
├── src/
│   ├── app.py                          # Flask application entry point and route definitions
│   ├── controllers/
│   │   ├── home_controller.py          # Home page, manual generation, and display handlers
│   │   ├── llm_controller.py           # Ollama service management
│   │   ├── manual_controller.py        # Manual generation logic
│   │   ├── subtitles_controller.py     # YouTube video processing
│   │   └── video_validator_controller.py # Video filtering logic
│   ├── device_manuals/                 # Generated manuals (JSON)
│   ├── devices_database/
│   │   ├── device.sqlite               # Device model database
│   │   └── modelli.sql                 # Database schema
│   ├── static/
│   │   ├── css/style.css               # Styling
│   │   └── js/home.js                  # Frontend interactivity
│   ├── subtitles/                      # Downloaded subtitle files
│   ├── templates/
│   │   ├── home.html                   # Search page
│   │   └── manual.html                 # Manual display page
│   └── utils/
│       ├── create_db.py                # Database creation utility
│       ├── prompt_manual.txt           # LLM prompt for manual generation
│       └── prompt_subtitles.txt        # LLM prompt for video selection
├── .env                                # Environment configuration
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
└── LICENSE                             # License information
```

### 🗄️ Database Structure

The SQLite database at `src/devices_database/device.sqlite` contains device information with the following schema:

**Table: `devices**

| Column | Type | Description |
|--------|------|-------------|
| `ID` | INTEGER | Primary key (auto-increment) |
| `DEVICE` | TEXT | Complete name of the device|

## 🚀 Getting Started
To run a local copy of the application, follow the steps below. 

### ✅ Prerequisites
Ensure the following tools are installed on your computer:

- **Python 3.12**: you can install Python by following this [link](https://www.python.org/downloads/)
- **Ollama**: you can install Ollama by folllowing this ([link](https://ollama.com))
- **Ollama Model**: `llama3.2:latest` pulled and available
- **SQLite**: pre-installed with Python
- **Internet Connection**: required for YouTube video access

> 💡 **NOTE**: This web app is tested with *Python 3.12* and the `llama3.2:latest` model on *Linux* and *Windows 11*. It *may* work with other versions and operating systems (e.g., macOS), but we cannot guarantee compatibility.

### 🔧 Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/CaterinaSabatini/Technical_Manual_Generator.git
   cd Technical_Manual_Generator
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama and download the model**
   
   - Download and install Ollama from [ollama.com](https://ollama.com)
   - Once installed, start Ollama and pull the required model:
     ```bash
     ollama serve
     ```
     Open a new terminal and run:
     ```bash
     ollama pull llama3.2:latest
     ```
   - Verify the model is installed:
     ```bash
     ollama list
     ```
>  💡 **NOTE**: After that, the Ollama model is started and managed by the application itself, so you do not need to start Ollama manually.

4. **Configure environment variables**
   
   Create a `.env` file in the project root following this schema (or copy from `.env.example`):

   ```env
   # Flask configuration
   FLASK_APP=src/app.py
   FLASK_ENV=
   FLASK_DEBUG=
   FLASK_HOST=localhost
   FLASK_PORT=5000

   # Ollama configuration
   OLLAMA_PATH=
   OLLAMA_URL=http://localhost:11434/api/generate
   OLLAMA_TEST=http://localhost:11434/api/tags
   OLLAMA_MODEL=llama3.2:latest
   PROMPT_SUBTITLES=utils/prompt_subtitles.txt
   PROMPT_MANUAL=utils/prompt_manual.txt
   MAX_RETRIES=
   RETRY_DELAY=
   REQUEST_TIMEOUT=

   # Database configuration
   DB_PATH=devices_database/device.sqlite

   # Video analysis parameters
   MAX_SEARCH=
   MAX_VIDEOS=
   MIN_VIEWS=
   MIN_DURATION=        # seconds
   MAX_DURATION=        # 1 hour
   MIN_LIKE_RATIO=      # 70% likes vs total votes
   ```

   **Environment Variables Explanation:**

  **Flask Configuration:**
   - `FLASK_APP`: path to the main Flask application file (default: `src/app.py`)
   - `FLASK_ENV`: environment mode - `development` for debugging, `production` for deployment
   - `FLASK_DEBUG`: enables/disables debug mode - `True` for development, `False` for production
   - `FLASK_HOST`: host address where Flask runs (default: `localhost`)
   - `FLASK_PORT`: port number for the Flask server (default: `5000`)

   **Ollama Configuration:**
   - `OLLAMA_PATH`: absolute path to the Ollama executable on your system
   - `OLLAMA_URL`: API endpoint for Ollama text generation (default: `http://localhost:11434/api/generate`)
   - `OLLAMA_TEST`: API endpoint to verify Ollama connection (default: `http://localhost:11434/api/tags`)
   - `OLLAMA_MODEL`: name of the Ollama model to use (default: `llama3.2:latest`)
   - `PROMPT_SUBTITLES`: relative path to the prompt template for video selection
   - `PROMPT_MANUAL`: relative path to the prompt template for manual generation
   - `MAX_RETRIES`: maximum connection attempts to Ollama before failing
   - `RETRY_DELAY`: seconds to wait between connection retry attempts
   - `REQUEST_TIMEOUT`: maximum seconds to wait for Ollama response

   **Database Configuration:**
   - `DB_PATH`: relative path to the SQLite database containing device models

   **Video Analysis Parameters:**
   - `MAX_SEARCH`: maximum number of YouTube videos to search and evaluate
   - `MAX_VIDEOS`: maximum number of videos to process for manual generation
   - `MIN_VIEWS`: minimum view count required for a video to be considered
   - `MIN_DURATION`: minimum video length in seconds (filters out too-short videos)
   - `MAX_DURATION`: maximum video length in seconds (filters out too-long videos)
   - `MIN_LIKE_RATIO`: minimum like-to-total-votes ratio (0.7 = 70% likes minimum) 


5. **Set up the database**
   
   The device database should already exist at `src/devices_database/device.sqlite`. If it does not, you can create it by running  `src/utils/create_db.py`.

## 💻 Usage

### Starting the Application

You can start the application using either of the following methods:

**Option A: Using Flask CLI (from project root)**
```bash
flask run
```

**Option B: Using Python directly (from src directory)**
```bash
cd src
python app.py
```

Once the server is running, open your browser and navigate to `http://localhost:5000`

### Generating a Manual

1. Enter a device name in the search box (e.g., *MacBook Pro 14*, *Dell Inspiron 15*)
2. Click *Search*
3. Wait for the process to complete 
4. View the generated manual in your browser


### API Endpoints

- `GET /` - Home page with search interface
  
- `POST /api/manual-generation` - Generate manual for a device
  ```json
  Request Body:
  {
    "device": "MacBook Pro 14"
  }
  
  Response:
  {
    "success": true,
    "manual_id": "macbook_pro_14_28-01-2026_12-00-00.json"
  }
  ```
- `GET /api/manual/<manual_id>` - View a specific manual
---

## 🛑 Troubleshooting

### Common Issues

**Ollama Connection Failed**
- Ensure Ollama is running
- Check `OLLAMA_URL` in `.env` matches your Ollama port
- Verify model is installed

**Device Not Found in Database**
- Database is case-insensitive but requires 4+ characters and 3+ words
- Try more specific model names (e.g., *Acer Aspire 1 15  A115-32" vs *Acer Aspire 1*)
- Check database exists at `src/devices_database/device.sqlite`

> 💡 **NOTE**: Subtitle results depend on YouTube content. For some models, subtitles cannot be generated if there are no available videos.

**YouTube Request Limits**
- YouTube imposes limits on how many requests you can make in a given time period when downloading video data or subtitles.
- Excessive requests in a short timeframe can trigger rate limiting errors (e.g., HTTP 429).
- These limits are part of YouTube’s official API quota and request policies; once the quota is exhausted, requests may be blocked until reset.

>  💡 **NOTE**: Sometimes it may be necessary to update the yt-dlp library due to changes in YouTube’s policies.

---

## ⚠️ Limitations

**Manual Accuracy**

The generated manuals may contain inaccuracies or incomplete information due to two main factors:

1. **YouTube Content Dependency**: The quality and accuracy of the manuals directly depend on the available YouTube video content. If teardown videos are incomplete, unclear, or incorrect, the generated manual will reflect these limitations.

2. **Model Size Constraints**: This application uses the `llama3.2:latest` model with only **3 billion parameters**. While functional, smaller models have limited reasoning capabilities compared to larger alternatives (e.g., 7B, 13B, or 70B parameter models).

> 💡 **Recommendation**: The choice of a 3B model was made to accommodate hardware constraints during development. For improved accuracy and more detailed manuals, we recommend using a larger Ollama model if your system has sufficient resources (RAM/GPU). You can switch models by updating the `OLLAMA_MODEL` variable in your `.env` file and pulling the desired model with `ollama pull <model_name>`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---