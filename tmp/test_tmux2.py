import pty
import os
import subprocess
import time

# Create a session first
subprocess.run(["tmux", "new-session", "-d", "-s", "test_attach_session", "echo running; sleep 10"])
time.sleep(1)

master, slave = pty.openpty()
p = subprocess.Popen(["tmux", "new-session", "-A", "-s", "test_attach_session"], stdin=slave, stdout=slave, stderr=slave)

time.sleep(1)

import fcntl
flags = fcntl.fcntl(master, fcntl.F_GETFL)
fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)

try:
    print("READ:")
    print(os.read(master, 8192))
except Exception as e:
    print(f"Nothing read: {e}")

subprocess.run(["tmux", "kill-session", "-t", "test_attach_session"])
