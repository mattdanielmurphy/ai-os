# services/lecture_mode/cli.py
import argparse
import asyncio
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import json

def cmd_mode(action: str):
    """Controls the Hammerspoon Lecture Mode enforcer directly."""
    if action == "on":
        subprocess.run(["hs", "-c", "require('modules.lecture_mode').activate()"])
        print("🎓 Hammerspoon Lecture Mode Engaged (Focus locked to Notes, Chrome & Files)")
    elif action == "off":
        subprocess.run(["hs", "-c", "require('modules.lecture_mode').requestExit()"])
        print("⏱️  Initiated 10-second exit delay in Hammerspoon...")
    elif action == "status":
        proc = subprocess.run(
            ["hs", "-c", "return require('modules.lecture_mode').isActive()"],
            capture_output=True,
            text=True,
        )
        is_active = "true" in proc.stdout.strip().lower()
        status_str = "ACTIVE 🔒" if is_active else "INACTIVE 🔓"
        print(f"Lecture Mode Status: {status_str}")

def cmd_slides(pdf_path: str):
    """Extracts text and academic terms of art from a slide deck."""
    from services.lecture_mode.slide_parser import extract_terms_of_art, extract_text_from_pdf
    path = Path(pdf_path).expanduser()
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"📄 Analyzing slide deck: {path.name}...")
    text = extract_text_from_pdf(path)
    terms = extract_terms_of_art(text)
    print(f"✅ Extracted {len(terms)} technical terms of art:")
    for t in terms:
        print(f"  • {t}")

def cmd_status():
    """Queries the local Lecture HUD server status."""
    try:
        req = urllib.request.Request("http://127.0.0.1:4141/api/status")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("is_running"):
                elapsed = int(data.get("elapsed_seconds", 0))
                m, s = divmod(elapsed, 60)
                print(f"🎓 Active Lecture: {data.get('course')}")
                print(f"⏱️  Elapsed: {m:02d}:{s:02d}")
                print(f"🎙️  Segments: {data.get('segment_count')}")
                print(f"🧠 Terms Primed: {len(data.get('terms_of_art', []))}")
                print(f"🌐 HUD: http://127.0.0.1:4141")
            else:
                print("Lecture Mode Server is idle (no active recording).")
    except Exception:
        print("Lecture Mode HUD server is not currently running.")

def cmd_hud():
    """Opens the Lecture HUD in Google Chrome Profile 3."""
    url = "http://127.0.0.1:4141"
    subprocess.run([
        "open", "-a", "Google Chrome", "--args",
        "--profile-directory=Profile 3", url
    ])
    print(f"🌐 Opened Lecture HUD: {url}")

def main():
    parser = argparse.ArgumentParser(
        description="AI-OS Lecture Focus Mode & Live Audio-Synced Rolling Transcript"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # mode command
    mode_parser = subparsers.add_parser("mode", help="Toggle or inspect Hammerspoon lecture lock")
    mode_parser.add_argument("action", choices=["on", "off", "status"], default="status", nargs="?")

    # slides command
    slides_parser = subparsers.add_parser("slides", help="Extract terms of art from a slide deck")
    slides_parser.add_argument("path", help="Path to slide PDF")

    # status command
    subparsers.add_parser("status", help="Check active lecture status")

    # hud command
    subparsers.add_parser("hud", help="Open the live transcript HUD in Chrome Profile 3")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Run the Lecture HUD server daemon")
    serve_parser.add_argument("--port", type=int, default=4141)

    args = parser.parse_args()

    if args.command == "mode":
        cmd_mode(args.action)
    elif args.command == "slides":
        cmd_slides(args.path)
    elif args.command == "status":
        cmd_status()
    elif args.command == "hud":
        cmd_hud()
    elif args.command == "serve":
        from services.lecture_mode.server import run_server
        run_server(port=args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
