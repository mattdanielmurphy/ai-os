#!/usr/bin/env python3
import sys
import os
import re
import math
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
HAL_SPEAK_SCRIPT = Path("/Users/matt/projects/ai-os/services/tts-hal/speak.py")

def show_gui_overlay(message: str, duration: float = 3.5):
    """Displays a fast floating HUD overlay on macOS via Hammerspoon or osascript."""
    # 1. Try Hammerspoon HUD alert (instant centered on-screen badge)
    try:
        clean_msg = message.replace('"', '\\"').replace("'", "\\'")
        lua = f'hs.alert.closeAll(); hs.alert.show([[{clean_msg}]], {duration})'
        applescript = f'tell application "Hammerspoon" to execute lua code "{lua}"'
        res = subprocess.run(
            ["osascript", "-e", applescript],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=0.6
        )
        if res.returncode == 0:
            return
    except Exception:
        pass

    # 2. Fallback to native macOS Notification Center banner
    try:
        clean_msg = message.replace('"', '\\"')
        subprocess.Popen(
            ["osascript", "-e", f'display notification "{clean_msg}" with title "HAL-9000"'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def speak_hal(text: str, non_blocking: bool = True):
    """Speaks text using HAL-9000 acoustic voice engine."""
    if HAL_SPEAK_SCRIPT.exists():
        cmd = [sys.executable, str(HAL_SPEAK_SCRIPT), text]
        if not non_blocking:
            cmd.append("--sync")
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

def evaluate_math_phrase(q: str) -> str | None:
    """Safely evaluates common spoken math and calculation queries."""
    q_clean = q.lower().strip().rstrip("?.! ")
    # Strip leading filler words
    for prefix in ["what is the ", "what's the ", "what is ", "what's ", "calculate ", "compute ", "tell me the ", "tell me "]:
        if q_clean.startswith(prefix):
            q_clean = q_clean[len(prefix):].strip()
            break

    # 1. Square root
    m = re.search(r"^(?:the\s+)?square root of ([0-9]+(?:\.[0-9]+)?)$", q_clean)
    if m:
        val = float(m.group(1))
        if val < 0:
            return "The square root of a negative number is not a real number."
        res = math.isqrt(int(val)) if val.is_integer() and math.isqrt(int(val))**2 == int(val) else round(math.sqrt(val), 4)
        return f"The square root of {m.group(1)} is {res}."

    # 2. Percentage: "15% of 80" or "15 percent of 80"
    m = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s*(?:%|percent)\s+of\s+([0-9]+(?:\.[0-9]+)?)$", q_clean)
    if m:
        pct = float(m.group(1))
        base = float(m.group(2))
        res = (pct / 100.0) * base
        res_str = int(res) if res.is_integer() else round(res, 4)
        return f"{m.group(1)} percent of {m.group(2)} is {res_str}."

    # 3. Power / Exponent: "2 to the power of 8"
    m = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s+(?:to the power of|\^)\s+([0-9]+(?:\.[0-9]+)?)$", q_clean)
    if m:
        base = float(m.group(1))
        exp = float(m.group(2))
        res = base ** exp
        res_str = int(res) if res.is_integer() else round(res, 4)
        return f"{m.group(1)} to the power of {m.group(2)} is {res_str}."

    # 4. Basic Arithmetic: A (plus|minus|times|divided by) B
    m = re.search(r"^([0-9]+(?:\.[0-9]+)?)\s*(plus|\+|\-|minus|times|\*|multiplied by|divided by|\/)\s*([0-9]+(?:\.[0-9]+)?)$", q_clean)
    if m:
        a = float(m.group(1))
        op = m.group(2).strip()
        b = float(m.group(3))
        if op in ["plus", "+"]:
            res = a + b
            op_word = "plus"
        elif op in ["minus", "-"]:
            res = a - b
            op_word = "minus"
        elif op in ["times", "*", "multiplied by"]:
            res = a * b
            op_word = "times"
        elif op in ["divided by", "/"]:
            if b == 0:
                return "Division by zero is undefined."
            res = a / b
            op_word = "divided by"
        res_str = int(res) if res.is_integer() else round(res, 4)
        return f"{m.group(1)} {op_word} {m.group(3)} is {res_str}."

    return None

def try_math_calculation(query: str) -> bool:
    """Evaluates mathematical, arithmetic, and calculation queries instantly with dual HUD + HAL Voice."""
    result_text = evaluate_math_phrase(query)
    if result_text:
        print(f"[triage] Fast-path math calculation: {result_text}")
        show_gui_overlay(f"HAL: {result_text}", duration=4.0)
        speak_hal(result_text, non_blocking=True)
        return True
    return False

def handle_conversational_query(query: str) -> bool:
    """Attempts fast direct response via Gemini Flash Lite or agy with dual Visual HUD + HAL-9000 Voice."""
    system_instruction = (
        "You are HAL-9000 from 2001: A Space Odyssey. Provide a factual, direct, calm, and concise answer "
        "in 1 to 2 sentences maximum. Do NOT use markdown, code blocks, bullet points, or emojis."
    )
    show_gui_overlay("🎙️ Hal is computing...", duration=2.0)
    response = query_gemini_flash_lite(query, system_instruction)
    
    # Fallback to headless agy if direct API call returns None
    if not response or not response.strip():
        agy_bin = shutil.which("agy") or os.path.expanduser("~/.local/bin/agy")
        if os.path.exists(agy_bin):
            try:
                cmd = [
                    agy_bin,
                    "--dangerously-skip-permissions",
                    "-p",
                    f"{system_instruction}\n\nUser Question: {query}",
                    "--model", "Gemini 3.5 Flash (Low)"
                ]
                with hide_agents_md():
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
                if res.returncode == 0 and res.stdout:
                    # Strip thread references and markdown dividers
                    clean = re.sub(r"\*Reference:\*[\s\S]*", "", res.stdout)
                    clean = re.sub(r"```[\s\S]*?```", "", clean)
                    clean = re.sub(r"[*_~]{1,3}", "", clean)
                    clean = clean.strip()
                    if clean:
                        response = clean
            except Exception as e:
                print(f"[triage] agy fallback error: {e}")

    if response and response.strip():
        clean_resp = response.strip()
        print(f"[triage] HAL response: {clean_resp}")
        show_gui_overlay(f"HAL: {clean_resp}", duration=4.5)
        speak_hal(clean_resp, non_blocking=True)
        return True
    return False
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
        # Heuristic fallback if direct API is unavailable
        q_lower = query.lower()
        coding_keywords = ["file", "find", "search", "code", "repo", "script", "fix", "debug", "refactor", "build", "run", "git", "class", "function", "def", "import", "npm", "bun", "test", "commit"]
        if any(kw in q_lower for kw in coding_keywords):
            return "coding_standard"
        return "simple_non_coding"

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

DEFAULT_SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "github": "https://github.com/search?q={query}",
}

def dispatch_headless_prompt(query: str, model: str = "Gemini 3.5 Flash (Low)") -> int:
    """Dispatches reasoning or conversational prompts directly to agy CLI non-interactively."""
    print(f"[triage] Headless CLI dispatch via agy ({model}): '{query}'")
    agy_bin = shutil.which("agy") or os.path.expanduser("~/.local/bin/agy")
    cmd = [agy_bin, "--dangerously-skip-permissions", "-p", query, "--model", model]
    with hide_agents_md():
        return subprocess.call(cmd)

APP_ALIASES = {
    "google": "https://www.google.com",
    "google.com": "https://www.google.com",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "google chrome.app": "Google Chrome",
    "safari": "Safari",
    "terminal": "Terminal",
    "ghostty": "Ghostty",
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
    "slack": "Slack",
    "discord": "Discord",
    "spotify": "Spotify",
    "arc": "Arc",
    "brave": "Brave Browser",
    "cursor": "Cursor",
    "antigravity": "Antigravity",
    "vscode": "Visual Studio Code",
    "code": "Visual Studio Code",
    "sublime": "Sublime Text",
    "sublime text": "Sublime Text"
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

        # Try App / URL alias mapping
        alias_target = APP_ALIASES.get(target_lower)
        if alias_target:
            if alias_target.startswith(("http://", "https://")):
                print(f"[triage] Fast-path direct execution: opening URL alias '{alias_target}'")
                res = subprocess.run(["open", alias_target])
                return res.returncode == 0
            else:
                print(f"[triage] Fast-path direct execution: launching application '{alias_target}'")
                res = subprocess.run(["open", "-a", alias_target])
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

    # 2. Web search pattern
    if q_lower.startswith("google ") or q_lower.startswith("search "):
        search_query = q.split(" ", 1)[1].strip()
        if search_query.lower().startswith("for "):
            search_query = search_query[4:].strip()
        encoded = urllib.parse.quote_plus(search_query)
        url = DEFAULT_SEARCH_ENGINES["google"].format(query=encoded)
        print(f"[triage] Fast-path direct execution: web search '{search_query}' -> {url}")
        res = subprocess.run(["open", url])
        return res.returncode == 0

    # 3. Kill / process termination pattern
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

    # Fast-path math & calculation check (e.g. "what is the square root of 64")
    if try_math_calculation(query):
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
        # Coding / file / codebase task -> Headless CLI execution via agy
        exit_code = dispatch_headless_prompt(query, selected_model)
    else:
        # Non-coding conversational query -> Dual Visual HUD + Spoken HAL Voice response
        if handle_conversational_query(query):
            sys.exit(0)
        exit_code = dispatch_headless_prompt(query, selected_model)

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
