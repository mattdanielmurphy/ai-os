#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pexpect",
# ]
# ///
import pexpect
import time
import threading
import os
import sys

def trigger_editor(child):
    time.sleep(2)
    try:
        child.send(b'\x07')
    except Exception:
        pass

def main():
    try:
        # Get the exact size of the active split pane file descriptor
        size = os.get_terminal_size(sys.stdin.fileno())
        # Subtract a tiny padding margin to handle Warp's borders/chrome
        columns = size.columns - 2
        lines = size.lines - 1
    except Exception:
        columns, lines = 100, 40

    child = pexpect.spawn('claude', encoding=None)
    child.setwinsize(lines, columns)
    
    t = threading.Thread(target=trigger_editor, args=(child,), daemon=True)
    t.start()
    
    child.interact()

if __name__ == '__main__':
    main()
