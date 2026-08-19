---
title: "Fixing Zsh Insecure Directories"
date: "2026-08-08"
conversation_id: "eb3c43e4-ef10-4f90-9b97-9ecd6edd886a"
source: "antigravity"
---

# Fixing Zsh Insecure Directories

## User

figure out why I'm seeing this in Warp:
```
zsh compinit: insecure directories, run compaudit for list.
Ignore insecure directories and continue [y] or abort compinit [n]? 
```

I think I updated zshrc recently

---

## Assistant

Created At: 2026-08-07T20:08:18-06:00
Completed At: 2026-08-07T20:08:18-06:00

				The command exited with code 1.
				Output:
				not interactive and can't open terminal
compinit: initialization aborted
not interactive and can't open terminal
compinit: initialization aborted
/Users/matt/.bun/_bun:1038: command not found: compdef
not interactive and can't open terminal
compinit: initialization aborted
There are insecure directories:
/opt/homebrew/share
/usr/local/share

Created At: 2026-08-07T20:08:20-06:00
Completed At: 2026-08-07T20:08:20-06:00

				The command exited with code 0.
				Output:
				drwxrwxr-x@ 70 matt  admin  2240 Aug  6 19:56 /opt/homebrew/share
drwxr-xr-x@  3 matt  admin    96 Nov  3  2024 /opt/homebrew/share/zsh
drwxr-xr-x@ 20 matt  admin   640 Aug  5 16:29 /opt/homebrew/share/zsh/site-functions
drwxrwxr-x@ 61 matt  admin  1952 Jul  5 15:52 /usr/local/share

Created At: 2026-08-07T20:08:21-06:00
Completed At: 2026-08-07T20:08:21-06:00
File Path: `file:///Users/matt/.zshrc`
Total Lines: 287
Total Bytes: 10336
Showing lines 1 to 150
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # ENABLE AUTO-COMPLETE
2: if type brew &>/dev/null; then
3:   FPATH=$(brew --prefix)/share/zsh-completions:$FPATH
4:   autoload -Uz compinit
5:   compinit
6: fi
7: 
8: # PATHS
9: export PATH="/Users/matt/Library/Python/3.9/bin:$PATH"
10: export PATH="/Users/matt/audio-orchestrator-ffmpeg/bin:$PATH"
11: export PATH="$HOME/bin:/usr/local/bin:$PATH"
12: export PATH="/Users/matt/.local/bin:$PATH"
13: export PATH="/Users/matt/.antigravity-ide/antigravity-ide/bin:$PATH"
14: export PATH="$HOME/.cargo/bin:$PATH"
15: export PATH="$HOME/.openvlt/bin:$PATH"
16: 
17: # Go (GOPATH/bin)
18: case ":$PATH:" in
19:   *":$HOME/go/bin:"*) ;;
20:   *) export PATH="$HOME/go/bin:$PATH" ;;
21: esac
22: 
23: # Environment Fixes
24: export TMPDIR=/tmp
25: 
26: # Node Environment Manager (fnm)
27: eval "$(fnm env --use-on-cd)"
28: 
29: # pnpm Setup removed
30: 
31: # Bun Runtime
32: export BUN_INSTALL="$HOME/.bun"
33: export PATH="$BUN_INSTALL/bin:$PATH"
34: [ -s "/Users/matt/.bun/_bun" ] && source "/Users/matt/.bun/_bun"
35: 
36: # Zsh Completions
37: fpath=(~/.zsh/completions $fpath)
38: autoload -Uz compinit
39: compinit
40: 
41: # =====================================================================
42: # CUSTOM ALIAS FUNCTION (handles dynamic runtime adjustments)
43: # =====================================================================
44: alias() {
45:   if [[ $# -eq 0 ]]; then
46:     command alias
47:     return
48:   fi
49: 
50:   if [[ "$1" == "-s" ]]; then
51:     shift
52:   fi
53: 
54:   local alias_name="$1"
55:   shift
56:   local command="$*"
57: 
58:   if [[ -z "$alias_name" || -z "$command" ]]; then
59:   
<truncated 1155 bytes>
===============================================
95: 
96: function pd() {
97:   if [[ -d "api" ]] || [[ -f "vercel.json" ]] || grep -q "@vercel/node" package.json 2>/dev/null; then
98:     echo "📡 Vercel API detected, running vercel dev..."
99:     vercel dev
100:   else
101:     echo "🚀 Running bun dev..."
102:     bun run dev
103:   fi
104: }
105: 
106: reset-cursor() {
107:   curl -fsSL https://raw.githubusercontent.com/yuaotian/go-cursor-help/master/scripts/install.sh | sudo bash
108: }
109: 
110: ogg2mp3() {
111:   if [[ $# -lt 1 || $# -gt 2 ]]; then
112:     echo "Usage: ogg2mp3 <input-filepath> [output-filepath|output-filename]" >&2
113:     return 1
114:   fi
115:   local in="$1"
116:   if [[ ! -f "$in" ]]; then
117:     echo "ogg2mp3: input file not found: $in" >&2
118:     return 1
119:   fi
120:   local out
121:   if [[ $# -eq 1 ]]; then
122:     out="${in%.*}.mp3"
123:   else
124:     local out_arg="$2"
125:     local in_dir="${in:h}"
126:     if [[ "$out_arg" == */* ]]; then
127:       out="$out_arg"
128:     else
129:       if [[ "$in_dir" == "$in" ]]; then
130:         out="$out_arg"
131:       else
132:         out="${in_dir}/$out_arg"
133:       fi
134:     fi
135:     [[ "$out" != *.mp3 ]] && out="${out%.*}.mp3"
136:   fi
137:   echo "Converting:\n  IN : $in\n  OUT: $out"
138:   ffmpeg -i "$in" -codec:a libmp3lame -qscale:a 2 "$out"
139: }
140: 
141: yt-dl() {
142:     local video_url=""
143:     local auto_open=false
144:     local hide_spoilers=false
145:     local series_episode_detection
146:     local extra_args=()
147:     local ffmpeg_path="/Users/matt/audio-orchestrator-ffmpeg/bin/ffmpeg"
148:     local temp_download_dir="$HOME/Downloads"
149:     local final_dir="/Users/matt/Library/CloudStorage/CloudMounter-MattMurphy/YouTube"
150:     local GEMINI_API_KEY='[REDACTED_GOOGLE_API_KEY]'
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-07T20:08:26-06:00
Completed At: 2026-08-07T20:08:26-06:00

				The command exited with code 127.
				Output:
				zsh:1: command not found: compaudit

Created At: 2026-08-07T20:08:27-06:00
Completed At: 2026-08-07T20:08:27-06:00

				The command exited with code 1.
				Output:
				There are insecure directories:
/usr/local/share

Created At: 2026-08-07T20:08:29-06:00
Completed At: 2026-08-07T20:08:29-06:00

				The command exited with code 1.
				Output:
				There are insecure directories:
/opt/homebrew/share
/usr/local/share

Created At: 2026-08-07T20:08:30-06:00
Completed At: 2026-08-07T20:08:30-06:00

				The command exited with code 0.
				Output:
				drwxrwxr-x@  70 matt  admin  2240 Aug  6 19:56 /opt/homebrew/share
drwxr-xr-x@   3 matt  admin    96 Nov  3  2024 /opt/homebrew/share/zsh
drwxr-xr-x@ 182 matt  admin  5824 Aug  6 19:56 /opt/homebrew/share/zsh-completions
drwxr-xr-x@  20 matt  admin   640 Aug  5 16:29 /opt/homebrew/share/zsh/site-functions
drwxrwxr-x@  61 matt  admin  1952 Jul  5 15:52 /usr/local/share

Created At: 2026-08-07T20:08:32-06:00
Completed At: 2026-08-07T20:08:32-06:00

				The command exited with code 0.
				Output:
				drwxr-xr-x@  3 matt  admin   96 Jul 17  2025 /usr/local/share/zsh
drwxr-xr-x@ 17 matt  admin  544 Jul  9 20:50 /usr/local/share/zsh/site-functions

Created At: 2026-08-07T20:08:35-06:00
Completed At: 2026-08-07T20:08:35-06:00
No background tasks are currently running.

### Why This is Happening

When Zsh's completion system (`compinit`) initializes, it runs security checks via `compaudit` on all completion directories in `$fpath` and their parent directories. If any of those directories are **group-writable** (even if owned by your user and group `admin`), Zsh halts with the warning:

```
zsh compinit: insecure directories, run compaudit for list.
Ignore insecure directories and continue [y] or abort compinit [n]? 
```

Running `compaudit` reveals the culprit directories:
- `/opt/homebrew/share` (`drwxrwxr-x` — group `admin` has write permission `w`)
- `/usr/local/share` (`drwxrwxr-x` — group `admin` has write permission `w`)

In your [~/.zshrc](file:///Users/matt/.zshrc#L1-L6), `compinit` is executed right at the top when adding Homebrew completions:

```zsh
if type brew &>/dev/null; then
  FPATH=$(brew --prefix)/share/zsh-completions:$FPATH
  autoload -Uz compinit
  compinit
fi
```

---

### How to Fix It

You have two clean options:

#### Option 1: Fix Directory Permissions (Recommended)

Remove group-write permissions from the affected directories so `compaudit` passes:

```bash
chmod g-w /opt/homebrew/share /usr/local/share
```

You can verify that `compaudit` is satisfied by running:
```bash
zsh -c "autoload -Uz compaudit; compaudit"
```
*(If it returns no output, all insecure directory warnings are resolved).*

---

#### Option 2: Tell `compinit` to Skip/Bypass Insecure Directory Prompts

If you prefer not to alter system directory permissions, you can tell `compinit` in [~/.zshrc](file:///Users/matt/.zshrc#L5) to automatically use insecure directories without asking:

```zsh
autoload -Uz compinit
compinit -u
```

*(Note: `-u` uses them without prompting; `-i` silently ignores insecure directories without loading them).*

---

### Additional `~/.zshrc` Cleanup Note

In your [~/.zshrc](file:///Users/matt/.zshrc), `compinit` is currently called **twice**:
1. At **lines 1–6**: Inside the Homebrew block.
2. At **lines 36–39**: Under `# Zsh Completions`.

Also, [line 34](file:///Users/matt/.zshrc#L34) sources `~/.bun/_bun` (which requires `compdef` from `compinit`). If the first `compinit` is aborted at startup, `_bun` throws `command not found: compdef`. Consolidating `fpath` and calling `compinit -u` once before `_bun` keeps your shell startup fast and error-free.

---
Conversation thread artifact:

---

## User

do op1 for me

---

## Assistant

Created At: 2026-08-07T20:08:51-06:00
Completed At: 2026-08-07T20:08:52-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-07T20:08:53-06:00
Completed At: 2026-08-07T20:08:53-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-07T20:08:54-06:00
Completed At: 2026-08-07T20:08:54-06:00

				The command exited with code 0.
				Output:
				zsh init success

Created At: 2026-08-07T20:08:56-06:00
Completed At: 2026-08-07T20:08:56-06:00
No background tasks are currently running.

Group-write permissions have been removed from the insecure directories:

```bash
chmod g-w /opt/homebrew/share /usr/local/share
```

### Verification
- `compaudit` check: **Clean** (0 insecure directories found).
- Interactive `zsh -i` startup: **Success** (no prompts or warnings).

Warp and new terminal tabs will now launch cleanly without the `compinit` prompt.

---
Conversation thread artifact:

---
