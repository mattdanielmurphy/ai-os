#!/bin/zsh
# Claude Code Stop hook: keep the QMD index current with new Claude threads and vault edits.
# Returns immediately; the work runs detached, at most once every 15 minutes.
LOG="$HOME/.cache/qmd/refresh.log"
STAMP="$HOME/.cache/qmd/refresh.stamp"
LOCK="$HOME/.cache/qmd/refresh.lock"
mkdir -p "$HOME/.cache/qmd"
cat >/dev/null  # drain hook input

if [[ -f "$STAMP" ]] && (( $(date +%s) - $(stat -f %m "$STAMP") < 900 )); then
  exit 0
fi
mkdir "$LOCK" 2>/dev/null || exit 0
touch "$STAMP"

(
  export PATH="$HOME/.local/share/fnm/aliases/default/bin:$HOME/.bun/bin:$PATH"
  {
    date
    python3 "$HOME/projects/ai-os/scripts/export_claude_threads.py"
    qmd update
    qmd embed
  } >>"$LOG" 2>&1
  rmdir "$LOCK"
) </dev/null >/dev/null 2>&1 &!
exit 0
