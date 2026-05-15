from constants.values import SYSTEM_FILE
def sysInstructions():
    with open(SYSTEM_FILE, "r") as f:
        return f.read()

def get_value(fname):
    with open(fname, "r") as f:
        return f.read().strip()
def set_value(fname, value):
    with open(fname, "w") as f:
        f.write(value)
def append_value(fname, value):
    with open(fname, "a") as f:
        f.write(value + "\n")