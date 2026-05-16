import os
import time
from constants.values import API_KEYS_FILE

class GeminiRotator:
    def __init__(self, file_path=API_KEYS_FILE):
        self.file_path = file_path
        self.keys = self._load_keys()
        self.key_to_index = {entry["key"]: i for i, entry in enumerate(self.keys)}
        self.current_index = 0
        self.cooldown_period = 65

    def _load_keys(self):
        """Reads keys from a text file, one per line."""
        if not os.path.exists(self.file_path):
            print(f"Error: {self.file_path} not found.")
            return []
        
        with open(self.file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            
        return [{"key": k, "blocked_until": 0} for k in lines]

    def get_available_key(self):
        if not self.keys:
            return "no_keys_found"

        num_keys = len(self.keys)
        
        for _ in range(num_keys):
            current_entry = self.keys[self.current_index]
            
            if time.time() >= current_entry["blocked_until"]:
                key = current_entry["key"]
                return key

            self.current_index = (self.current_index + 1) % num_keys

        return "wait"

    def mark_exhausted(self, key):
        """Sets a cooldown for the specific key that hit the rate limit."""
        if key in self.key_to_index:
            idx = self.key_to_index[key]
            self.keys[idx]["blocked_until"] = time.time() + self.cooldown_period
            
            if self.current_index == idx:
                self.current_index = (self.current_index + 1) % len(self.keys)

    def get_state(self):
        """Returns current API rotation state."""
        now = time.time()
        total_keys = len(self.keys)
        exhausted_count = sum(1 for entry in self.keys if now < entry["blocked_until"])
        
        return {
            "total_keys": total_keys,
            "exhausted_count": exhausted_count,
            "available_count": total_keys - exhausted_count,
            "current_index": self.current_index + 1,
            "status": "Active" if exhausted_count < total_keys else "All Exhausted"
        }