import subprocess
import time

session_name = "test_shell_interactive"
subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)
# Start session running zsh
subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "zsh"])
time.sleep(0.5)

# Find pane tty
proc = subprocess.run(["tmux", "display-message", "-t", session_name, "-p", "#{pane_tty}"], capture_output=True, text=True)
pane_tty = proc.stdout.strip()

# Let's write a multiline command that runs a program, with actual line breaks:
# Wait, when zsh receives a carriage return/newline, does it try to execute immediately if it's not bracketed?
# Let's try writing:
# echo "line 1
# line 2"
# to the tty.
with open(pane_tty, "wb") as f:
    f.write(b'echo "line 1\rline 2"\r')
    f.flush()

time.sleep(0.5)
cap = subprocess.run(["tmux", "capture-pane", "-p", "-t", session_name], capture_output=True, text=True)
print("Captured (with \\r):")
print(repr(cap.stdout))

subprocess.run(["tmux", "kill-session", "-t", session_name])
