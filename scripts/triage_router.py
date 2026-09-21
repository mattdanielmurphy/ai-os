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
                    "--model", "Gemini 3.7 Flash (Low)"
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

SNAPSHOT_PATH = Path.home() / ".ag_quota_snapshot.json"

def check_quota(timeout_sec: float = 2.0) -> dict:
    """
    Evaluates usable Antigravity quota and returns structured quota state:
    'healthy', 'low', 'exhausted', 'unavailable', or 'unknown'.
    """
    # 1. Primary: Run ag-quota -j (canonical local CLI)
    ag_quota_bin = shutil.which("ag-quota") or os.path.expanduser("~/go/bin/ag-quota")
    if os.path.exists(ag_quota_bin):
        try:
            res = subprocess.run([ag_quota_bin, "-j"], capture_output=True, text=True, timeout=timeout_sec)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                models = data.get("Models", [])
                if models:
                    flash_fractions = []
                    pro_fractions = []
                    all_exhausted = True
                    snapshot = {}
                    email = data.get("Email", "default")
                    
                    for m in models:
                        model_id = m.get("ModelID", "")
                        disp = m.get("DisplayName", model_id)
                        frac = m.get("RemainingFraction", 1.0)
                        is_ex = m.get("IsExhausted", False)
                        if isinstance(frac, (int, float)):
                            snapshot[f"{email} | {disp}"] = round(frac, 4)
                            if not is_ex and frac > 0:
                                all_exhausted = False
                            if "flash" in model_id.lower() or "flash" in disp.lower():
                                flash_fractions.append(frac)
                            elif "pro" in model_id.lower() or "pro" in disp.lower():
                                pro_fractions.append(frac)

                    # Update snapshot cache
                    try:
                        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
                            json.dump(snapshot, f, indent=2)
                    except Exception:
                        pass

                    if all_exhausted:
                        return {
                            "status": "exhausted",
                            "remaining_fraction": 0.0,
                            "primary_model": data.get("DefaultModelID", "gemini-flash"),
                            "details": "All quota buckets exhausted"
                        }
                    
                    rep_frac = max(flash_fractions) if flash_fractions else (max(pro_fractions) if pro_fractions else 1.0)
                    status = "healthy" if rep_frac >= 0.20 else "low"
                    return {
                        "status": status,
                        "remaining_fraction": rep_frac,
                        "primary_model": data.get("DefaultModelID", "gemini-3.7-flash"),
                        "details": f"{int(rep_frac * 100)}% remaining on primary model"
                    }
        except Exception:
            pass

    # 2. Secondary: Check recent snapshot cache (< 5 minutes old)
    if SNAPSHOT_PATH.exists():
        try:
            mtime = os.path.getmtime(SNAPSHOT_PATH)
            if time.time() - mtime < 300:
                with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
                    snapshot = json.load(f)
                vals = [v for v in snapshot.values() if isinstance(v, (int, float))]
                if vals:
                    max_val = max(vals)
                    if max_val == 0.0:
                        return {"status": "exhausted", "remaining_fraction": 0.0, "primary_model": "cached", "details": "Cached snapshot shows exhausted"}
                    status = "healthy" if max_val >= 0.20 else "low"
                    return {"status": status, "remaining_fraction": max_val, "primary_model": "cached", "details": f"Cached snapshot: {int(max_val * 100)}%"}
        except Exception:
            pass

    # 3. Tertiary: Google PA API fallback
    try:
        quota_5h, quota_week, is_real = get_quota()
        if is_real:
            min_frac = min(quota_5h, quota_week)
            if min_frac <= 0.0:
                return {"status": "exhausted", "remaining_fraction": 0.0, "primary_model": "pa-api", "details": "PA API shows exhausted"}
            status = "healthy" if min_frac >= 0.20 else "low"
            return {"status": status, "remaining_fraction": min_frac, "primary_model": "pa-api", "details": f"PA API: {int(min_frac * 100)}%"}
    except Exception:
        pass

    # 4. Unknown / Unavailable
    if not (shutil.which("ag-quota") or os.path.exists(os.path.expanduser("~/go/bin/ag-quota"))):
        return {"status": "unavailable", "remaining_fraction": None, "primary_model": "unknown", "details": "ag-quota binary unavailable"}
    return {"status": "unknown", "remaining_fraction": None, "primary_model": "unknown", "details": "Quota status could not be determined"}

def is_lightweight_request(query: str) -> tuple[bool, str]:
    """
    Identifies whether a request is obviously lightweight (best kept direct in ChatGPT).
    Returns (is_lightweight, reason).
    Deliberately low threshold: if complexity is uncertain, returns (False, '').
    """
    q_clean = query.strip()
    q_lower = q_clean.lower().rstrip(".!?;:")

    # 1. Greetings & casual conversation
    greetings = {
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "how are you doing", "how's it going", "hows it going",
        "what's up", "whats up", "yo", "sup", "thanks", "thank you", "bye", "goodbye",
        "hello there", "hi there", "hey there"
    }
    if q_lower in greetings or (q_lower.startswith(("hi ", "hello ", "hey ")) and len(q_lower.split()) <= 3 and not any(kw in q_lower for kw in ["code", "bug", "plan", "review", "repo", "file"])):
        return True, "greeting / casual conversation"

    # 2. Trivial math or calculation
    if evaluate_math_phrase(query) is not None:
        return True, "trivial calculation"

    # 3. Explicit user instruction not to delegate
    no_delegate_phrases = [
        "do not delegate", "don't delegate", "dont delegate",
        "no delegation", "stay in chatgpt", "handle directly in chatgpt",
        "handle directly", "answer directly", "chatgpt only"
    ]
    if any(p in q_lower for p in no_delegate_phrases):
        return True, "explicit user request not to delegate"

    # 4. Explicitly marked quick / simple
    quick_prefixes = ["quick question:", "simple question:", "just a quick question:", "just a quick:", "quick:"]
    for qp in quick_prefixes:
        if q_lower.startswith(qp):
            rest = q_clean[len(qp):].strip()
            if len(rest) < 120 and not any(kw in rest.lower() for kw in ["architecture", "review", "bug", "implement", "investigate", "compare", "system", "code"]):
                return True, "explicitly marked quick/simple"

    # 5. Very short rewrites, grammar corrections, or text formatting (< 150 chars)
    rewrite_prefixes = [
        "rewrite this sentence", "rewrite this", "fix the grammar in this",
        "fix grammar in this", "fix the grammar", "fix grammar",
        "fix typo", "fix the typo", "make this title shorter", "make this shorter",
        "format this as markdown", "format as markdown", "spellcheck this",
        "check spelling in this"
    ]
    for rp in rewrite_prefixes:
        if q_lower.startswith(rp) and len(q_clean) < 200:
            return True, "short text rewrite or formatting"

    # 6. Simple context-free brainstorming or quick list (< 100 chars)
    simple_brainstorm = [
        "give me three quick name ideas", "give me 3 quick name ideas",
        "give me three name ideas", "give me 3 name ideas",
        "quick name ideas", "name ideas for"
    ]
    for sb in simple_brainstorm:
        if q_lower.startswith(sb) and len(q_clean) < 120:
            return True, "simple context-free brainstorming"

    # 7. One-line factual questions with zero contextual dependency (< 60 chars)
    if len(q_clean) < 60 and not any(kw in q_lower for kw in [
        "project", "file", "repo", "code", "bug", "arch", "design", "plan",
        "rule", "memory", "wiki", "system", "review", "why", "how do i",
        "implement", "error", "trace", "test", "session"
    ]):
        if q_lower.startswith(("what is ", "what's ", "who is ", "who's ", "when was ", "where is ")) and len(q_clean.split()) <= 8:
            return True, "context-free factual query"

    return False, ""

def get_git_repo_root(cwd: Path | None = None) -> str | None:
    target = cwd or Path.cwd()
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(target),
            capture_output=True,
            text=True,
            timeout=1.5
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def detect_execution_mode(prompt: str) -> str:
    p_lower = prompt.lower()
    if any(k in p_lower for k in ["plan", "roadmap", "architecture", "design", "propose", "proposal"]):
        return "plan"
    if any(k in p_lower for k in ["review", "audit", "critique", "inspect"]):
        return "review"
    if any(k in p_lower for k in ["investigate", "why is", "why does", "diagnose", "root cause", "debug"]):
        return "investigate"
    if any(k in p_lower for k in ["implement", "build", "write code", "create", "refactor", "patch", "fix", "add"]):
        return "build"
    return "reason"

def build_thin_handoff(
    prompt: str,
    cwd: Path | str | None = None,
    mode: str | None = None,
    safety_boundary: str | None = None,
    extra_note: str | None = None
) -> str:
    """
    Constructs a thin handoff to agy per policy:
    - Original user request, preserved verbatim
    - Active project/repository and working directory
    - Minimal necessary execution metadata (mode / safety boundary)
    - Concise extra note only if critical context cannot be discovered by agy itself.
    """
    working_dir = Path(cwd).resolve() if cwd else Path.cwd().resolve()
    repo_root = get_git_repo_root(working_dir) or str(working_dir)
    selected_mode = mode or detect_execution_mode(prompt)

    lines = [
        f"Original user request: {prompt.strip()}",
        "",
        f"Active project/repository and working directory: {repo_root}",
        f"Working directory: {working_dir}",
        f"Mode: {selected_mode}"
    ]
    if safety_boundary:
        lines.append(f"Safety boundary: {safety_boundary}")
    if extra_note:
        lines.append(f"Note: {extra_note}")

    return "\n".join(lines)

def evaluate_routing(
    query: str,
    explicit_flags: list | None = None,
    cwd: Path | str | None = None,
    safety_boundary: str | None = None,
    extra_note: str | None = None,
    mock_quota_status: str | None = None,
    mock_quota_fraction: float | None = None
) -> dict:
    """
    Core routing evaluator for AI-OS harness.
    Determines whether to route to agy (default for non-trivial with healthy quota),
    direct ChatGPT, or other backends.
    """
    explicit_flags = explicit_flags or []
    q_lower = query.lower()
    
    # 1. Check Explicit Overrides
    forced_backend = None
    override_reason = None
    
    # Flag overrides
    if any(f in explicit_flags for f in ["--chatgpt", "--direct", "--no-delegate"]):
        forced_backend = "chatgpt"
        override_reason = "explicit CLI flag (--chatgpt/--direct)"
    elif any(f in explicit_flags for f in ["--agy", "--force-agy"]):
        forced_backend = "agy"
        override_reason = "explicit CLI flag (--agy)"
    elif any(f in explicit_flags for f in ["--claude"]):
        forced_backend = "claude"
        override_reason = "explicit CLI flag (--claude)"
    elif any(f in explicit_flags for f in ["--codex"]):
        forced_backend = "codex"
        override_reason = "explicit CLI flag (--codex)"
        
    # In-prompt overrides
    if not forced_backend:
        if query.startswith("/agy ") or re.search(r"\b(use agy|delegate to agy|run with agy|pass to agy|ask agy)\b", q_lower):
            forced_backend = "agy"
            override_reason = "explicit prompt instruction for agy"
        elif re.search(r"\b(do not delegate|don't delegate|handle directly in chatgpt|stay in chatgpt|chatgpt only)\b", q_lower):
            forced_backend = "chatgpt"
            override_reason = "explicit prompt instruction for direct ChatGPT"

    # Check quota
    if mock_quota_status:
        quota_status = mock_quota_status
        remaining_fraction = mock_quota_fraction if mock_quota_fraction is not None else (1.0 if mock_quota_status == "healthy" else 0.15)
        quota_info = {"status": quota_status, "remaining_fraction": remaining_fraction, "primary_model": "mock", "details": f"Mock quota: {quota_status}"}
    else:
        quota_info = check_quota()
        quota_status = quota_info.get("status", "unknown")
        remaining_fraction = quota_info.get("remaining_fraction")

    # 2. Decision Logic
    if forced_backend:
        backend = forced_backend
        selection_method = "explicit"
        fallback_occurred = False
        fallback_reason = None
        is_lw = False
        lw_reason = ""
    else:
        selection_method = "automatic"
        is_lw, lw_reason = is_lightweight_request(query)
        
        if is_lw:
            backend = "chatgpt"
            fallback_occurred = False
            fallback_reason = None
        else:
            # Substantive request!
            if quota_status == "healthy":
                backend = "agy"
                fallback_occurred = False
                fallback_reason = None
            elif quota_status == "low":
                backend = "chatgpt"
                fallback_occurred = True
                fallback_reason = "low quota"
            elif quota_status == "exhausted":
                backend = "chatgpt"
                fallback_occurred = True
                fallback_reason = "exhausted quota"
            elif quota_status == "unavailable":
                backend = "chatgpt"
                fallback_occurred = True
                fallback_reason = "unavailable quota"
            else:  # unknown
                backend = "chatgpt"
                fallback_occurred = True
                fallback_reason = "unknown quota"

    # Thin handoff construction
    thin_handoff = None
    if backend == "agy":
        clean_query = re.sub(r"^(?:/agy\s*|(?:use agy|delegate to agy|run with agy|pass to agy|ask agy)[:,\s]*)", "", query, flags=re.IGNORECASE).strip() or query
        thin_handoff = build_thin_handoff(
            prompt=clean_query,
            cwd=cwd,
            safety_boundary=safety_boundary,
            extra_note=extra_note
        )

    # Resolve model name for agy
    resolved_model = "Gemini 3.7 Flash (High)"
    if backend == "agy":
        if quota_status == "low":
            resolved_model = "Gemini 3.1 Pro (Low)"
        else:
            resolved_model = "Gemini 3.7 Flash (High)"

    return {
        "query": query,
        "backend": backend,
        "selection_method": selection_method,
        "override_reason": override_reason,
        "quota_status": quota_status,
        "remaining_fraction": remaining_fraction,
        "quota_details": quota_info.get("details", ""),
        "fallback_occurred": fallback_occurred,
        "fallback_reason": fallback_reason,
        "is_lightweight": is_lw,
        "lightweight_reason": lw_reason,
        "thin_handoff": thin_handoff,
        "model": resolved_model if backend == "agy" else "chatgpt-direct",
    }

def format_routing_visibility(decision: dict) -> str:
    backend = decision["backend"]
    method = decision["selection_method"]
    quota_st = decision["quota_status"]
    frac = decision["remaining_fraction"]
    frac_str = f" ({int(frac * 100)}% remaining)" if frac is not None else ""
    fallback = decision["fallback_occurred"]
    fb_reason = decision["fallback_reason"]

    lines = [
        "[ai-os routing]",
        f"  Backend: {backend}",
        f"  Selection: {method}" + (" (healthy quota available)" if backend == "agy" and method == "automatic" else f" ({decision['override_reason']})" if decision.get("override_reason") else ""),
        f"  Quota: {quota_st}{frac_str}",
        f"  Fallback: {'true (Reason: ' + fb_reason + ')' if fallback else 'false'}"
    ]
    return "\n".join(lines)

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

def dispatch_headless_prompt(query: str, model: str = "Gemini 3.7 Flash (Low)") -> int:
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
        model = model_override or "Gemini 3.7 Flash (Low)"
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

    # Core routing evaluation
    decision = evaluate_routing(query, explicit_flags=args, cwd=Path.cwd())

    # If --json requested, output JSON and exit
    if "--json" in args:
        print(json.dumps(decision, indent=2))
        sys.exit(0)

    # Print visible routing record
    print(format_routing_visibility(decision))

    # Route based on evaluated backend:
    if decision["backend"] == "agy":
        prompt_to_dispatch = decision["thin_handoff"] or query
        exit_code = dispatch_headless_prompt(prompt_to_dispatch, decision["model"])
        if exit_code != 0:
            print(f"\n[ai-os routing] agy invocation failed (exit code {exit_code}). Falling back cleanly to direct handling...")
            handle_conversational_query(query)
            sys.exit(0)
        sys.exit(exit_code)
    elif decision["backend"] == "claude":
        cmd = ["claude", query, "--dangerously-skip-permissions"]
        sys.exit(subprocess.call(cmd))
    elif decision["backend"] == "codex":
        cmd = ["codex", "exec", query]
        sys.exit(subprocess.call(cmd))
    else:
        # direct chatgpt / local handling
        if decision.get("fallback_occurred"):
            print(f"[ai-os routing] Direct fallback active: {decision.get('fallback_reason')}")
        if handle_conversational_query(query):
            sys.exit(0)
        print(f"\n[ai-os routing] Direct response completed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
