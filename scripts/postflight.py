#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def check_syntax():
    print("Checking syntax of modified Python files...")
    diff = run_command("git diff --cached --name-only --diff-filter=ACM | grep '.py$'")
    files = diff.stdout.splitlines()
    for file in files:
        if os.path.exists(file):
            print(f"Compiling {file}...")
            res = run_command(f"python3 -m py_compile {file}")
            if res.returncode != 0:
                print(f"Syntax error in {file}:\n{res.stderr}")
                return False
    return True

def check_docs():
    print("Verifying documentation...")
    docs = ["AG_CONTEXT.md", "DEVELOPMENT_JOURNAL.md"]
    for doc in docs:
        if not os.path.exists(doc):
            print(f"Missing {doc}!")
            return False
    return True

def run_wiki_ingest():
    print("Executing wiki ingest...")
    res = run_command("python3 scripts/wiki_ingest_project.py")
    if res.returncode != 0:
        print(f"Wiki ingestion failed:\n{res.stderr}")
        return False
    return True

def main():
    if not check_syntax():
        print("Syntax check failed. Fix errors before proceeding.")
        sys.exit(1)
    
    if not check_docs():
        print("Documentation check failed.")
        sys.exit(1)

    if not run_wiki_ingest():
        print("Wiki ingestion failed.")
        sys.exit(1)

    print("Post-flight checks passed.")

if __name__ == "__main__":
    main()
