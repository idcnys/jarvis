from time import time
from google import genai
from google.genai import types

from constants.values import AI_MODEL_NAME
from helpers.fetch import get_value
from helpers.groqai import getGroqResponse
from helpers.physical_helpers import run_terminal_command, open_app, close_app, press_key, enter_text, press_multiple_keys, music_control, play_pause_music, take_screenshot, open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, create_file, read_file, update_file, delete_file, create_directory, delete_directory, list_files
from helpers.memory_helpers import load_system_instruction, save_history, load_history
from helpers.voice import speak as nix_speak, get_speaking_status, strip_markdown
from helpers.skill_helpers import save_skill, run_skill
from helpers.rotator import GeminiRotator


rotator = GeminiRotator()

MODEL_NAME = AI_MODEL_NAME

def getGeminiResponse(user_text):
    while True:
        current_key = rotator.get_available_key()
        if current_key == "wait":
            nix_speak("Sorry boss, all our gemini APIs are currently exhausted. Please give me a minute to breathe. I am trying switching to groq in the meantime.")
            return getGroqResponse(user_text)
        elif current_key == "no_keys_found":
            nix_speak("I couldn't find any Gemini API keys, boss. Please check the APIs.txt file.")
            return getGroqResponse(user_text)

        try:
            client = genai.Client(api_key=current_key)
            
            config = types.GenerateContentConfig(
                tools=[run_terminal_command, open_app, close_app, press_key, enter_text, press_multiple_keys, music_control, play_pause_music, take_screenshot, open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, create_file, read_file, update_file, delete_file, create_directory, delete_directory, list_files, save_skill, run_skill],
                system_instruction=load_system_instruction(),
                thinking_config=types.ThinkingConfig(include_thoughts=False)
            )

            raw_history = load_history()
            
            chat = client.chats.create(
                model=MODEL_NAME,
                config=config,
                history=raw_history
            )
            
            response = chat.send_message(user_text)

            nix_speak(strip_markdown(response.text))
            save_history(chat.get_history())

            return {"status": "success", "output": response.text}

        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"Key exhausted, rotating to next...")
                rotator.mark_exhausted(current_key)
                continue 
            elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                print(f"I am tired, wait a moment boss...")
                continue

            nix_speak("I encountered a technical glitch, boss.")
            return {"status": "error", "output": error_msg}