import os
import json
import urllib.request

directories = ['voice_files', 'user_data']

api_file = {
    'user_data/APIs.txt': ""
}

groq_file = {
    "api_key": "",
    "model_name": "llama-3.3-70b-versatile"
}

downloads = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
}

# ANSI Escape Codes for Terminal Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def download_progress(count, block_size, total_size):
    """Callback function to display download progress in yellow."""
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        percent = min(100, percent)  # Cap at 100%
        print(f"\r{YELLOW}Downloading... {percent}% complete{RESET}", end="")
    else:
        print(f"\r{YELLOW}Downloading...{RESET}", end="")

def setup_workspace():
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}/")
        else:
            print(f"Directory already exists: {directory}/")

    for file_path, content in api_file.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created file: {file_path}")
        else:
            print(f"File already exists: {file_path}")

    groq_json_path = 'user_data/groq_config.txt'
    if not os.path.exists(groq_json_path):
        with open(groq_json_path, 'w', encoding='utf-8') as f:
            json.dump(groq_file, f, indent=2)
        print(f"Created file: {groq_json_path}")
    else:
        print(f"File already exists: {groq_json_path}")

    print("-" * 40)

    for filename, url in downloads.items():
        destination_path = os.path.join("voice_files", filename)
        
        if not os.path.exists(destination_path):
            print(f"{YELLOW}Starting download: {filename}...{RESET}")
            try:
                urllib.request.urlretrieve(url, destination_path, download_progress)
                print(f"\n{GREEN}Successfully downloaded and saved to: {destination_path}{RESET}\n")
            except Exception as e:
                print(f"\nFailed to download {filename}. Error: {e}\n")
        else:
            print(f"File already exists (skipping download): {destination_path}")

if __name__ == "__main__":
    setup_workspace()
    print(f"{GREEN}Workspace setup complete!{RESET}")