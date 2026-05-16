import os
from pathlib import Path


AI_MODEL_NAME = "gemini-2.5-flash"
AI_NAME = "Jarvis"
#TTS VOICE SETTINGS
VOICE_ONNX = "voice_files/kokoro-v1.0.onnx"
VOICES_BIN = "voice_files/voices-v1.0.bin"
CURRENT_VOICE = "af_bella"
VOICE_SPEED = 1.1
VOICE_LANG = "en-us"
#MEMORY FILES
SYSTEM_FILE = "user_data/instructions.txt"
HISTORY_FILE = "user_data/history.json"
SKILLS_FILE = "memory/skills.json"
#API_KEYS
API_KEYS_FILE = "user_data/APIs.txt"
GROQ_CONFIG_FILE = "user_data/groq_config.txt"


# Define the separate working directory (project root)
WORKING_DIR = str(Path(__file__).parent.parent.resolve())

KEY_DICT_FILE = Path(WORKING_DIR) / "user_data" / "keydict.txt"

# Ensure the directory exists immediately
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)