# Project Overview

<p align="center">
  <a href="#-features">🚀 Features</a> • 
  <a href="#️-tech-stack">🛠️ Tech Stack</a> • 
  <a href="#-prerequisites">📋 Prerequisites</a>  • 
  <a href="#-setup">📋 Setup</a>   • 
    <a href="#architecture">📋 Architecture</a>
</p>

### AI Orchestration Layer with Flask Web UI

A powerful, local-first AI orchestration layer that unifies advanced LLM reasoning, real-time voice synthesis, and local system automation. Featuring a Flask-based web interface, this system uses a smart Gemini API rotation strategy with a Groq fallback, allowing it to seamlessly perform CRUD operations on files, automate OS tasks via PyAutoGUI, tell jokes, and act as a fully capable local AI assistant.


<img width="1920" height="913" alt="image" src="https://github.com/user-attachments/assets/929eef8b-583d-4fe6-b982-df7f7bdad421" />


## 🚀 Features

### 🧠 Intelligent Brain & Routing
* **Gemini API Rotator:** Automatically rotates through multiple Gemini API keys to maximize rate limits and prevent service interruptions.
* **Groq API Fallback:** Instantly falls back to Groq's ultra-low latency API if all Gemini keys are exhausted or rate-limited.

### 🎙️ Audio & Voice
* **Kokoro-82M Voice Synthesis:** Integrated with the lightweight, highly efficient Kokoro-82M model for natural, low-latency text-to-speech (TTS) responses.

### 💻 System Automation (OS Agent)
* **PyAutoGUI Simulation:** Grants the AI the ability to interact with the host OS—opening/closing applications, typing, and taking screenshots.
* **File & Folder CRUD:** Full workspace management allowing the agent to create, read, update, and delete files or directories safely via natural language.

### 🌐 Web Interface
* **Flask Web UI:** A clean, responsive front-end dashboard to interact with the assistant, view logs, and monitor system tasks in real-time.

---

## 🛠️ Tech Stack

* **Backend Framework:** Flask (Python)
* **LLM Providers:** Google Gemini API, Groq API
* **TTS Engine:** Kokoro-82M Model
* **OS Automation:** PyAutoGUI,keyboard, Python `os` & `shutil` libraries
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API / WebSockets)

---

## 📋 Prerequisites

Before setting up, ensure you have the following installed on your host machine:
* Python 3.10 or higher
* Pip (Python package manager)
* *Note for Linux users:* PyAutoGUI may require `scrot`, `python3-tk`, and `python3-dev` installed via your system package manager. Besides `PyAutoGUI` does not work properly in wayland [use x11 instead]

## 📋 Setup

* Clone this repository locally using `git clone https://github.com/idcnys/jarvis.git .` command
* Create a virtual env using `python -m venv [name]` , activate it `env\Scripts\activate` then install the requirements using `pip install -r requirements.txt`
* Download kokoro-82M model files from their github repo. file names ` kokoro-v1.0.onnx` and ` voices-v1.0.bin` [download from here](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0) and put them in the `voice_files/` folder
* Add your own gemini API_KEY(S) ([get Gemini API key here](https://aistudio.google.com/app/api-keys) ) and a groq API key for fallback ([get groq API KEY here](https://console.groq.com/keys)), (You can also connect local LLM), make sure that you have added the gemini API keys in the `user_data/APIs.txt` file `one per line` and groq API key in the `user_data/groq_config.txt` file. In this format `{ "api_key": "YOUR KEY", "model_name": "model that you prefer" }` .For groq i prefer `llama-3.3-70b-versatile` it is better for tool calling.
* Once you have done everything right and your folder structure looks like the given structure. you can run the app using `env\Scripts\python.exe server.py` or directly inside the virtual env `python server.py` then open the link in the browser. You can also access the link `192.168.0.102:5000 ( something looks like this)` from your other devices connected to your wifi as well.
* Make sure to add your own api keys as well as keydict. run `key_test.py` to get the hidden keycodes and add them in the `user_data/keydict.txt`.
* if you face any kind of setup issue you can ask me in the [discussion](https://github.com/idcnys/jarvis/discussions) or you can submit [an issure here](https://github.com/idcnys/jarvis/issues) as well.

##  After you have done everything your folder should look like this

```
requirements.txt
server.py
constants/
    values.py
current/
    API.txt
    exhausted.txt
env/
helpers/
    api_selector.py
    compliments.py
    fetch.py
    gemini.py
    groqai.py
    memory_helpers.py
    physical_helpers.py
    randomQuote.py
    reset.py
    rotator.py
    skill_helpers.py
    utils.py
    viewer.py
    voice.py
    workspace_manager.py
memory/
    skills.json
static/
    css/
        cpuextra.css
        dialclock.css
        minichat.css
        mobile.css
        styles.css
        uptime_spinner.css
    js/
        client.js
        dialclock.js
        dials.js
        mobile.js
templates/
    index.html
    mobile.html
    settings.html
user_data/
    APIs.txt
    groq_config.txt
    history.json
    instructions.txt
    keydict.txt
variables/
    ai_name.txt
    voice_name.txt
    workspace.txt
voice_files/
    kokoro-v1.0.onnx
    voices-v1.0.bin
workspace/
```

This README provides an overview of the folder structure for the project. Each folder and file serves a specific purpose in the application. For further details, refer to the respective files and directories.

# 📋 Architecture

<img width="1333" height="711" alt="image" src="https://github.com/user-attachments/assets/dcc83476-48cb-4e23-8ede-61d9915a71d6" />

