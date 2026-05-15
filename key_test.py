import keyboard
import time

def on_key_event(event):
    """
    Callback function that triggers every time a key is pressed or released.
    It reveals the 'hidden' data inside the KeyboardEvent object.
    """
    if event.event_type == keyboard.KEY_DOWN:
        print("\n--- Key Press Detected ---")
        print(f"Key Name:      {event.name}")
        print(f"Scan Code:     {event.scan_code}")
        print(f"Event Type:    {event.event_type}")
        print(f"Time Stamp:    {event.time}")
        print(f"Is Modifier?:  {event.is_keypad}")
        print("-" * 26)

def main():
    print("==================================================")
    print("  Key Inspector Active (Press 'esc' to exit)  ")
    print("==================================================")
    print("Start typing anywhere on your system to see key data...")

    keyboard.hook(on_key_event)
    keyboard.wait('esc')
    
    print("\nUnhooking keyboard listeners. Exiting safely.")

if __name__ == "__main__":
    main()