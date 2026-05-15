import random
from constants.values import API_KEYS_FILE
def getRandomKey():
    with open(API_KEYS_FILE, "r") as f:
        keys = f.read().splitlines()
    return random.choice(keys)