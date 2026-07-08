#!/usr/bin/env python3
import json
import os
import sys
import datetime
import urllib.request
import urllib.parse
from pathlib import Path

OPENROUTER_KEY = "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"

def get_access_token():
    TOKEN_PATH = Path.home() / ".gemini" / "antigravity-cli" / "antigravity-oauth-token"
    CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
    CLIENT_SECRET = "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"
    if not TOKEN_PATH.exists():
        return None
    try:
        token_data = json.loads(TOKEN_PATH.read_text())
    except Exception:
        return None

    token_info = token_data.get("token", {})
    refresh_token_val = token_info.get("refresh_token")
    access_token = token_info.get("access_token")
    expiry_str = token_info.get("expiry")

    if not refresh_token_val:
        return None

    is_expired = True
    if expiry_str:
        try:
            expiry = datetime.datetime.fromisoformat(expiry_str)
            now = datetime.datetime.now(datetime.timezone.utc) if expiry.tzinfo else datetime.datetime.now()
            if expiry > now + datetime.timedelta(seconds=60):
                is_expired = False
        except Exception:
            pass

    if is_expired or not access_token:
        url = "https://oauth2.googleapis.com/token"
        req_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token_val,
            "grant_type": "refresh_token"
        }
        encoded_data = urllib.parse.urlencode(req_data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, method="POST")
        try:
            with urllib.request.urlopen(req) as res:
                resp_data = json.loads(res.read().decode())
                access_token = resp_data.get("access_token")
                expires_in = resp_data.get("expires_in", 3600)
                if access_token:
                    token_info["access_token"] = access_token
                    new_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
                    token_info["expiry"] = new_expiry.isoformat()
                    token_data["token"] = token_info
                    TOKEN_PATH.write_text(json.dumps(token_data, indent=2))
        except Exception:
            pass

    return access_token

def call_gemini_api(prompt, response):
    token = get_access_token()
    if not token:
        return None
    
    url = "https://daily-cloudcode-pa.googleapis.com/v1internal:generateContent"
    instruction = (
        "Generate a 2-5 word title summarizing the user prompt and agent response below. "
        "Do NOT use markdown, quotes, formatting, or generic prefixes like 'Continuing conversation'. "
        "Respond ONLY with the 2-5 word title itself."
    )
    user_content = f"User prompt:\n{prompt}\n\nAgent response:\n{response}"
    
    payload = {
        "project": "atlas-calculator",
        "model": "gemini-2.5-flash",
        "request": {
            "contents": [{
                "parts": [{"text": f"{instruction}\n\n{user_content}"}]
            }]
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
        with urllib.request.urlopen(req, timeout=5) as res:
            resp = json.loads(res.read().decode())
            text = resp["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text
    except Exception:
        return None

def call_openrouter_api(prompt, response):
    url = "https://openrouter.ai/api/v1/chat/completions"
    instruction = (
        "Generate a 2-5 word title summarizing the user prompt and agent response below. "
        "Do NOT use markdown, quotes, formatting, or generic prefixes like 'Continuing conversation'. "
        "Respond ONLY with the 2-5 word title itself."
    )
    user_content = f"User prompt:\n{prompt}\n\nAgent response:\n{response}"
    
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": f"{instruction}\n\n{user_content}"}
        ]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            resp = json.loads(res.read().decode())
            text = resp["choices"][0]["message"]["content"].strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
            if text.startswith("'") and text.endswith("'"):
                text = text[1:-1].strip()
            return text
    except Exception:
        return None

def generate_title(prompt, response):
    # Try Google Cloud Code API first
    title = call_gemini_api(prompt, response)
    if title:
        return title
    # Fallback to OpenRouter
    return call_openrouter_api(prompt, response)

def main():
    if len(sys.argv) < 3:
        print("Usage: generate_title.py <prompt> <response>")
        sys.exit(1)
        
    prompt = sys.argv[1]
    response = sys.argv[2]
    
    title = generate_title(prompt, response)
    if title:
        print(title)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
