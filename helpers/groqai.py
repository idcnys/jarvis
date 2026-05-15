import json
from groq import Groq
from pathlib import Path

from helpers.physical_helpers import run_terminal_command, open_app, close_app, press_key, enter_text, press_multiple_keys, music_control, play_pause_music, take_screenshot, open_calculator, toggle_mute, lock_screen, get_PC_KEYS_status, create_file, read_file, update_file, delete_file, create_directory, delete_directory, list_files
from helpers.voice import speak as nix_speak, strip_markdown
from helpers.skill_helpers import save_skill, run_skill
from helpers.memory_helpers import load_system_instruction
from constants.values import GROQ_CONFIG_FILE, WORKING_DIR

Jarvis_HISTORY = []

# Load Groq configuration from user_data
config_path = Path(WORKING_DIR) / GROQ_CONFIG_FILE
groq_config = {}

if config_path.exists():
    try:
        with open(config_path, 'r') as f:
            groq_config = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load Groq config from {config_path}: {e}")

API_KEY = groq_config.get("api_key")
MODEL_NAME = groq_config.get("model_name")
client = Groq(api_key=API_KEY)

tools = [
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

available_functions = {
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

def getGroqResponse(user_text):
    global Jarvis_HISTORY
    
    try:
        messages = [{"role": "system", "content": load_system_instruction()}]
        messages.extend(Jarvis_HISTORY)
        messages.append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Must append the assistant's request to call a tool first
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                })

            # Get the final verbal confirmation
            second_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            final_text = second_response.choices[0].message.content
        else:
            final_text = response_message.content

        nix_speak(strip_markdown(final_text))
        
        Jarvis_HISTORY.append({"role": "user", "content": user_text})
        Jarvis_HISTORY.append({"role": "assistant", "content": final_text})

        # Keep only last 2 messages for token optimization
        if len(Jarvis_HISTORY) > 2:
            Jarvis_HISTORY = Jarvis_HISTORY[-2:]

        return {"status": "success", "output": final_text}

    except Exception as e:
        nix_speak(strip_markdown("Sorry boss, my logic circuits are a bit fried."))
        return {"status": "error", "output": str(e)}