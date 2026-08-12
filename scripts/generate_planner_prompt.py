#!/usr/bin/env python3
import sys
import os
import subprocess
import re
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate planner context using repomix")
    parser.add_argument("request", help="User request string")
    parser.add_argument("--include", help="Comma separated glob patterns to include", default="")
    
    # If no arguments provided, print help and exit
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    user_request = args.request
    
    os.makedirs("./tmp", exist_ok=True)
    
    print("Bundling codebase with repomix...")
    
    ignore_patterns = [
        # Version Control & Dependencies
        "**/.git/**", "**/.svn/**", "**/node_modules/**", "**/vendor/**", "**/packages/**", "**/bower_components/**", "**/Pods/**", "**/.cargo/registry/**", 
        
        # Build, Caches, & Outputs
        "**/build/**", "**/dist/**", "**/out/**", "**/target/**", "**/bin/**", "**/obj/**",
        "**/.next/**", "**/.nuxt/**", "**/.svelte-kit/**", "**/.angular/**", "**/.cache/**", "**/.webpack/**", "**/.vite/**", "**/.gradle/**", "**/.serverless/**", "**/.terraform/**",
        "**/__pycache__/**", "**/.pytest_cache/**", "**/.mypy_cache/**", "**/.ruff_cache/**", "**/.venv/**", "**/venv/**", "**/env/**", "**/.eggs/**", "**/*.egg-info/**", 
        
        # IDE & OS
        "**/.idea/**", "**/.vscode/**", "**/.fleet/**", "**/.DS_Store", "**/Thumbs.db",
        
        # Secrets & Environment
        "**/.env", "**/.env.*", "**/*.pem", "**/*.key", "**/*.cert", "**/*.crt", "**/*.p12", "**/secrets.json", "**/credentials.json", "**/*.htpasswd", "**/id_rsa*", "**/id_ed25519*",
        
        # Lockfiles
        "**/*.lock", "**/*-lock.json", "**/pnpm-lock.yaml", "**/bun.lockb", "**/Cargo.lock", "**/poetry.lock", "**/Gemfile.lock", "**/go.sum",
        
        # Coverage, Logs & Temp
        "**/coverage/**", "**/.nyc_output/**", "**/logs/**", "**/*.log", "**/*.trace", "**/tmp/**", "**/temp/**"
    ]
    ignore_str = ",".join(ignore_patterns)

    # run repomix
    cmd = ["bunx", "repomix", "-o", "./tmp/context.md", "--style", "markdown", "--ignore", ignore_str]
    if args.include:
        cmd.extend(["--include", args.include])

    try:
        result = subprocess.run(
            cmd, 
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running repomix: {e}")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
        
    # write planner prompt
    with open("./tmp/planner_prompt.txt", "w") as f:
        f.write(user_request)
        
    token_match = re.search(r"Total Tokens:\s*([\d,]+)\s*tokens", result.stdout, re.IGNORECASE)
    if token_match:
        token_str = token_match.group(1).replace(",", "")
        total_tokens = int(token_str)
        if total_tokens > 100000:
            print(f"\n❌ ERROR: Context size is far too large ({total_tokens:,} tokens).")
            print("ACTION REQUIRED:")
            print("1. You MUST NOT attach this massive context.md file yet.")
            print("2. You MUST use your tools (like grep_search, view_file, etc.) to figure out which specific directories or files are actually relevant to the task.")
            print("3. Re-run this script with the --include flag to narrow down the scope. Example:")
            print("   python3 ~/projects/ai-os/scripts/generate_planner_prompt.py \"<request>\" --include \"src/api/**,docs/**\"")
            print("4. Keep re-running and refining until the context size is under 100,000 tokens.")
            print("5. CRITICAL RULE: If you cannot successfully call proxima:ask_perplexity with a reasonable context size, you MUST STOP and explicitly tell the user. You are STRICTLY FORBIDDEN from thinking for yourself or attempting to do the planning work locally.")
            return

    print("\n✅ Context size is reasonable.")
    print("ACTION REQUIRED: invoke proxima:ask_perplexity using the contents of ./tmp/planner_prompt.txt and attach ./tmp/context.md via the files parameter.")
    print("CRITICAL RULE: If proxima:ask_perplexity fails for any reason, you MUST STOP and inform the user. You are STRICTLY FORBIDDEN from attempting to plan or execute the work yourself.")

if __name__ == "__main__":
    main()
