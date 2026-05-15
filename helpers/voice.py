from kokoro_onnx import Kokoro
import sounddevice as sd
import threading
import queue
import time
import re

from constants.values import VOICE_ONNX, VOICES_BIN, CURRENT_VOICE, VOICE_SPEED, VOICE_LANG

# Initialize with the files you just downloaded
kokoro = Kokoro(VOICE_ONNX, VOICES_BIN)

# Queue system for managing speech
speech_queue = queue.Queue()
is_speaking = False
speech_lock = threading.Lock()
shutdown_event = threading.Event()  # Signal to gracefully stop the thread

def strip_markdown(text: str) -> str:
    """
    Removes markdown formatting from text for cleaner speech.
    
    Args:
        text: Text with markdown formatting
    
    Returns:
        Plain text without markdown
    """
    if not text:
        return text
    
    # Remove headers (# ## ### etc)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'\1', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove code blocks (```...```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove inline code (`code`)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove images ![alt](url)
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
    
    # Remove blockquotes (> text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^(-{3}|\*{3}|_{3})', '', text, flags=re.MULTILINE)
    
    # Remove extra whitespace
    text = re.sub(r'\n\n+', '\n', text)
    text = text.strip()
    
    return text

def _play_from_queue():
    """
    Internal function that processes the speech queue.
    Plays queued items with 1 second delay between each.
    """
    global is_speaking
    
    while not shutdown_event.is_set():
        try:
            # Get next item from queue with timeout to check shutdown signal
            text = speech_queue.get(timeout=1)
            
            with speech_lock:
                is_speaking = True
            
            try:
                # Generate and play audio
                samples, sample_rate = kokoro.create(
                    text, 
                    voice=CURRENT_VOICE, 
                    speed=VOICE_SPEED, 
                    lang=VOICE_LANG
                )
                sd.play(samples, sample_rate)
                sd.wait()  # Wait for entire audio to finish
                
                # 1 second delay before next speech
                # time.sleep(1)
                
            finally:
                with speech_lock:
                    is_speaking = False
            
            # Mark task as done
            speech_queue.task_done()
            
        except queue.Empty:
            # No items in queue, continue checking shutdown signal
            continue
        except Exception as e:
            print(f"Error in speech queue: {str(e)}")
            with speech_lock:
                is_speaking = False

# Start the speech queue processor in a background daemon thread
# Daemon=True works better with Flask; we'll use shutdown mechanisms to ensure audio finishes
speech_thread = threading.Thread(target=_play_from_queue, daemon=True)
speech_thread.start()

def speak(text):
    """
    Queues text to be spoken.
    If already speaking, adds to queue and plays after current speech finishes.
    Otherwise, plays immediately.
    
    Args:
        text: The text to speak
    """
    global is_speaking
    
    # Add to queue
    speech_queue.put(text)
    
    # If not speaking, item will be processed immediately
    # If speaking, item will be processed after current speech and 1s delay

def get_speaking_status():
    """
    Returns the current speaking status.
    
    Returns:
        dict with speaking status and queue size
    """
    with speech_lock:
        return {
            "is_speaking": is_speaking,
            "queue_size": speech_queue.qsize()
        }

def wait_for_speech():
    """
    Waits for all queued speech to finish playing.
    Useful before exiting to ensure no audio is cut off.
    """
    speech_queue.join()  # Blocks until all tasks are done

def shutdown_voice():
    """
    Gracefully shuts down the speech thread.
    Call this before exiting your program to ensure all speech finishes.
    """
    global speech_thread
    try:
        speech_queue.join()  # Wait for queue to be empty
    except:
        pass
    shutdown_event.set()
