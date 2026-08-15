python3 scripts/precision_edit.py scripts/subagent.py replace --target 'def _kill_pane():
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0.0", "C-c"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0.0", "Enter"], stderr=subprocess.DEVNULL)
    time.sleep(0.3)


def _respawn(cmd: str):
    _kill_pane()
    subprocess.run(["tmux", "respawn-pane", "-k", "-t", f"{SESSION}:0.0", "bash", "-c", cmd],
                   check=True, capture_output=True, timeout=5)' --content 'def _allocate_pane() -> str:
    output = subprocess.check_output(["tmux", "list-panes", "-t", f"{SESSION}:0", "-F", "#{pane_id} #{pane_dead} #{@busy}"]).decode("utf-8")
    panes = [line.strip().split() for line in output.strip().split("\n") if line.strip()]
    
    for parts in panes:
        pane_id = parts[0]
        is_dead = parts[1]
        is_busy = parts[2] if len(parts) > 2 else ""
        if is_dead == "1" or is_busy != "1":
            subprocess.run(["tmux", "set-option", "-p", "-t", pane_id, "@busy", "1"])
            return pane_id

    output = subprocess.check_output(["tmux", "split-window", "-d", "-t", f"{SESSION}:0", "-P", "-F", "#{pane_id}", "bash"]).decode("utf-8")
    pane_id = output.strip()
    subprocess.run(["tmux", "set-option", "-p", "-t", pane_id, "@busy", "1"])
    return pane_id


def _cleanup_pane(pane_id: str):
    subprocess.run(["tmux", "set-option", "-p", "-t", pane_id, "@busy", "0"])
    output = subprocess.check_output(["tmux", "list-panes", "-t", f"{SESSION}:0", "-F", "#{pane_id}"]).decode("utf-8")
    panes = [line.strip() for line in output.strip().split("\n") if line.strip()]
    if len(panes) > 1:
        subprocess.run(["tmux", "kill-pane", "-t", pane_id])


def _kill_pane(pane_id: str):
    subprocess.run(["tmux", "send-keys", "-t", pane_id, "C-c"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", pane_id, "Enter"], stderr=subprocess.DEVNULL)
    time.sleep(0.3)


def _respawn(pane_id: str, cmd: str):
    _kill_pane(pane_id)
    subprocess.run(["tmux", "respawn-pane", "-k", "-t", pane_id, "bash", "-c", cmd],
                   check=True, capture_output=True, timeout=5)'
