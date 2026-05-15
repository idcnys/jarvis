"""
Workspace Manager for Jarvis Agent
Handles file creation and reading in the workspace directory
"""

import os
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent  # helpers folder
PROJECT_ROOT = SCRIPT_DIR.parent  # project root
WORKSPACE_DIR = PROJECT_ROOT / "workspace"

# Ensure workspace directory exists
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def create_file(filename: str, content: str, subdirectory: str = None) -> dict:
    """
    Creates a file in the workspace directory.
    
    Args:
        filename: Name of the file to create
        content: Content to write to the file
        subdirectory: Optional subdirectory within workspace (e.g., "documents", "code")
    
    Returns:
        dict with success status and file path
    """
    try:
        if subdirectory:
            file_dir = WORKSPACE_DIR / subdirectory
            file_dir.mkdir(parents=True, exist_ok=True)
        else:
            file_dir = WORKSPACE_DIR
        
        # Force absolute path
        file_path = (file_dir / filename).resolve()
        
        # Verify it's within WORKSPACE_DIR
        if not str(file_path).startswith(str(WORKSPACE_DIR.resolve())):
            return {
                "success": False,
                "error": f"Path {file_path} is outside workspace directory"
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"File created successfully",
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(WORKSPACE_DIR.parent))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def read_file(filename: str, subdirectory: str = None) -> dict:
    """
    Reads a file from the workspace directory.
    
    Args:
        filename: Name of the file to read
        subdirectory: Optional subdirectory within workspace
    
    Returns:
        dict with success status and file content
    """
    try:
        if subdirectory:
            file_path = (WORKSPACE_DIR / subdirectory / filename).resolve()
        else:
            file_path = (WORKSPACE_DIR / filename).resolve()
        
        # Verify it's within WORKSPACE_DIR
        if not str(file_path).startswith(str(WORKSPACE_DIR.resolve())):
            return {
                "success": False,
                "error": f"Path {file_path} is outside workspace directory"
            }
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {filename}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(file_path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def list_files(subdirectory: str = None) -> dict:
    """
    Lists all files in the workspace or subdirectory.
    
    Args:
        subdirectory: Optional subdirectory to list
    
    Returns:
        dict with list of files
    """
    try:
        if subdirectory:
            target_dir = WORKSPACE_DIR / subdirectory
        else:
            target_dir = WORKSPACE_DIR
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Directory not found"
            }
        
        files = [f.name for f in target_dir.iterdir() if f.is_file()]
        dirs = [d.name for d in target_dir.iterdir() if d.is_dir()]
        
        return {
            "success": True,
            "files": files,
            "directories": dirs,
            "path": str(target_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def save_json(filename: str, data: dict, subdirectory: str = None) -> dict:
    """
    Saves a dictionary as JSON file.
    
    Args:
        filename: Name of the JSON file
        data: Dictionary to save
        subdirectory: Optional subdirectory within workspace
    
    Returns:
        dict with success status
    """
    try:
        content = json.dumps(data, indent=2)
        return create_file(filename, content, subdirectory)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def load_json(filename: str, subdirectory: str = None) -> dict:
    """
    Loads a JSON file from workspace.
    
    Args:
        filename: Name of the JSON file
        subdirectory: Optional subdirectory within workspace
    
    Returns:
        dict with success status and parsed JSON data
    """
    try:
        result = read_file(filename, subdirectory)
        if result["success"]:
            result["data"] = json.loads(result["content"])
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_workspace_path() -> str:
    """Returns the full path to the workspace directory"""
    return str(WORKSPACE_DIR)
