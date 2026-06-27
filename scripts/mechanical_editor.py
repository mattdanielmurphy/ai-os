#!/usr/bin/env python3
import os
import sys
import argparse
import json
import urllib.request
import urllib.error
import subprocess
import re
from pathlib import Path

def call_litellm(prompt, response_format=None):
    url = "http://localhost:4000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    if response_format:
        data["response_format"] = response_format

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            return res_json["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        print(f"Error connecting to LiteLLM proxy: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing API response: {e}", file=sys.stderr)
        sys.exit(1)

def apply_patch(filepath, patch_content):
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)
    patch_file = tmp_dir / "temp_patch.patch"
    
    with open(patch_file, "w", encoding="utf-8") as f:
        f.write(patch_content)
        
    try:
        # Run patch command: patch -u filepath -i patch_file
        result = subprocess.run(
            ["patch", "-u", str(filepath), "-i", str(patch_file), "--no-backup-if-mismatch"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr + "\n" + result.stdout
    except Exception as e:
        return False, str(e)
    finally:
        if patch_file.exists():
            patch_file.unlink()

def apply_substitutions(filepath, substitutions):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        for idx, sub in enumerate(substitutions):
            search = sub.get("search_string")
            replace = sub.get("replace_string")
            if search is None or replace is None:
                return False, f"Substitution at index {idx} is missing search_string or replace_string"
            if search not in content:
                return False, f"Search string not found in file:\n{search}"
            content = content.replace(search, replace)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "Substitutions applied successfully."
    except Exception as e:
        return False, f"Failed to apply substitutions: {e}"

def main():
    parser = argparse.ArgumentParser(description="Mechanical Editor utilizing local LiteLLM proxy")
    parser.add_argument("filepath", help="Path to the file to modify")
    parser.add_argument("spec", help="Technical spec describing the modifications")
    args = parser.parse_args()
    
    filepath = Path(args.filepath).resolve()
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8") as f:
        file_content = f.read()
        
    # Phase 1: Try unified patch
    prompt = f"""You are a precise coding tool. You must edit the file at path: {filepath}
Here is the current content of the file:
--- START OF FILE ---
{file_content}
--- END OF FILE ---

Apply the following technical spec to modify the file:
{args.spec}

OUTPUT INSTRUCTIONS:
- You must output ONLY a valid unified `.patch` format to perform these modifications.
- Do not include explanation, preamble, or any conversational text.
- Wrap the patch block in ```diff code block.
"""

    print("Requesting unified patch from DeepSeek via LiteLLM...")
    response = call_litellm(prompt)
    
    # Extract the patch block
    patch_match = re.search(r'```(?:diff|patch)?\n(.*?)\n```', response, re.DOTALL | re.IGNORECASE)
    if patch_match:
        patch_content = patch_match.group(1)
    else:
        # Fallback if block is not wrapped but starts with patch markers
        patch_lines = []
        started = False
        for line in response.splitlines():
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                started = True
            if started:
                patch_lines.append(line)
        patch_content = "\n".join(patch_lines) if patch_lines else response

    success, msg = apply_patch(filepath, patch_content)
    if success:
        print("Success: Patch applied successfully via Unix patch command.")
        print(msg)
        sys.exit(0)
        
    print("Patch application failed. Retrying with JSON search/replace fallback...")
    print(f"Patch error details:\n{msg}\n")
    
    # Phase 2 Fallback: JSON search & replace
    fallback_prompt = f"""You are a precise coding tool. Your previous patch failed to apply.
You must now provide exact search-and-replace block substitutions to modify the file at path: {filepath}
Here is the current content of the file:
--- START OF FILE ---
{file_content}
--- END OF FILE ---

Apply the following technical spec:
{args.spec}

OUTPUT INSTRUCTIONS:
- You must return a strict JSON object with a single top-level key "substitutions".
- "substitutions" must be a list of objects, each containing "search_string" and "replace_string" keys.
- Each "search_string" must match exactly a contiguous block of text in the original file (including whitespace).
- Each "replace_string" must contain the new text to replace that exact block of text.
- Do not return markdown headers or any other conversational text. Return ONLY the JSON object.

Example JSON output format:
{{
  "substitutions": [
    {{
      "search_string": "def old_func():\\n    pass",
      "replace_string": "def old_func():\\n    return True"
    }}
  ]
}}
"""
    
    fallback_response = call_litellm(fallback_prompt, response_format={"type": "json_object"})
    try:
        # Parse JSON
        json_str = fallback_response.strip()
        if json_str.startswith("```"):
            json_str = re.sub(r'^```json\s*', '', json_str, flags=re.IGNORECASE)
            json_str = re.sub(r'\s*```$', '', json_str)
            
        data = json.loads(json_str)
        substitutions = data.get("substitutions", [])
        if not substitutions:
            print("Error: JSON response from model did not contain 'substitutions' list.", file=sys.stderr)
            sys.exit(1)
            
        fallback_success, fallback_msg = apply_substitutions(filepath, substitutions)
        if fallback_success:
            print("Success: Modifications applied successfully via fallback JSON search-and-replace.")
            sys.exit(0)
        else:
            print(f"Error: Fallback search-and-replace failed:\n{fallback_msg}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error processing fallback response: {e}\nRaw Response:\n{fallback_response}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
