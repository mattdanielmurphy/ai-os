import pty
import os
import subprocess
import time

master, slave = pty.openpty()
p = subprocess.Popen(["tmux", "new-session", "-A", "-s", "test_tmux_refresh"], stdin=slave, stdout=slave, stderr=slave)

time.sleep(1)
os.write(master, b"echo hello\n")
time.sleep(1)

# Read all output
import fcntl
flags = fcntl.fcntl(master, fcntl.F_GETFL)
fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)

try:
    print("FIRST READ:")
    print(os.read(master, 8192))
except:
    pass

print("Triggering refresh...")
subprocess.run(["tmux", "refresh-client"])
time.sleep(1)

try:
    print("SECOND READ:")
    print(os.read(master, 8192))
except Exception as e:
    print(f"Nothing read: {e}")

subprocess.run(["tmux", "kill-session", "-t", "test_tmux_refresh"])
