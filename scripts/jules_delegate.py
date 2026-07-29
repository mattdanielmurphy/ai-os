#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import subprocess
import base64

BASE_URL = "https://jules.googleapis.com/v1alpha"

def get_keychain_token():
    try:
        raw = subprocess.check_output('security find-generic-password -s "jules-cli" -w', shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if raw.startswith("go-keyring-base64:"):
            raw = raw[len("go-keyring-base64:"):]
        data = json.loads(base64.b64decode(raw).decode())
        return data.get("access_token")
    except Exception:
        return None

def get_auth_headers(key_index=0):
    env_keys = []
    k1 = os.environ.get("JULES_API_KEY")
    if not k1:
        f1 = os.path.expanduser("~/.jules/api_key")
        if os.path.exists(f1):
            with open(f1) as f:
                k1 = f.read().strip()
    if k1:
        env_keys.append(("JULES_API_KEY", k1, "api_key"))

    k2 = os.environ.get("JULES_API_KEY_ALT")
    if not k2:
        f2 = os.path.expanduser("~/.jules/api_key_alt")
        if os.path.exists(f2):
            with open(f2) as f:
                k2 = f.read().strip()
    if k2:
        env_keys.append(("JULES_API_KEY_ALT", k2, "api_key"))

    keychain_token = get_keychain_token()
    if keychain_token:
        env_keys.append(("macOS Keychain OAuth Token", keychain_token, "oauth"))

    if not env_keys:
        print("Error: No Jules credentials (JULES_API_KEY, JULES_API_KEY_ALT, or Keychain OAuth token) found.", file=sys.stderr)
        sys.exit(1)

    if key_index >= len(env_keys):
        return None, None, None

    name, val, mode = env_keys[key_index]
    if mode == "oauth":
        headers = {"Authorization": f"Bearer {val}", "Content-Type": "application/json"}
    else:
        headers = {"x-goog-api-key": val, "Content-Type": "application/json"}
    
    return name, headers, key_index

def make_request(endpoint, data=None, method="GET", key_index=0):
    name, headers, curr_idx = get_auth_headers(key_index)
    if headers is None:
        print("Error: All configured Jules authentication credentials failed.", file=sys.stderr)
        sys.exit(1)

    url = f"{BASE_URL}/{endpoint}"
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        # Try next credential if available
        next_name, next_headers, _ = get_auth_headers(curr_idx + 1)
        if next_headers is not None:
            print(f"[*] Credential '{name}' returned HTTP {e.code}. Failing over to '{next_name}'...", file=sys.stderr)
            return make_request(endpoint, data=data, method=method, key_index=curr_idx + 1)

        print(f"API Error ({name}): {e.code} - {e.reason}\n{error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request Exception ({name}): {e}", file=sys.stderr)
        sys.exit(1)

def cmd_create(args):
    repo = args.repo.strip()
    if not repo.startswith("sources/"):
        if "/" not in repo:
            print("Error: --repo should be in format 'owner/repo'", file=sys.stderr)
            sys.exit(1)
        if not repo.startswith("github/"):
            repo = f"github/{repo}"
        repo = f"sources/{repo}"

    payload = {
        "prompt": args.prompt,
        "sourceContext": {
            "source": repo,
            "githubRepoContext": {
                "startingBranch": args.branch
            }
        }
    }
    if args.auto_pr:
        payload["automationMode"] = "AUTO_CREATE_PR"

    res = make_request("sessions", data=payload, method="POST")
    print(json.dumps(res, indent=2))

def cmd_list(args):
    res = make_request("sessions")
    print(json.dumps(res, indent=2))

def cmd_get(args):
    session_id = args.session.strip()
    if not session_id.startswith("sessions/"):
        session_id = f"sessions/{session_id}"
    res = make_request(session_id)
    print(json.dumps(res, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Google Jules Multi-Account Delegation Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_create = subparsers.add_parser("create", help="Create a new Jules session")
    p_create.add_argument("--repo", required=True, help="Target GitHub repo (e.g. mattdanielmurphy/gitl-emails)")
    p_create.add_argument("--prompt", required=True, help="Task prompt for Jules")
    p_create.add_argument("--branch", default="main", help="Starting branch (default: main)")
    p_create.add_argument("--no-auto-pr", dest="auto_pr", action="store_false", default=True, help="Disable auto PR creation")

    p_list = subparsers.add_parser("list", help="List active Jules sessions")

    p_get = subparsers.add_parser("get", help="Get details of a specific session")
    p_get.add_argument("--session", required=True, help="Session ID or resource name")

    args = parser.parse_args()
    if args.command == "create":
        cmd_create(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)

if __name__ == "__main__":
    main()
