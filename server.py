from flask import Flask, render_template, request, jsonify, redirect
import time
import psutil
import threading
import json
from pathlib import Path

from helpers.compliments import get_compliment
from helpers.gemini import getGeminiResponse, rotator
from helpers.reset import history_reset
from helpers.viewer import view_skills
from helpers.voice import speak as nix_speak, get_speaking_status, wait_for_speech, shutdown_voice
from helpers.workspace_manager import create_file, read_file, list_files, save_json, load_json, get_workspace_path
from helpers.utils import get_static_info, get_local_ip, get_public_ip,give_app_info
from helpers.api_selector import getRandomKey
from helpers.fetch import sysInstructions, append_value
from constants.values import AI_MODEL_NAME, CURRENT_VOICE, VOICE_LANG, VOICE_SPEED, WORKING_DIR, GROQ_CONFIG_FILE
from helpers.fetch import get_value
from helpers.randomQuote import myQuote
from helpers.groqai import getGroqResponse
app = Flask(__name__)
start_time = time.time()


@app.teardown_appcontext
def cleanup(error=None):
    wait_for_speech()


@app.route('/',methods=['GET'])
def home():
    user_agent = request.headers.get('User-Agent')

    if 'Mobile' in user_agent:
        return render_template('mobile.html')
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    user_text = data.get('text_input')
    result = getGeminiResponse(user_text)
    # result = getGroqResponse(user_text)
    return jsonify(result)

# to get system info
@app.route('/sys_static',methods=['GET'])
def system_info():
    return get_static_info()


@app.route('/appinfo',methods=['GET'])
def app_info():
    return give_app_info()


@app.route('/quote',methods=['GET'])
def quote():
    myq = myQuote()
    nix_speak(myq)
    return "Success"

@app.route('/compliment',methods=['GET'])
def compliment():
    myq = get_compliment()
    nix_speak(myq)
    return "Success"

@app.route('/ruhere',methods=['GET'])
def ruhere():
    nix_speak(f"Yes captain, I'm here. What can I do for you?") 
    return "Success"

@app.route('/greet',methods=['GET'])
def greet():
    nix_speak(f"Refreshing my system...All parameters are optimal. I'm ready for your command boss.") 
    return "Success"


@app.route("/utility")
def utility():
    utility = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "swap": psutil.swap_memory().percent,
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 0,
    }
    return jsonify(utility)

@app.route("/uptime")
def uptime():
    uptime_seconds = int(time.time() - start_time)
    return jsonify({"uptime_seconds": uptime_seconds})

@app.route("/speaking_status")
def speaking_status():
    return jsonify(get_speaking_status())

@app.route("/dashboard")
def dashboard():
    """
    Combined endpoint for all dashboard data.
    Reduces API calls by bundling frequently-requested data.
    """
    uptime_seconds = int(time.time() - start_time)
    speaking_info = get_speaking_status()
    
    return jsonify({
        "uptime": uptime_seconds,
        "speaking": speaking_info.get("is_speaking", False),
        "queue_size": speaking_info.get("queue_size", 0),
        "timestamp": time.time()
    })

@app.route("/api_state")
def api_state():
    """Returns current Gemini API rotation state."""
    state = rotator.get_state()
    return jsonify(state)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Get API keys count
    try:
        with open("user_data/APIs.txt", "r") as f:
            api_keys_count = len(f.read().splitlines())
    except:
        api_keys_count = 0
    
    # Read voice settings from files with fallbacks to constants
    try:
        with open("variables/voice_name.txt", "r") as f:
            voice_name = f.read().strip()
    except:
        voice_name = CURRENT_VOICE
    
    try:
        with open("variables/voice_speed.txt", "r") as f:
            voice_speed = f.read().strip()
    except:
        voice_speed = str(VOICE_SPEED)
    
    try:
        with open("variables/voice_lang.txt", "r") as f:
            voice_lang = f.read().strip()
    except:
        voice_lang = VOICE_LANG
    
    # Read skills from memory/skills.json
    skills_data = {}
    try:
        with open("memory/skills.json", "r") as f:
            skills_data = json.load(f)
    except:
        skills_data = {}
    
    # Get API rotation state
    api_state = rotator.get_state()
    
    return render_template('settings.html', 
        ai_model=AI_MODEL_NAME, 
        system_info=sysInstructions(),
        voice_name=voice_name, 
        voice_speed=voice_speed, 
        voice_lang=voice_lang, 
        ai_name="Jarvis",
        api_keys_count=api_keys_count,
        api_in_use=AI_MODEL_NAME,
        api_state=api_state,
        skills=skills_data,
        workspace_dir=get_workspace_path())



@app.route("/add_api_key", methods=["POST"])
def add_api_key():
    append_value("user_data/APIs.txt", request.form.get("new_api_key"))
    return "API key added successfully!"

@app.route("/update_groq_api", methods=["POST"])
def update_groq_api():
    """Update Groq API key"""
    import json
    new_api_key = request.form.get("new_groq_api_key")
    try:
        groq_config_file = Path(WORKING_DIR) / GROQ_CONFIG_FILE
        groq_config = {"api_key": new_api_key, "model_name": "llama-3.3-70b-versatile"}
        
        if groq_config_file.exists():
            try:
                with open(groq_config_file, 'r') as f:
                    groq_config = json.load(f)
                groq_config["api_key"] = new_api_key
            except:
                pass
        
        with open(groq_config_file, 'w') as f:
            json.dump(groq_config, f, indent=2)
        return redirect("/settings?msg=Groq+API+key+updated")
    except Exception as e:
        return f"Error updating Groq API key: {str(e)}", 500

@app.route("/update_groq_model", methods=["POST"])
def update_groq_model():
    """Update Groq model name"""
    import json
    new_model_name = request.form.get("new_groq_model")
    try:
        groq_config_file = Path(WORKING_DIR) / GROQ_CONFIG_FILE
        groq_config = {}
        if groq_config_file.exists():
            try:
                with open(groq_config_file, 'r') as f:
                    groq_config = json.load(f)
                groq_config["model_name"] = new_model_name
            except:
                pass
        
        with open(groq_config_file, 'w') as f:
            json.dump(groq_config, f, indent=2)
        return redirect("/settings?msg=Groq+model+updated")
    except Exception as e:
        return f"Error updating Groq model: {str(e)}", 500

@app.route("/update_voice_name", methods=["POST"])
def update_voice_name():
    new_voice_name = request.form.get("new_voice_name")
    try:
        with open("variables/voice_name.txt", "w") as f:
            f.write(new_voice_name)
        return redirect("/settings?msg=Voice+name+updated")
    except Exception as e:
        return f"Error updating voice name: {str(e)}", 500

@app.route("/update_voice_speed", methods=["POST"])
def update_voice_speed():
    new_voice_speed = request.form.get("new_voice_speed")
    try:
        with open("variables/voice_speed.txt", "w") as f:
            f.write(new_voice_speed)
        return redirect("/settings?msg=Voice+speed+updated")
    except Exception as e:
        return f"Error updating voice speed: {str(e)}", 500



@app.route("/workspace/create", methods=["POST"])
def workspace_create():
    """Create a file in the workspace"""
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("content", "")
    subdirectory = data.get("subdirectory")
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = create_file(filename, content, subdirectory)
    return jsonify(result)


@app.route("/workspace/read", methods=["POST"])
def workspace_read():
    """Read a file from the workspace"""
    data = request.get_json()
    filename = data.get("filename")
    subdirectory = data.get("subdirectory")
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = read_file(filename, subdirectory)
    return jsonify(result)


@app.route("/workspace/list", methods=["GET"])
def workspace_list():
    """List files in the workspace"""
    subdirectory = request.args.get("subdirectory")
    result = list_files(subdirectory)
    return jsonify(result)


@app.route("/workspace/save_json", methods=["POST"])
def workspace_save_json():
    """Save JSON data to a file in the workspace"""
    data = request.get_json()
    filename = data.get("filename")
    json_data = data.get("data", {})
    subdirectory = data.get("subdirectory")
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = save_json(filename, json_data, subdirectory)
    return jsonify(result)


@app.route("/workspace/load_json", methods=["POST"])
def workspace_load_json():
    """Load JSON data from a file in the workspace"""
    data = request.get_json()
    filename = data.get("filename")
    subdirectory = data.get("subdirectory")
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = load_json(filename, subdirectory)
    return jsonify(result)


@app.route("/workspace/path", methods=["GET"])
def workspace_path():
    """Get the workspace directory path"""
    return jsonify({"path": get_workspace_path()})

@app.route("/update_voice_lang", methods=["POST"])
def update_voice_lang():
    new_voice_lang = request.form.get("new_voice_lang")
    try:
        with open("variables/voice_lang.txt", "w") as f:
            f.write(new_voice_lang)
        return redirect("/settings?msg=Voice+language+updated")
    except Exception as e:
        return f"Error updating voice language: {str(e)}", 500

@app.route("/update_workspace_dir", methods=["POST"])
def update_workspace_dir():
    new_workspace = request.form.get("new_workspace_dir")
    try:
        import os
        if os.path.isdir(new_workspace):
            with open("variables/workspace.txt", "w") as f:
                f.write(new_workspace)
            return redirect("/settings?msg=Workspace+directory+updated+%28restart+app+to+apply%29")
        else:
            return redirect("/settings?msg=Directory+does+not+exist")
    except Exception as e:
        return redirect("/settings?msg=Error+updating+workspace")

@app.route("/skills")
def skills():
    return view_skills()

if __name__ == '__main__':
    history_reset()
    app.run(host="0.0.0.0", debug=True)
