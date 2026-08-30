#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.parse
import subprocess
import time
import contextlib
import shutil
from pathlib import Path

# Config and settings paths
SETTING_PATH = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
OAUTH_CREDS_PATH = Path.home() / ".gemini" / "oauth_creds.json"
TELEMETRY_DB_PATH = Path.home() / ".ai-os-telemetry.json"
ERROR_LOG_PATH = Path("/tmp/aios_last_cmd.log")

@contextlib.contextmanager
def hide_agents_md():
    """Temporarily renames AGENTS.md to prevent agy from loading it, avoiding double system prompts when launched by Hermes."""
    paths_to_hide = [Path("AGENTS.md"), Path(".agents/AGENTS.md")]
    hidden = []
    
    try:
        for p in paths_to_hide:
            if p.exists():
                bak = p.with_name(f".{p.name}.bak")
                try:
                    p.rename(bak)
                    hidden.append((bak, p))
                except Exception:
                    pass
        yield
    finally:
        for bak, original in hidden:
            if bak.exists():
                try:
                    bak.rename(original)
                except Exception:
                    pass

def get_access_token():
    if not OAUTH_CREDS_PATH.exists():
        return None
    try:
        token_data = json.loads(OAUTH_CREDS_PATH.read_text())
        return token_data.get("access_token")
    except Exception:
        return None

def get_quota():
    """Fetch quota remaining fraction for 5h/pro and weekly/flash windows."""
    token = get_access_token()
    if not token:
        return 1.0, 1.0, False  # Default to normal if we can't fetch

    url = "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota"
    req = urllib.request.Request(
        url,
        data=b"{}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            resp = json.loads(res.read().decode())
            buckets = resp.get("buckets", [])
            quota_5h = 1.0
            quota_week = 1.0
            is_real = False
            for bucket in buckets:
                model_id = bucket.get("modelId")
                fraction = bucket.get("remainingFraction", 1.0)
                if model_id == "gemini-2.5-pro":
                    quota_5h = fraction
                    is_real = True
                elif model_id == "gemini-2.5-flash":
                    quota_week = fraction
                    is_real = True
            return quota_5h, quota_week, is_real
    except Exception:
        return 1.0, 1.0, False

def query_gemini_flash_lite(prompt, system_instruction=None):
    """Hits the raw external Google AI API for classification / investigation using GEMINI_API_KEY or Oauth token."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as res:
                resp = json.loads(res.read().decode())
                return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            # Fallback to oauth
            pass

    # Fallback to oauth Google Pa API endpoint
    token = get_access_token()
    if token:
        url = "https://daily-cloudcode-pa.googleapis.com/v1internal:generateContent"
        full_text = prompt
        if system_instruction:
            full_text = f"{system_instruction}\n\n{prompt}"
        payload = {
            "project": "atlas-calculator",
            "model": "gemini-3.1-flash-lite",
            "request": {
                "contents": [{"parts": [{"text": full_text}]}]
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as res:
                resp = json.loads(res.read().decode())
                return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass
    return None

def tier1_triage(query):
    """Classifies user queries into standard models or special valve workflows."""
    system_instruction = (
        "You are the Tier 1 Triage Gateway router. Classify the user prompt/query. "
        "Respond ONLY with a deterministic JSON payload. No markdown blocks, no formatting. "
        "Output format:\n"
        "{\n"
        '  "category": "simple_non_coding" | "coding_standard" | "coding_complex" | "valve_boilerplate"\n'
        "}"
    )
    prompt = f"User query to classify:\n{query}"
    response_text = query_gemini_flash_lite(prompt, system_instruction)
    
    if not response_text:
        return "coding_standard"  # Safe default

    # Clean JSON output if wrapped in markdown formatting
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        data = json.loads(clean_text)
        return data.get("category", "coding_standard")
    except Exception:
        # Simple heuristic if JSON parse fails
        if "valve_boilerplate" in clean_text:
            return "valve_boilerplate"
        elif "coding_complex" in clean_text:
            return "coding_complex"
        elif "simple_non_coding" in clean_text:
            return "simple_non_coding"
        return "coding_standard"

def tier2_investigation(query, model_used, error_log):
    """Invoked when execution fails. Analyzes errors and determines escalation route."""
    system_instruction = (
        "You are the Tier 2 Executive Investigation & Escalation engine. "
        "Analyze the user's initial query, the model that was used, and the error traceback/diagnostics. "
        "Select the minimum escalation tier needed to achieve a patch and solve this issue. "
        "Respond ONLY with a JSON payload with keys: 'escalation_model' and 'reason'. "
        "Available escalation models are:\n"
        "- 'Gemini 3.1 Pro (High)' (advanced local reasoning)\n"
        "- 'GLM-5.2 (max)' (paid API fallback)\n"
        "- 'google-premium' (paid Google AI Premium endpoint)\n"
        "- 'Claude Fable 5' (highly complex/frontier layer)\n"
        "Output format:\n"
        "{\n"
        '  "escalation_model": "model_name",\n'
        '  "reason": "short explanation"\n'
        "}"
    )
    prompt = f"Original Query: {query}\nModel Used: {model_used}\nError Logs/Traceback:\n{error_log}"
    response_text = query_gemini_flash_lite(prompt, system_instruction)
    
    if not response_text:
        return "Gemini 3.1 Pro (High)"

    # Clean JSON
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        data = json.loads(clean_text)
        return data.get("escalation_model", "Gemini 3.1 Pro (High)")
    except Exception:
        return "Gemini 3.1 Pro (High)"

def run_valve_boilerplate(query):
    """Outputs instructions for the Fire-and-Forget Web UI Valve."""
    payload_instructions = (
        "== FIRE-AND-FORGET WEB UI VALVE ACTIVATED ==\n"
        "This is a massive boilerplate / isolated coding task. To conserve API quotas, run this on Perplexity or Gemini Web UI.\n\n"
        "COPY AND PASTE THE FOLLOWING PROMPT INTO THE WEB UI:\n"
        "--------------------------------------------------\n"
        f"Task instruction:\n{query}\n\n"
        "SYSTEM DIRECTIVE: When you have completed this code generation, you MUST conclude your response with a terminal tool-call block exactly formatted as:\n"
        "```tool-call\n"
        "write_file(path='path/to/target/file', content='...')\n"
        "```\n"
        "--------------------------------------------------\n"
        "The local userscript listener will automatically detect, scrape, and write this output to the codebase files.\n"
    )
    print(payload_instructions)
    sys.exit(0)

def open_gemini_webview_thread(query, model=None):
    """Dispatches prompt directly to the ai-os Tauri app via local HTTP server API,
    or launches ai-os app if not currently running."""
    print(f"[triage] Dispatching prompt ({len(query)} chars) to Gemini webview in ai-os...")

    # 1. Copy prompt to macOS clipboard as fallback
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(input=query.encode("utf-8"))
    except Exception:
        pass

    # 2. Attempt HTTP POST to local AI-OS Tauri Axum server (127.0.0.1:3031/api/prompt)
    payload = json.dumps({"prompt": query}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:3031/api/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=2) as res:
            if res.status == 200:
                print("[triage] Successfully dispatched prompt directly to running AI-OS Gemini window!")
                sys.exit(0)
    except Exception:
        pass

    # 3. If AI-OS app server is not running, write pending prompt file and launch /Applications/ai-os.app
    print("[triage] AI-OS app not currently active. Launching /Applications/ai-os.app with pending prompt...")
    pending_file = Path.home() / ".ai-os" / "pending_prompt.txt"
    pending_file.parent.mkdir(parents=True, exist_ok=True)
    pending_file.write_text(query, encoding="utf-8")

    app_paths = [
        Path("/Applications/ai-os.app"),
        Path("/Applications/AI-OS.app"),
        Path.home() / "Applications" / "ai-os.app",
        Path.home() / "Applications" / "AI-OS.app"
    ]
    
    launched = False
    for app_path in app_paths:
        if app_path.exists():
            subprocess.run(["open", str(app_path)])
            launched = True
            break
            
    if not launched:
        res = subprocess.run(["open", "-a", "AI-OS"], stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            subprocess.run(["open", "-a", "ai-os"], stderr=subprocess.DEVNULL)

    sys.exit(0)

def open_perplexity_webview_thread(query, model=None):
    """Dispatches prompt directly to the ai-os Perplexity webview via local HTTP server API,
    or launches ai-os app if not currently running."""
    print(f"[triage] Dispatching prompt ({len(query)} chars) to Perplexity webview in ai-os...")

    # 1. Copy prompt to macOS clipboard as fallback
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(input=query.encode("utf-8"))
    except Exception:
        pass

    # 2. Attempt HTTP POST to local AI-OS Tauri Axum server (127.0.0.1:3031/api/perplexity/prompt)
    payload = json.dumps({"prompt": query, "model": model}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:3031/api/perplexity/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=2) as res:
            if res.status == 200:
                print("[triage] Successfully dispatched prompt directly to running AI-OS Perplexity window!")
                sys.exit(0)
    except Exception:
        pass

    # 3. If AI-OS app server is not running, write pending prompt file and launch /Applications/ai-os.app
    print("[triage] AI-OS app not currently active. Launching /Applications/ai-os.app with pending Perplexity prompt...")
    pending_file = Path.home() / ".ai-os" / "pending_pplx_prompt.txt"
    pending_file.parent.mkdir(parents=True, exist_ok=True)
    pending_file.write_text(query, encoding="utf-8")

    app_paths = [
        Path("/Applications/ai-os.app"),
        Path("/Applications/AI-OS.app"),
        Path.home() / "Applications" / "ai-os.app",
        Path.home() / "Applications" / "AI-OS.app"
    ]
    
    launched = False
    for app_path in app_paths:
        if app_path.exists():
            subprocess.run(["open", str(app_path)])
            launched = True
            break
            
    if not launched:
        res = subprocess.run(["open", "-a", "AI-OS"], stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            subprocess.run(["open", "-a", "ai-os"], stderr=subprocess.DEVNULL)

    sys.exit(0)

def get_antigravity_window_bounds():
    """Gets (x, y, w, h) of window 1 of Antigravity process."""
    try:
        res = subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to tell process "Antigravity" to return (position of window 1) & (size of window 1)'
        ], capture_output=True, text=True, timeout=3)
        parts = [int(p.strip()) for p in res.stdout.strip().replace("{", "").replace("}", "").split(",")]
        if len(parts) == 4:
            return parts[0], parts[1], parts[2], parts[3]
    except Exception:
        pass
    return 0, 38, 1200, 800

def click_coords(x, y):
    """Sends a hardware mouse click event at screen coordinates (x, y)."""
    import ctypes
    cg = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")
    class CGPoint(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]
    cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
    cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
    cg.CGEventPost.restype = None
    cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

    pt = CGPoint(x, y)
    event_down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    event_up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, event_down)
    cg.CGEventPost(0, event_up)

def launch_antigravity_app(query, model=None):
    """Launches / opens /Applications/Antigravity.app, copies prompt to clipboard,
    opens new conversation with Shift+Cmd+O twice, resets element list with a top-right click,
    tabs twice to the textarea, pastes, and sends."""
    print(f"[triage] Opening /Applications/Antigravity.app with prompt ({len(query)} chars)...")
    
    # 1. Copy prompt to macOS system clipboard
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(input=query.encode("utf-8"))
    except Exception:
        pass

    # 2. Activate Antigravity, ensure frontmost focus, and press Shift+Cmd+O twice (key code 31)
    applescript_step1 = '''
    tell application "Antigravity" to activate
    repeat 10 times
        tell application "System Events"
            if frontmost of process "Antigravity" is true then exit repeat
        end tell
        delay 0.1
    end repeat
    delay 0.3
    tell application "System Events"
        -- Key code 31 = 'O' (Shift + Cmd + O)
        key code 31 using {command down, shift down}
        delay 0.3
        key code 31 using {command down, shift down}
        delay 0.6
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript_step1])

    # 3. Perform mouse click 100px from right, 100px from top of window to reset focus
    x, y, w, h = get_antigravity_window_bounds()
    click_x = x + w - 100
    click_y = y + 100
    print(f"[triage] Performing focus reset click at ({click_x}, {click_y})...")
    click_coords(click_x, click_y)
    time.sleep(0.3)

    # 4. Tab twice to bring focus to textarea, paste prompt, and send (Return)
    applescript_step2 = '''
    tell application "System Events"
        -- Press Tab twice to select textarea from reset state
        key code 48
        delay 0.2
        key code 48
        delay 0.3
        -- Paste prompt from clipboard
        keystroke "v" using {command down}
        delay 0.3
        -- Send prompt (Return key)
        key code 36
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript_step2])
    sys.exit(0)

APP_ALIASES = {
    "google": "Google Chrome",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "google chrome.app": "Google Chrome",
    "vscode": "Visual Studio Code",
    "code": "Visual Studio Code",
    "sublime": "Sublime Text",
    "sublime text": "Sublime Text",
    "terminal": "Terminal",
    "iterm": "iTerm",
    "iterm2": "iTerm",
    "finder": "Finder",
    "calculator": "Calculator",
    "system settings": "System Settings",
    "settings": "System Settings",
    "preferences": "System Settings",
    "system preferences": "System Settings",
    "notes": "Notes",
    "messages": "Messages",
    "mail": "Mail",
    "music": "Music",
    "photos": "Photos",
    "safari": "Safari",
    "slack": "Slack",
    "discord": "Discord",
    "spotify": "Spotify",
    "arc": "Arc",
    "brave": "Brave Browser",
    "cursor": "Cursor"
}

def try_direct_execution(query):
    """Attempts fast direct execution for simple OS commands (open app, open URL, kill process, etc.)
    without starting LLM reasoning models or launching agy.
    Returns True if handled, False otherwise."""
    q = query.strip().rstrip(".!?;:")
    if not q:
        return False
    q_lower = q.lower()

    # Strip common spoken conversational filler prefixes:
    conversational_prefixes = [
        "i'll ", "i will ", "please ", "can you ", "could you ", "would you ", "go ahead and ", "let's "
    ]
    for cp in conversational_prefixes:
        if q_lower.startswith(cp):
            q = q[len(cp):].strip().rstrip(".!?;:")
            q_lower = q.lower()
            break

    # 1. Open app / URL / file pattern
    open_prefixes = ["open ", "launch ", "start "]
    matched_prefix = None
    for prefix in open_prefixes:
        if q_lower.startswith(prefix):
            matched_prefix = prefix
            break
            
    if matched_prefix:
        target = q[len(matched_prefix):].strip().strip("'\"").rstrip(".!?;:")
        target_lower = target.lower()

        # Is it a URL?
        if target_lower.startswith(("http://", "https://", "www.")):
            url = target if not target_lower.startswith("www.") else f"https://{target}"
            print(f"[triage] Fast-path direct execution: opening URL '{url}'")
            res = subprocess.run(["open", url])
            return res.returncode == 0

        # Is it an existing file or directory path?
        expanded_path = Path(os.path.expanduser(target))
        if expanded_path.exists():
            print(f"[triage] Fast-path direct execution: opening path '{expanded_path}'")
            res = subprocess.run(["open", str(expanded_path)])
            return res.returncode == 0

        # Try App alias mapping
        app_name = APP_ALIASES.get(target_lower)
        if app_name:
            print(f"[triage] Fast-path direct execution: launching application '{app_name}'")
            res = subprocess.run(["open", "-a", app_name])
            if res.returncode == 0:
                return True

        # Try raw target string with `open -a`
        print(f"[triage] Fast-path direct execution: attempting to open application '{target}'")
        res = subprocess.run(["open", "-a", target], stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

        # Try title-case target string
        res = subprocess.run(["open", "-a", target.title()], stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return True

        # Check /Applications or /System/Applications for matching .app bundle
        app_dirs = [Path("/Applications"), Path("/System/Applications"), Path.home() / "Applications"]
        for app_dir in app_dirs:
            if app_dir.exists():
                for item in app_dir.rglob("*.app"):
                    if item.stem.lower() == target_lower or item.name.lower() == f"{target_lower}.app":
                        print(f"[triage] Fast-path direct execution: found app bundle '{item}'")
                        res = subprocess.run(["open", str(item)])
                        if res.returncode == 0:
                            return True

    # 2. Kill / process termination pattern
    kill_prefixes = ["killall ", "pkill "]
    for prefix in kill_prefixes:
        if q_lower.startswith(prefix):
            proc_target = q[len(prefix):].strip()
            cmd_name = prefix.strip()
            print(f"[triage] Fast-path direct execution: running '{cmd_name} {proc_target}'")
            res = subprocess.run([cmd_name, proc_target])
            return res.returncode == 0

    # 3. Text to speech pattern
    if q_lower.startswith("say "):
        text = q[4:].strip()
        print(f"[triage] Fast-path direct execution: speaking text")
        res = subprocess.run(["say", text])
        return res.returncode == 0

    # 4. Explicit run/exec command
    if q_lower.startswith("run ") or q_lower.startswith("exec "):
        raw_cmd = q.split(" ", 1)[1].strip()
        print(f"[triage] Fast-path direct execution: executing '{raw_cmd}'")
        res = subprocess.run(raw_cmd, shell=True)
        return res.returncode == 0

    return False

def main():
    args = sys.argv[1:]
    
    # 1. Parse manual model overrides
    has_model = False
    model_override = None
    for i, arg in enumerate(args):
        if arg == "--model" and i + 1 < len(args):
            has_model = True
            model_override = args[i+1]
            break

    # 2. Extract query/prompt if present
    non_flag_args = [arg for arg in args if not arg.startswith("-")]
    query = " ".join(non_flag_args) if non_flag_args else ""
            
    # Default behavior for interactive shell
    if not query:
        model = model_override or "Gemini 3.5 Flash (Low)"
        print(f"[triage] Interactive mode or empty prompt: launching agy with {model}")
        cmd = ["agy"] + args
        if not has_model:
            cmd += ["--model", model]
        with hide_agents_md():
            sys.exit(subprocess.call(cmd))

    # Bypassing classification if model override is provided
    if has_model:
        model = model_override
        print(f"[triage] Model override provided: running {model}")
        cmd = ["agy"] + args
        with hide_agents_md():
            sys.exit(subprocess.call(cmd))

    # Fast-path direct execution check (e.g. "open google chrome")
    if try_direct_execution(query):
        sys.exit(0)

    # 3. Tier 1 Classification
    print(f"[triage] Intercepting prompt: '{query[:50]}...'")
    category = tier1_triage(query)
    print(f"[triage] Classified category: {category}")

    # 4. Route selection
    selected_model = "Gemini 3.5 Flash (Low)"
    
    is_coding_intent = category in ["coding_standard", "coding_complex"] or any(
        kw in query.lower() for kw in ["file", "find", "search", "code", "repo", "script", "fix", "debug", "refactor", "build", "run", "git"]
    )

    if category == "simple_non_coding" and not is_coding_intent:
        selected_model = "Gemini 3.5 Flash (Low)"
    elif category == "coding_standard" or is_coding_intent:
        quota_5h, quota_week, is_real = get_quota()
        if is_real and quota_5h < 0.20:
            print(f"[triage] Quota < 20% ({int(quota_5h * 100)}%). Throttling to Gemini 3.1 Pro (Low) to conserve resources.")
            selected_model = "Gemini 3.1 Pro (Low)"
        else:
            selected_model = "Gemini 3.5 Flash (Low)"
    elif category == "coding_complex":
        selected_model = "Gemini 3.1 Pro (High)"
    elif category == "valve_boilerplate":
        run_valve_boilerplate(query)

    # Check if CLI execution was explicitly requested via flags
    force_cli = any(arg in args for arg in ["--cli", "--terminal", "--agy", "--claude"]) or query.startswith("/")

    if force_cli:
        print(f"[triage] Explicit CLI flag detected: running terminal agy with {selected_model}")
        cmd = ["agy", "--model", selected_model]
        for arg in args:
            if arg in ["--model", "--cli", "--terminal", "--agy"]:
                continue
            cmd.append(arg)
        with hide_agents_md():
            sys.exit(subprocess.call(cmd))

    # Route based on prompt intent:
    if is_coding_intent:
        # Coding / file / codebase task -> Launch / open /Applications/Antigravity.app
        launch_antigravity_app(query, selected_model)
    else:
        # Non-coding general query -> Open Gemini Webview in ai-os app
        open_gemini_webview_thread(query, selected_model)

    # 6. Tier 2 Executive Investigation on failure
    if exit_code != 0:
        print("\n[triage] Initial execution encountered a crash. Triggering Tier 2 Executive Investigation...")
        error_log = ""
        if ERROR_LOG_PATH.exists():
            try:
                error_log = ERROR_LOG_PATH.read_text()[-2000:] # Last 2k chars
            except Exception:
                pass
        
        escalated_model = tier2_investigation(query, selected_model, error_log)
        print(f"[triage] Tier 2 escalation target computed: {escalated_model}")

        if escalated_model == "Claude Fable 5":
            print("[triage] HALT: Claude Fable 5 is strictly barred from autonomous invocation due to cost limits.")
            print("[triage] Manual human intervention is required to run this model.")
            sys.exit(exit_code)
        
        # Google Premium and GLM-5.2 are paid endpoints not directly mapped in standard agy list
        if escalated_model in ["GLM-5.2 (max)", "google-premium"]:
            print(f"[triage] Out-of-pocket escalation route selected: {escalated_model}.")
            print("Please configure external API credentials or run manually on premium endpoints.")
            sys.exit(exit_code)

        # Retry/escalate with Gemini 3.1 Pro (High)
        print(f"[triage] Automatically retrying with escalated reasoning model: {escalated_model}...")
        cmd_escalated = ["agy", "--model", escalated_model]
        for arg in args:
            if arg == "--model":
                continue
            cmd_escalated.append(arg)
        with hide_agents_md():
            sys.exit(subprocess.call(cmd_escalated))

    sys.exit(0)

if __name__ == "__main__":
    main()
