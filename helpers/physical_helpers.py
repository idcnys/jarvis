import platform
import subprocess
import os
import shutil
import time
import pyautogui
import json
from pathlib import Path

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

from constants.values import WORKING_DIR
pyautogui.FAILSAFE = True

WORKSPACE_DIR = Path(WORKING_DIR) / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

KEY_DICT_FILE = Path(WORKING_DIR) / "user_data" / "keydict.txt"

PC_KEYS = {}

if KEY_DICT_FILE.exists():
    try:
        with open(KEY_DICT_FILE, 'r') as f:
            PC_KEYS = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load Lenovo key dictionary: {e}")

def run_terminal_command(command: str) -> str:
    """
    Executes a shell command on the local system and returns the output.
    
    Args:
        command: The full terminal command string to execute.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10,cwd=WORKING_DIR)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

def open_app(app_name: str) -> str:
    """
    Attempts to launch an application by its name.
    
    Args:
        app_name: The name of the application to open (e.g., 'chrome', 'notepad').
    """
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(f'start {app_name}', shell=True)
            
        elif system == "Darwin":  # macOS
            subprocess.Popen(['open', '-a', app_name])
            
        elif system == "Linux":
            binary = shutil.which(app_name)
            if binary:
                subprocess.Popen([binary])
            else:
                # Fallback for desktop-integrated apps
                subprocess.Popen(['xdg-open', app_name])
        return f"✓ Opened application: {app_name}"
    except Exception as e:
        return f"✗ Error opening {app_name}: {str(e)}"

def close_app(app_name: str) -> str:
    """
    Closes an application. Tries to close gracefully before forcing.
    
    Args:
        app_name: The name of the process to kill (e.g., 'chrome', 'spotify').
    """
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(f'taskkill /IM {app_name}.exe', shell=True, capture_output=True)
        elif system == "Darwin":
            subprocess.run(['killall', app_name], capture_output=True)
        elif system == "Linux":
            # -ix makes it case-insensitive and exact match for better reliability
            subprocess.run(['pkill', '-ix', app_name], capture_output=True)
        return f"Successfully attempted to close {app_name}"
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def press_key(key: str) -> str:
    """
    Presses a single keyboard key.

    Args:
        key: The name of the key (e.g., 'enter', 'esc', 'space', 'f1').
    """
    try:
        time.sleep(0.5)
        pyautogui.press(key.lower())
        return f"✓ Pressed key: {key}"
    except Exception as e:
        return f"✗ Error pressing key {key}: {str(e)}"

def enter_text(text: str) -> str:
    """
    Types a string of text character by character into the active window.
    
    Args:
        text: The actual text string to be typed out.
    """
    try:
        # Crucial delay: Gives the application window time to focus before typing starts
        time.sleep(1.0)
        pyautogui.write(text, interval=0.05)
        return f"✓ Entered text: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        return f"✗ Error entering text: {str(e)}"

def press_multiple_keys(keys: list[str]) -> str:
    """
    Presses a combination of keys simultaneously (Hotkeys).
    
    Args:
        keys: A list of key names to hold down (e.g., ['ctrl', 'c'] or ['win', 'r']).
    """
    try:
        time.sleep(0.5)
        pyautogui.hotkey(*[k.lower() for k in keys])
        return f"✓ Executed hotkey: {'+'.join(keys)}"
    except Exception as e:
        return f"✗ Error executing hotkey: {str(e)}"

def music_control(action: str) -> str:
    """
    Controls system music playback (play, pause, next, previous).
    Uses Lenovo special keys for play/pause if available.
    
    Args:
        action: The music control action (e.g., 'play', 'pause', 'next', 'previous').
    """
    action_lower = action.lower().strip()
    
    # For play/pause, use the Lenovo special key function
    if action_lower in ('play', 'pause', 'play/pause', 'playpause', 'toggle'):
        return play_pause_music()
    
    # For other actions, use PyAutoGUI media keys as fallback
    key_map = {
        "next": "nexttrack",
        "previous": "prevtrack"
    }
    
    target_key = key_map.get(action_lower)
    if not target_key:
        return f"✗ Unsupported music action: {action}. Use: play, pause, next, or previous"
    
    time.sleep(0.3)
    try:
        pyautogui.press(target_key)
        return f"✓ Executed music control: {action}"
    except Exception as e:
        return f"✗ Error executing music control {action}: {str(e)}"

# ==================== FILE CRUD OPERATIONS ====================

def create_file(file_path: str, content: str = "") -> str:
    """
    Creates a new file with optional initial content.
    Files are created in the Jarvis_workspace directory for safety.
    Works on Windows, Linux, and macOS.
    
    Args:
        file_path: Filename or relative path (will be created in Jarvis_workspace)
        content: Optional initial content for the file
    
    Returns:
        Success or error message
    """
    try:
        # Convert to Path object and resolve to absolute path
        file_path_obj = Path(file_path)
        
        # If it's an absolute path, use it as is (if valid)
        # Otherwise, treat it as relative to workspace
        if file_path_obj.is_absolute():
            full_path = file_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / file_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        # Create parent directories if they don't exist
        parent_dir = full_path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the file
        with open(full_path, 'w', encoding='utf-8') as f:
            if content:
                f.write(content)
        
        return f"✓ File created: {full_path}"
    except Exception as e:
        return f"✗ Error creating file: {str(e)}"

def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a file from Jarvis_workspace.
    
    Args:
        file_path: Filename or relative path (will be read from Jarvis_workspace)
    
    Returns:
        File content or error message
    """
    try:
        # Convert to Path object and resolve
        file_path_obj = Path(file_path)
        
        # If it's an absolute path, use it as is
        # Otherwise, treat it as relative to workspace
        if file_path_obj.is_absolute():
            full_path = file_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / file_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if not full_path.exists():
            return f"✗ File not found: {full_path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content if content else f"(empty file)"
    except Exception as e:
        return f"✗ Error reading file: {str(e)}"

def update_file(file_path: str, content: str, append: bool = False) -> str:
    """
    Updates a file by writing or appending content from Jarvis_workspace.
    
    Args:
        file_path: Filename or relative path (will be updated in Jarvis_workspace)
        content: Content to write or append
        append: If True, append content; if False, overwrite
    
    Returns:
        Success or error message
    """
    try:
        # Convert to Path object and resolve
        file_path_obj = Path(file_path)
        
        # If it's an absolute path, use it as is
        # Otherwise, treat it as relative to workspace
        if file_path_obj.is_absolute():
            full_path = file_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / file_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if not full_path.exists():
            return f"✗ File not found: {full_path}"
        
        mode = 'a' if append else 'w'
        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "appended to" if append else "updated"
        return f"✓ File {action}: {full_path}"
    except Exception as e:
        return f"✗ Error updating file: {str(e)}"

def delete_file(file_path: str) -> str:
    """
    Deletes a file permanently from Jarvis_workspace.
    
    Args:
        file_path: Filename or relative path (will be deleted from Jarvis_workspace)
    
    Returns:
        Success or error message
    """
    try:
        # Convert to Path object and resolve
        file_path_obj = Path(file_path)
        
        # If it's an absolute path, use it as is
        # Otherwise, treat it as relative to workspace
        if file_path_obj.is_absolute():
            full_path = file_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / file_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if not full_path.exists():
            return f"✗ File not found: {full_path}"
        
        full_path.unlink()
        return f"✓ File deleted: {full_path}"
    except Exception as e:
        return f"✗ Error deleting file: {str(e)}"

def create_directory(dir_path: str) -> str:
    """
    Creates a directory (and parent directories if needed) in Jarvis_workspace.
    
    Args:
        dir_path: Relative path to the directory to create
    
    Returns:
        Success or error message
    """
    try:
        # Convert to Path object and resolve
        dir_path_obj = Path(dir_path)
        
        # If it's an absolute path, use it as is
        # Otherwise, treat it as relative to workspace
        if dir_path_obj.is_absolute():
            full_path = dir_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / dir_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if full_path.exists():
            return f"✗ Directory already exists: {full_path}"
        
        full_path.mkdir(parents=True, exist_ok=True)
        return f"✓ Directory created: {full_path}"
    except Exception as e:
        return f"✗ Error creating directory: {str(e)}"

def delete_directory(dir_path: str, recursive: bool = False) -> str:
    """
    Deletes a directory from Jarvis_workspace. Use recursive=True to delete non-empty directories.
    
    Args:
        dir_path: Relative path to the directory to delete
        recursive: If True, delete directory and all contents
    
    Returns:
        Success or error message
    """
    try:
        # Convert to Path object and resolve
        dir_path_obj = Path(dir_path)
        
        # If it's an absolute path, use it as is
        # Otherwise, treat it as relative to workspace
        if dir_path_obj.is_absolute():
            full_path = dir_path_obj.resolve()
        else:
            full_path = (WORKSPACE_DIR / dir_path_obj).resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if not full_path.exists():
            return f"✗ Directory not found: {full_path}"
        
        if recursive:
            shutil.rmtree(full_path)
            return f"✓ Directory deleted (recursive): {full_path}"
        else:
            if list(full_path.iterdir()):
                return f"✗ Directory not empty. Use recursive=True to delete with contents."
            full_path.rmdir()
            return f"✓ Directory deleted: {full_path}"
    except Exception as e:
        return f"✗ Error deleting directory: {str(e)}"

def list_files(dir_path: str, recursive: bool = False) -> str:
    """
    Lists all files and directories in a given path from Jarvis_workspace.
    
    Args:
        dir_path: Relative path to the directory to list (defaults to workspace root)
        recursive: If True, list all files recursively
    
    Returns:
        Formatted list of files/directories or error message
    """
    try:
        # Convert to Path object and resolve
        if dir_path:
            dir_path_obj = Path(dir_path)
            if dir_path_obj.is_absolute():
                full_path = dir_path_obj.resolve()
            else:
                full_path = (WORKSPACE_DIR / dir_path_obj).resolve()
        else:
            full_path = WORKSPACE_DIR.resolve()
        
        # Security check: ensure path is within workspace
        try:
            full_path.relative_to(WORKSPACE_DIR.resolve())
        except ValueError:
            return f"✗ Error: Path must be within workspace directory ({WORKSPACE_DIR})"
        
        if not full_path.exists():
            return f"✗ Directory not found: {full_path}"
        
        items = []
        if recursive:
            for root, dirs, files in os.walk(str(full_path)):
                level = len(Path(root).relative_to(full_path).parts)
                indent = ' ' * 2 * level
                items.append(f"{indent} {os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    items.append(f"{subindent} {file}")
        else:
            for item in full_path.iterdir():
                if item.is_dir():
                    items.append(f" {item.name}/")
                else:
                    items.append(f" {item.name}")
        
        return '\n'.join(items) if items else "(empty directory)"
    except Exception as e:
        return f"✗ Error listing directory: {str(e)}"

# Special Lenovo PC Keys (play/pause, mute, lock screen, etc.)

def _press_keyboard_key(key_name: str) -> str:
    """
    Presses a key using the keyboard library (for special keys).
    
    Args:
        key_name: Key name to press (e.g., 'play-pause', 'mute', 'lock')
    
    Returns:
        Success or error message
    """
    if not KEYBOARD_AVAILABLE:
        return "✗ Error: keyboard library not installed. Run: pip install keyboard"
    
    if key_name not in PC_KEYS:
        return f"✗ Error: Key '{key_name}' not found in Lenovo key dictionary"
    
    try:
        key_info = PC_KEYS[key_name]
        keyboard_key = key_info.get('keyboard_name')
        
        if not keyboard_key:
            return f"✗ Error: No keyboard mapping found for '{key_name}'"
        
        keyboard.press(keyboard_key)
        time.sleep(0.1)
        keyboard.release(keyboard_key)
        
        return f"✓ Key pressed: {key_name} (keyboard_name: {keyboard_key})"
    except Exception as e:
        return f"✗ Error pressing key: {str(e)}"

def play_pause_music() -> str:
    """
    Plays or pauses current music/media.
    Uses Lenovo special key mapping.
    """
    result = _press_keyboard_key('play-pause')
    if "✓" in result:
        return "♫ Play/Pause toggled"
    return result

def take_screenshot() -> str:
    """
    Takes a screenshot using Windows Print Screen key.
    Uses Lenovo special key mapping.
    """
    result = _press_keyboard_key('prtsc')
    if "✓" in result:
        return "Screenshot taken (saved to clipboard)"
    return result

def open_calculator() -> str:
    """
    Opens the Windows Calculator application.
    Uses Lenovo special key mapping.
    """
    result = _press_keyboard_key('calculator')
    if "✓" in result:
        return "Calculator opening..."
    return result

def toggle_mute() -> str:
    """
    Toggles audio mute on/off.
    Uses Lenovo special key mapping.
    """
    result = _press_keyboard_key('mute')
    if "✓" in result:
        return "Mute toggled"
    return result

def lock_screen() -> str:
    """
    Locks the Windows screen (Win+L).
    Uses Lenovo special key mapping.
    """
    result = _press_keyboard_key('lock')
    if "✓" in result:
        return "Screen locked"
    return result

def get_PC_KEYS_status() -> str:
    """
    Returns the current status of PC key mappings.
    """
    if not PC_KEYS:
        return "✗ No PC keys mapped yet"
    
    status = f"✓ PC Keys Mapped ({len(PC_KEYS)}):\n"
    for name, info in PC_KEYS.items():
        status += f"  • {name} → {info.get('keyboard_name', 'unknown')}\n"
    
    return status