# --- MEMORY HELPERS ---
import os
import json

from constants.values import SYSTEM_FILE, HISTORY_FILE


def load_system_instruction():
    """Loads the system prompt from an external file."""
    if os.path.exists(SYSTEM_FILE):
        with open(SYSTEM_FILE, 'r') as f:
            return f.read()
    return "You are a helpful AI assistant with terminal access."

def save_history(history_objects):
    serializable_history = []
    
    for content in history_objects:
        # Extract the text from each part of the message
        parts = []
        for part in content.parts:
            # We only save the text parts for local memory
            if hasattr(part, 'text') and part.text:
                parts.append({"text": part.text})
        
        # Only add to history if there's actual content
        if parts:
            serializable_history.append({
                "role": content.role,
                "parts": parts
            })

    with open(HISTORY_FILE, "w") as f:
        json.dump(serializable_history, f, indent=4)

def load_history():
    # 1. Check if file exists
    if not os.path.exists(HISTORY_FILE):
        return []
        
    try:
        with open(HISTORY_FILE, 'r') as f:
            # 2. Check if file is actually empty (0 bytes)
            if os.stat(HISTORY_FILE).st_size == 0:
                return []
            
            full_history = json.load(f)
            # Return only last 2 messages for token optimization
            return full_history[-2:] if len(full_history) > 2 else full_history
            
    except (json.JSONDecodeError, ValueError):
        # 3. If file is corrupted or invalid, return empty list
        print("Warning: history.json corrupted. Starting fresh.")
        return []
