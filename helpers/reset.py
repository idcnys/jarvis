import json
import os

from constants.values import HISTORY_FILE

def history_reset():
    """Clears the user's interaction history."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
        return "History has been reset."
    else:
        return "No history found to reset."