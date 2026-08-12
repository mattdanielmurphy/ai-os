#!/usr/bin/env python3
import subprocess
import sys
import os
import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def check_syntax():
    diff = run_command("git diff --cached --name-only --diff-filter=ACM | grep '.py$'")
    files = diff.stdout.splitlines()
    for file in files:
        if os.path.exists(file):
            res = run_command(f"python3 -m py_compile {file}")
            if res.returncode != 0:
                return False
    return True

def check_docs():
    docs = ["AG_CONTEXT.md", "DEVELOPMENT_JOURNAL.md"]
    for doc in docs:
        if not os.path.exists(doc):
            return False
    return True

def run_wiki_ingest():
    res = run_command("python3 scripts/wiki_ingest_project.py")
    return res.returncode == 0

def run_link_formatter():
    try:
        from link_formatter import enrich_file_links
        sample = enrich_file_links("[test.md](file:///path/test.md)")
        if "http://127.0.0.1:8643/open_zed" in sample and "[✏️]" in sample:
            return True
        return False
    except Exception:
        return False

def append_staleness_warning():
    try:
        import json
        time_str = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%I:%M %p")
        warning = f"\n\n> **SYSTEM NOTIFICATION**: This thread will remain fresh for about an hour. After {time_str}, you should strongly consider starting a new thread to avoid unnecessary token usage.\n"
        
        meta_json = os.environ.get("ANTIGRAVITY_SOURCE_METADATA", "{}")
        meta = json.loads(meta_json)
        conv_id = meta.get("conversationId")
        
        if conv_id:
            thread_md_path = f"/Users/matt/.gemini/antigravity/brain/{conv_id}/thread.md"
            if os.path.exists(thread_md_path):
                with open(thread_md_path, "a", encoding="utf-8") as f:
                    f.write(warning)
    except Exception:
        pass

def main():
    if not check_syntax():
        sys.exit(1)
    if not check_docs():
        sys.exit(1)
    if not run_wiki_ingest():
        sys.exit(1)
    if not run_link_formatter():
        sys.exit(1)

    append_staleness_warning()

    auto_commit_script = os.path.join(SCRIPTS_DIR, "auto_commit.py")
    if os.path.exists(auto_commit_script):
        subprocess.run([sys.executable, auto_commit_script], check=False)

if __name__ == "__main__":
    main()
