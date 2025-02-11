import time
import threading
import subprocess
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPostToPid,
    CGEventSetFlags,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand
)


def get_pid(app_name):
    """
    Returns the Unix process ID of the running application with the given name.
    (The app name must match exactly, e.g. "TextEdit".)
    """
    script = f'tell application "System Events" to get unix id of process "{app_name}"'
    result = subprocess.run(["osascript", "-e", script],
                            capture_output=True, text=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        print("Could not find process:", app_name)
        return None


def send_key(pid, key_code, key_down, flags=0):
    """
    Creates a keyboard event for the given key_code and posts it to the target process.
    key_down is True for a key press and False for release.
    If flags is nonzero, they are set on the event (for example, to simulate modifier keys).
    """
    event = CGEventCreateKeyboardEvent(None, key_code, key_down)
    if flags:
        CGEventSetFlags(event, flags)
    CGEventPostToPid(pid, event)


def send_cmd_enter(pid):
    """
    Sends the CMD+ENTER key combination to the process with the given pid:
      1. Press Command down.
      2. Press Enter down with Command as modifier.
      3. Release Enter.
      4. Release Command.
    """
    CMD_KEY_CODE = 55  # Virtual key code for left Command
    ENTER_KEY_CODE = 36  # Virtual key code for Return/Enter
    modifier_flag = kCGEventFlagMaskCommand

    send_key(pid, CMD_KEY_CODE, True)
    time.sleep(0.01)
    send_key(pid, ENTER_KEY_CODE, True, flags=modifier_flag)
    time.sleep(0.01)
    send_key(pid, ENTER_KEY_CODE, False, flags=modifier_flag)
    time.sleep(0.01)
    send_key(pid, CMD_KEY_CODE, False)


# Mapping of characters to macOS virtual key codes (US layout)
VK_MAP = {
    'a': 0, 's': 1, 'd': 2, 'f': 3, 'h': 4, 'g': 5, 'z': 6, 'x': 7, 'c': 8, 'v': 9,
    'b': 11, 'q': 12, 'w': 13, 'e': 14, 'r': 15, 'y': 16, 't': 17, '1': 18, '2': 19,
    '3': 20, '4': 21, '6': 22, '5': 23, '=': 24, '9': 25, '7': 26, '-': 27, '8': 28,
    '0': 29, ']': 30, 'o': 31, 'u': 32, '[': 33, 'i': 34, 'p': 35, 'l': 37, 'j': 38,
    "'": 39, 'k': 40, ';': 41, '\\': 42, ',': 43, '/': 44, 'n': 45, 'm': 46, '.': 47,
    ' ': 49
}


def send_string(pid, text, delay_between_keys=0.05):
    """
    Simulates typing the given text by sending key-down and key-up events for each character.
    A short delay is inserted between characters.
    """
    for char in text:
        char_lower = char.lower()
        if char_lower in VK_MAP:
            vk = VK_MAP[char_lower]
            send_key(pid, vk, True)
            time.sleep(0.01)
            send_key(pid, vk, False)
            time.sleep(delay_between_keys)
        else:
            print(f"Character '{char}' not mapped. Skipping.")
            time.sleep(delay_between_keys)


def task_cmd_enter(pid, interval_seconds):
    """
    Sends CMD+ENTER to the target process every interval_seconds.
    """
    while True:
        send_cmd_enter(pid)
        time.sleep(interval_seconds)
        print("CMD + ENTER")


def task_continue(pid, interval_minutes, message="continue", delay_between_keys=0.05):
    """
    Simulates typing the given message into the target process every interval_minutes,
    then presses Enter.
    """
    while True:
        send_string(pid, message, delay_between_keys)
        # Press Enter (key code 36)
        send_key(pid, 36, True)
        time.sleep(0.01)
        send_key(pid, 36, False)
        time.sleep(interval_minutes * 60)
        print("=== continue ===")



if __name__ == "__main__":
    # ----- Customizable Parameters -----
    #target_app = input("Enter the target application's name (e.g., TextEdit): ")
    interval_cmd_enter = 11  # Seconds between CMD+ENTER
    interval_continue = 2  # Minutes between typing "continue"
    message = "continue doing what you think is best."  # The text to type every interval_continue minutes
    # -------------------------------------

    target_app = "Cursor"
    pid = get_pid(target_app)
    if pid is None:
        exit(1)
    print(f"Target app '{target_app}' (pid: {pid}) found.")

    # Start tasks in separate threads
    thread_cmd_enter = threading.Thread(target=task_cmd_enter, args=(pid, interval_cmd_enter))
    thread_continue = threading.Thread(target=task_continue, args=(pid, interval_continue, message))

    thread_cmd_enter.daemon = True
    thread_continue.daemon = True

    thread_cmd_enter.start()
    thread_continue.start()

    print(
        f"Running: CMD+ENTER every {interval_cmd_enter} seconds, and typing '{message}' every {interval_continue} minutes.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped.")
