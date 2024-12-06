import time
import sys


def waiting_print(text, timeout=None, state=None):
    
    # timeout in seconds

    interval = 0.1  # Duration of each fade in/out cycle in seconds

    if timeout:
        end_time = time.time() + timeout

        while time.time() < end_time:
            printing(text, interval)

    if state:
        actual_state = state.current_state
        while state.current_state == actual_state:
            printing(text, interval)

    # # Print the final text without clearing it
    # sys.stdout.write(f"\r{text}\n")

def printing(text, interval):
    for i in range(len(text) + 1):
            # Print the text partially
            sys.stdout.write(f"\r{text[:i]}")
            sys.stdout.flush()
            time.sleep(interval)
    for i in range(len(text) + 1):
        # Clear the text partially
        sys.stdout.write(f"\r{' ' * (len(text) - i)}")
        sys.stdout.flush()
        # time.sleep(interval)




