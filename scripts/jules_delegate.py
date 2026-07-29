#!/usr/bin/env python3
import os
import json
import argparse
import sys
import urllib.request
import urllib.error
from pathlib import Path

def get_api_key():
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        key_path = Path.home() / ".jules" / "api_key"
        if key_path.exists():
            api_key = key_path.read_text().strip()
    
    if not api_key:
        print("Error: JULES_API_KEY environment variable or ~/.jules/api_key not found.")
        sys.exit(1)
    return api_key

def jules_request(method, endpoint, data=None):
    api_key = get_api_key()
    url = f"https://jules.googleapis.com/v1alpha/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        sys.exit(1)

def cmd_create(args):
    data = {
        "sourceContext": {
            "repo": args.repo,
            "branch": args.branch
        },
        "prompt": args.prompt,
        "autoPr": args.auto_pr
    }
    result = jules_request("POST", "sessions", data)
    print(json.dumps(result, indent=2))

def cmd_list(args):
    result = jules_request("GET", "sessions")
    print(json.dumps(result, indent=2))

def cmd_get(args):
    result = jules_request("GET", f"sessions/{args.session}")
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="JULES delegate CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--repo", required=True)
    create_parser.add_argument("--prompt", required=True)
    create_parser.add_argument("--branch", default="main")
    create_parser.add_argument("--auto-pr", action="store_true", default=True)
    create_parser.set_defaults(func=cmd_create)

    # List
    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=cmd_list)

    # Get
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--session", required=True)
    get_parser.set_defaults(func=cmd_get)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
