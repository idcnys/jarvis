import os
import json

# File paths
APIS_FILE = 'user_data/APIs.txt'
GROQ_CONFIG_FILE = 'user_data/groq_config.txt'  # Kept as .txt as requested

# ANSI Escape Codes for Terminal Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def append_to_apis(key):
    """Appends a generic API key to user_data/APIs.txt on a new line."""
    if not os.path.exists(APIS_FILE):
        print(f"{YELLOW}Warning: {APIS_FILE} not found. Creating it.{RESET}")
    
    try:
        with open(APIS_FILE, 'a', encoding='utf-8') as f:
            # Ensure it writes on a clean new line
            f.write(f"{key}\n")
        print(f"{GREEN}Successfully appended key to {APIS_FILE}{RESET}")
    except Exception as e:
        print(f"Error updating {APIS_FILE}: {e}")

def update_groq_key(new_groq_key):
    """Updates the api_key inside user_data/groq_config.txt using JSON formatting."""
    if not os.path.exists(GROQ_CONFIG_FILE):
        print(f"Error: {GROQ_CONFIG_FILE} does not exist. Please run setup first.")
        return

    try:
        # 1. Read existing structured data from the text file
        with open(GROQ_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. Update the specific api_key field
        data['api_key'] = new_groq_key
        
        # 3. Save the formatted text back to the file
        with open(GROQ_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print(f"{GREEN}Successfully updated Groq API key in {GROQ_CONFIG_FILE}{RESET}")
    except Exception as e:
        print(f"Error updating {GROQ_CONFIG_FILE}: {e}")

if __name__ == "__main__":
    print(f"{YELLOW}--- API Key Setup Utility ---{RESET}")
    
    # Get user inputs
    groq_input = input("Enter your Groq API Key (or press Enter to skip): ").strip()
    other_key_input = input("Enter any other API key to append to APIs.txt (or press Enter to skip): ").strip()
    
    print("-" * 40)
    
    # Process Groq Key
    if groq_input:
        update_groq_key(groq_input)
    else:
        print("No Groq key provided. Skipping update.")
        
    # Process General Key
    if other_key_input:
        append_to_apis(other_key_input)
    else:
        print("No additional keys provided to append.")

    print(f"\n{GREEN}Key configuration script finished!{RESET}")