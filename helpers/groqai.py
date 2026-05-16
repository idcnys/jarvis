import json
import logging
from pathlib import Path
from groq import Groq

from helpers.physical_helpers import (
    run_terminal_command, open_app, close_app, press_key, enter_text, 
    press_multiple_keys, music_control, play_pause_music, take_screenshot, 
    open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, 
    create_file, read_file, update_file, delete_file, create_directory, 
    delete_directory, list_files
)
from helpers.voice import speak as nix_speak, strip_markdown
from helpers.skill_helpers import save_skill, run_skill
from helpers.memory_helpers import load_system_instruction
from constants.values import GROQ_CONFIG_FILE, WORKING_DIR

logger = logging.getLogger(__name__)

# Declare tools configurations globally to eliminate recreation overhead
TOOLS_MANIFEST = [
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Executes a shell command on the local system and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The full terminal command string to execute."}
                },
                "required": ["command"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Opens an application by name. Examples: 'chrome', 'notepad', 'calculator', 'spotify'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to open (string, required)."}
                },
                "required": ["app_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Closes a running application by process name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Process name to close (string, required)."}
                },
                "required": ["app_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Presses a single keyboard key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key name: enter, esc, space, tab, f1, etc."}
                },
                "required": ["key"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enter_text",
            "description": "Types text into the active window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to type (string, required)."}
                },
                "required": ["text"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_multiple_keys",
            "description": "Presses multiple keys simultaneously (hotkeys).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "List of key names (e.g., ['ctrl', 'c'])."
                    }
                },
                "required": ["keys"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "music_control",
            "description": "Controls music playback: play, pause, next, or previous track.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string", 
                        "enum": ["play", "pause", "next", "previous"],
                        "description": "Music action: play, pause, next, or previous."
                    }
                },
                "required": ["action"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_pause_music",
            "description": "Toggles play/pause for current media.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot and saves to clipboard.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_calculator",
            "description": "Opens the Windows Calculator app.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_mute",
            "description": "Toggles system audio mute.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Locks the Windows desktop.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_PC_KEYS_status",
            "description": "Returns status of mapped Lenovo special keys.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file with optional initial content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Full path to the file."},
                    "content": {"type": "string", "description": "Optional initial content."}
                },
                "required": ["file_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads and returns file content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Full path to the file."}
                },
                "required": ["file_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_file",
            "description": "Writes or appends content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Full path to the file."},
                    "content": {"type": "string", "description": "Content to write or append."},
                    "append": {"type": "boolean", "description": "True to append, false to overwrite."}
                },
                "required": ["file_path", "content"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a file permanently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Full path to the file."}
                },
                "required": ["file_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Creates a directory and parent directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Full path to the directory."}
                },
                "required": ["dir_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_directory",
            "description": "Deletes a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Full path to the directory."},
                    "recursive": {"type": "boolean", "description": "True to delete all contents."}
                },
                "required": ["dir_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all files and directories in a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {"type": "string", "description": "Full path to the directory."},
                    "recursive": {"type": "boolean", "description": "True for recursive listing."}
                },
                "required": ["dir_path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_skill",
            "description": "Saves a sequence of actions as a named skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Unique skill name."},
                    "commands": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of action objects with 'tool' and 'arg' keys."
                    }
                },
                "required": ["skill_name", "commands"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_skill",
            "description": "Executes a previously saved skill by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Name of the skill to execute."}
                },
                "required": ["skill_name"],
                "additionalProperties": False
            }
        }
    }
]

FUNCTION_ROUTER = {
    "run_terminal_command": run_terminal_command,
    "open_app": open_app,
    "close_app": close_app,
    "press_key": press_key,
    "enter_text": enter_text,
    "press_multiple_keys": press_multiple_keys,
    "music_control": music_control,
    "play_pause_music": play_pause_music,
    "take_screenshot": take_screenshot,
    "open_calculator": open_calculator,
    "toggle_mute": toggle_mute,
    "lock_screen": lock_screen,
    "get_PC_KEYS_status": get_PC_KEYS_status,
    "create_file": create_file,
    "read_file": read_file,
    "update_file": update_file,
    "delete_file": delete_file,
    "create_directory": create_directory,
    "delete_directory": delete_directory,
    "list_files": list_files,
    "save_skill": save_skill,
    "run_skill": run_skill
}

class PersistentGroqFallback:
    def __init__(self):
        self.config_path = Path(WORKING_DIR) / GROQ_CONFIG_FILE
        self.client = None
        self.model_name = None
        self.system_instruction = None
        self.history = []
        
        self._load_environment_assets()

    def _load_environment_assets(self):
        """Loads underlying setup properties safely once at instantiation."""
        groq_config = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    groq_config = json.load(f)
            except Exception as e:
                logger.error(f"Could not load Groq configuration file: {e}")

        api_key = groq_config.get("api_key")
        self.model_name = groq_config.get("model_name")
        
        if api_key:
            self.client = Groq(api_key=api_key)
            
        # Cache instructions to prevent redundant drive access loops
        try:
            self.system_instruction = load_system_instruction()
        except Exception as io_err:
            logger.error(f"Fallback asset recovery error: {io_err}")
            self.system_instruction = "You are a helpful system engineering assistant."

    def get_response(self, user_text):
        if not self.client:
            return {"status": "error", "output": "Groq execution client context not initialized."}

        try:
            # Added explicit instructions to Groq on how it MUST structure tools
            groq_guardrail = (
                "\n\nCRITICAL CONTEXT: You can talk directly to the user. "
                "For normal conversation, greetings, questions, or updates, respond with regular text. "
                "If you need to use a tool, you MUST use the native tool-calling system. "
                "Do NOT write raw text tags like '<function/...>'."
            )
            
            messages = [{"role": "system", "content": self.system_instruction + groq_guardrail}]
            messages.extend(self.history[-2:])
            messages.append({"role": "user", "content": user_text})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=TOOLS_MANIFEST,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            final_text = None

            # --- CASE 1: Native API Tool Calls ---
            if tool_calls:
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = FUNCTION_ROUTER.get(function_name)
                    
                    if function_to_call:
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            print(f"Groq hallucinated tool arguments. Catching gracefully.")
                            final_text = tool_call.function.arguments or "Had trouble parsing that command."
                            tool_calls = None
                            break

                        function_response = function_to_call(**function_args)

                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response),
                        })

                if tool_calls:
                    second_response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages
                    )
                    final_text = second_response.choices[0].message.content

            # --- CASE 2: Groq Written Text Tag Fallback (<function/tool_name>{...}) ---
            elif response_message.content and "<function/" in response_message.content:
                print("Detected string-embedded function token. Running regex extraction extraction...")
                import re
                
                # Match things like <function/create_file>{"file_path": ...}
                pattern = r"<function/(\w+)>(.*?)(?:</function>|$)"
                match = re.search(pattern, response_message.content, re.DOTALL)
                
                if match:
                    function_name = match.group(1)
                    raw_args = match.group(2).strip()
                    function_to_call = FUNCTION_ROUTER.get(function_name)
                    
                    if function_to_call:
                        try:
                            function_args = json.loads(raw_args)
                            function_response = function_to_call(**function_args)
                            
                            # Ask Groq to give a verbal update back using the text result
                            messages.append(response_message)
                            messages.append({
                                "role": "user",
                                "content": f"SYSTEM SYSTEM: The tool '{function_name}' executed. Result: {function_response}. Give a natural response to the user."
                            })
                            
                            second_response = self.client.chat.completions.create(
                                model=self.model_name,
                                messages=messages
                            )
                            final_text = second_response.choices[0].message.content
                        except Exception as parse_err:
                            print(f"Failed to execute manual string fallback tool: {parse_err}")
                            final_text = "I saw the file request but couldn't parse the configurations cleanly."
                
                if not final_text:
                    final_text = response_message.content

            # --- CASE 3: Normal Conversation ---
            else:
                final_text = response_message.content

            # Handle speech and memory storage
            nix_speak(strip_markdown(final_text))
            
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": final_text})

            if len(self.history) > 2:
                self.history = self.history[-2:]

            return {"status": "success", "output": final_text}

        except Exception as e:
            error_msg = str(e)
            if "tool_use_failed" in error_msg or "400" in error_msg:
                print("Groq failed tool construction completely. Executing stateless text fallback...")
                try:
                    fallback_response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "Respond to the user directly using pure text only. Do not invoke tools."},
                            {"role": "user", "content": user_text}
                        ]
                    )
                    final_text = fallback_response.choices[0].message.content
                    nix_speak(strip_markdown(final_text))
                    return {"status": "success", "output": final_text}
                except Exception as inner_e:
                    error_msg = str(inner_e)

            logger.error(f"Error during Groq run: {error_msg}")
            nix_speak(strip_markdown("Sorry boss, my logic circuits are a bit fried."))
            return {"status": "error", "output": error_msg}
# Instantiate clean shared context token once globally upon runtime load
groq_backup_engine = PersistentGroqFallback()

def getGroqResponse(user_text):
    """Wrapper function to preserve backwards compatibility across imports."""
    return groq_backup_engine.get_response(user_text)