import logging
import time
from google import genai
from google.genai import types

from constants.values import AI_MODEL_NAME
from helpers.groqai import getGroqResponse
from helpers.physical_helpers import (
    run_terminal_command, open_app, close_app, press_key, enter_text, 
    press_multiple_keys, music_control, play_pause_music, take_screenshot, 
    open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, 
    create_file, read_file, update_file, delete_file, create_directory, 
    delete_directory, list_files
)
from helpers.memory_helpers import load_system_instruction, save_history, load_history
from helpers.voice import speak as nix_speak, strip_markdown
from helpers.skill_helpers import save_skill, run_skill
from helpers.rotator import GeminiRotator

logger = logging.getLogger(__name__)

# System manifests declared globally once
TOOLS_LIST = [
    run_terminal_command, open_app, close_app, press_key, enter_text, 
    press_multiple_keys, music_control, play_pause_music, take_screenshot, 
    open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, 
    create_file, read_file, update_file, delete_file, create_directory, 
    delete_directory, list_files, save_skill, run_skill
]

class PersistentGeminiChat:
    def __init__(self):
        self.rotator = GeminiRotator()
        self.model_name = AI_MODEL_NAME
        self.client = None
        self.chat = None
        self.current_key = None
        self.allExhausted = False
        
        self._init_new_chat_session()

    def _init_new_chat_session(self):
        """Initializes or handles real-time rotation transitions cleanly."""
        self.current_key = self.rotator.get_available_key()
        
        if self.current_key in ["wait", "no_keys_found"]:
            self.client = None
            self.chat = None
            return

        try:
            system_instruction = load_system_instruction()
            raw_history = load_history()

            config = types.GenerateContentConfig(
                tools=TOOLS_LIST,
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(include_thoughts=False)
            )

            self.client = genai.Client(api_key=self.current_key)
            self.chat = self.client.chats.create(
                model=self.model_name,
                config=config,
                history=raw_history
            )
            print(f"Initialized active persistent chat using key: [***{self.current_key[-4:] if len(self.current_key) > 4 else ''}]")
            
        except Exception as e:
            logger.error(f"Error configuring persistent chat session: {e}")
            self.client = None
            self.chat = None

    def send_message(self, user_text):
        """Processes messaging traffic via running dynamic failovers only on error."""
        max_retries = len(self.rotator.keys) if self.rotator.keys else 5
        
        for _ in range(max_retries):
            if not self.chat or self.current_key in ["wait", "no_keys_found"]:
                if self.current_key == "wait":
                    if self.allExhausted:
                        nix_speak("All Gemini API keys are currently exhausted, boss. Please wait a moment or switch to Groq.")
                    else:
                        self.allExhausted = True
                    
                    return getGroqResponse(user_text)
                elif self.current_key == "no_keys_found":
                    nix_speak("I couldn't find any Gemini API keys, boss.")
                    return getGroqResponse(user_text)
                
                self._init_new_chat_session()
                continue

            try:
                response = self.chat.send_message(user_text)
                
                nix_speak(strip_markdown(response.text))
                save_history(self.chat.get_history())
                
                return {"status": "success", "output": response.text}

            except Exception as e:
                error_msg = str(e)
                
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f"Key [***{self.current_key[-4:] if len(self.current_key) > 4 else ''}] exhausted! Rotating slot...")
                    self.rotator.mark_exhausted(self.current_key)
                    self._init_new_chat_session()
                    continue
                    
                elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                    print("Service congestion (503). Attempting silent session switch...")
                    self._init_new_chat_session()
                    continue

                logger.exception("Fatal unhandled handler error caught")
                nix_speak("I encountered a technical glitch, boss.")
                return {"status": "error", "output": error_msg}

        nix_speak("All options exhausted, passing to backup pipelines.")
        return getGroqResponse(user_text)

gemini_session = PersistentGeminiChat()