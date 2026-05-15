import datetime
import math
import platform
import psutil
import socket
import requests

from constants.values import AI_MODEL_NAME, WORKING_DIR, WORKING_DIR
from helpers.viewer import view_skills
from helpers.rotator import GeminiRotator
from helpers.workspace_manager import get_workspace_path

rotator_instance = GeminiRotator()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException as e:
        return f"Error: {e}"


battery = psutil.sensors_battery()

def get_static_info():
    # Only run these once at startup
    info = {
        "Platform": platform.system(),
        "Platform-Release": platform.release(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "RAM Total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "Boot Time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return "\n".join([f"<b style='color:gray;'>{key}:</b> {value}" for key, value in info.items()])

def get_dynamic_info():
    info = {
        "Local IP": get_local_ip(),
        "Public IP": get_public_ip(),
        "Disk Usage": f"{psutil.disk_usage('/').percent}% ({psutil.disk_usage('/').free / (1024**3):.2f} GB Free)",
    }
    return "\n".join([f"<b style='color:gray;'>{key}:</b> {value}" for key, value in info.items()])
    
appinfo = {
    "Model": AI_MODEL_NAME,
    "Provider": "Google Gemini (w/ Groq Fallback)",
    "Workspace": get_workspace_path(),
    "Skills Learned": len(view_skills().split("\n")) - 1 if "Here are the skills I've learned:" in view_skills() else 0,
}

def get_api_info():
    """Returns API rotation state."""
    state = rotator_instance.get_state()
    return {
        "API Keys": f"{state['available_count']}/{state['total_keys']}",
        "Exhausted": state['exhausted_count'],
        "Current Key": f"#{state['current_index']}",
        "Status": state['status']
    }

def give_app_info():
    api_info = get_api_info()
    base_info = appinfo.copy()
    base_info.update(api_info)
    return "\n".join([f"<b style='color:gray;'>{key}:</b> {value}" for key, value in base_info.items()])
