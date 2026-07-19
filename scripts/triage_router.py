#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.parse
import subprocess
import time
from pathlib import Path

# Config and settings paths
SETTING_PATH = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
OAUTH_CREDS_PATH = Path.home() / ".gemini" / "oauth_creds.json"
TELEMETRY_DB_PATH = Path.home() / ".ai-os-telemetry.json"
ERROR_LOG_PATH = Path("/tmp/aios_last_cmd.log")

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
    query = ""
    # Look for query inside arguments
    for arg in args:
        if not arg.startswith("-"):
            query = arg
            break
            
    # Default behavior for interactive shell
    if not query:
        model = model_override or "Gemini 3.5 Flash (Low)"
        print(f"[triage] Interactive mode or empty prompt: launching agy with {model}")
        cmd = ["agy"] + args
        if not has_model:
            cmd += ["--model", model]
        sys.exit(subprocess.call(cmd))

    # Bypassing classification if model override is provided
    if has_model:
        model = model_override
        print(f"[triage] Model override provided: running {model}")
        cmd = ["agy"] + args
        sys.exit(subprocess.call(cmd))

    # 3. Tier 1 Classification
    print(f"[triage] Intercepting prompt: '{query[:50]}...'")
    category = tier1_triage(query)
    print(f"[triage] Classified category: {category}")

    # 4. Route selection
    selected_model = "Gemini 3.5 Flash (Low)"
    
    if category == "simple_non_coding":
        # DeepSeek V4 Flash is not locally configured in agy, fall back to cheap Gemini 3.5 Flash (Low)
        selected_model = "Gemini 3.5 Flash (Low)"
    elif category == "coding_standard":
        # Quota checks for conservation
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

    # 5. Run the chosen model
    print(f"[triage] Selected model: {selected_model}")
    cmd = ["agy"]
    # Rebuild arguments injecting chosen model
    cmd += ["--model", selected_model]
    for arg in args:
        # Skip original --model if user passed a default somehow
        if arg == "--model":
            continue
        cmd.append(arg)

    exit_code = subprocess.call(cmd)

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
        sys.exit(subprocess.call(cmd_escalated))

    sys.exit(0)

if __name__ == "__main__":
    main()
