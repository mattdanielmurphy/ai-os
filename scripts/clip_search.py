#!/usr/bin/env python3
import sys
import sqlite3
import os
import subprocess
import shutil
import re

ALFRED_DB_PATH = os.path.expanduser("~/Library/Application Support/Alfred/Databases/clipboard.alfdb")

def extract_urls(text):
    """Extract all web links from text using regex"""
    url_regex = re.compile(r'https?://[^\s\"\'\>]+')
    matches = url_regex.findall(text)
    return [m.rstrip('.,);]:') for m in matches]

def search_sqlite(query, limit=100):
    if not os.path.exists(ALFRED_DB_PATH):
        print(f"Error: Alfred DB not found at {ALFRED_DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(ALFRED_DB_PATH)
    cursor = conn.cursor()
    
    words = [w.strip().lower() for w in query.split() if len(w.strip()) > 1]
    url_keywords = ["link", "url", "http", "https", "website", "site", "referral"]
    url_focused = any(w in url_keywords for w in words)
    
    if url_focused:
        sql = """
            SELECT item, app, datetime(ts + 978307200, 'unixepoch', 'localtime') as created_at 
            FROM clipboard 
            WHERE item IS NOT NULL AND dataType = 0 AND (item LIKE '%http://%' OR item LIKE '%https://%')
            ORDER BY ts DESC 
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
    else:
        sql = """
            SELECT item, app, datetime(ts + 978307200, 'unixepoch', 'localtime') as created_at 
            FROM clipboard 
            WHERE item IS NOT NULL AND dataType = 0 
            ORDER BY ts DESC 
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        
    rows = cursor.fetchall()
    conn.close()
    
    candidates = []
    seen = set()
    idx = 1
    for item, app, created_at in rows:
        item_str = item.strip()
        if not item_str or item_str in seen:
            continue
        seen.add(item_str)
        
        # If url focused, extract the exact URL line for display
        urls = extract_urls(item_str)
        if url_focused and urls:
            matched_line = urls[0]
        else:
            lines = [l.strip() for l in item_str.splitlines() if l.strip()]
            matched_line = lines[0] if lines else item_str
            
        display = f"[{idx}] ({app or 'Unknown'} | {created_at}) - {matched_line[:120]}"
        candidates.append((item_str, display))
        idx += 1
        
    return candidates

def ask_llm(query, candidate_tuples, model="flash"):
    formatted_list = []
    for idx, (full_text, display) in enumerate(candidate_tuples[:35], 1):
        urls = extract_urls(full_text)
        if urls:
            snippet_desc = f"URLs found: {', '.join(urls[:3])} | Text context: {full_text[:120].replace('\n', ' ')}"
        else:
            snippet_desc = full_text[:150].replace('\n', ' ')
        formatted_list.append(f"[{idx}] {snippet_desc}")
        
    prompt = f"""Search Query: "{query}"

Clipboard Candidates:
--------------------------------------------------
{"\n".join(formatted_list)}
--------------------------------------------------

INSTRUCTIONS:
1. Find the top matching candidate indices (e.g. [3], [12]).
2. If the user asks for a link, URL, or referral link, ONLY match candidates with valid URLs.
3. Output format: INDEX | MATCHED_URL_OR_SNIPPET | REASON
If NO candidates match, output 'NONE'.
"""
    
    target_model = "gemini/gemini-2.5-pro" if model == "pro" else "gemini/gemini-2.5-flash"
    try:
        res = subprocess.run(["litellm", "--model", target_model, "-p", prompt], capture_output=True, text=True, timeout=15)
        return res.stdout.strip()
    except Exception:
        return "NONE"

def run_fzf_selector(candidate_tuples):
    fzf_input = []
    text_map = {}
    for idx, (full_text, display) in enumerate(candidate_tuples, 1):
        clean_display = display.replace("\n", " ")
        fzf_input.append(clean_display)
        text_map[clean_display] = full_text
        
    try:
        fzf_proc = subprocess.Popen(["fzf", "--prompt=Select Clipboard Item > ", "--header=Press ENTER to copy selection to clipboard"], 
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = fzf_proc.communicate(input="\n".join(fzf_input))
        
        selected_line = out.strip()
        if selected_line in text_map:
            matched_text = text_map[selected_line]
            pb = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            pb.communicate(input=matched_text)
            print(f"\n✓ Copied to clipboard:\n{matched_text}")
        else:
            print("\nNo item selected.")
    except Exception as e:
        print(f"Interactive mode error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: search-clipboard '<query>' [--pro]")
        sys.exit(1)
        
    use_pro = "--pro" in sys.argv
    query_args = [arg for arg in sys.argv[1:] if arg != "--pro"]
    query = " ".join(query_args)
    
    candidates = search_sqlite(query)
    
    if not candidates:
        print("No items found in clipboard DB.")
        return

    llm_output = ask_llm(query, candidates, model="pro" if use_pro else "flash")
    
    if "NONE" in llm_output or not llm_output:
        if not use_pro:
            print("⚡ Flash model found no confident match. Auto-escalating to Gemini 2.5 Pro...")
            llm_output = ask_llm(query, candidates, model="pro")
            
    print(f"\n=== AI Search Results for '{query}' ===")
    print(llm_output if (llm_output and "NONE" not in llm_output) else "No matching items found by AI.")
    
    if shutil.which("fzf") and sys.stdout.isatty():
        print("\n--- Launching Interactive Selector (Arrow Keys + Enter to Copy) ---")
        run_fzf_selector(candidates[:40])

if __name__ == "__main__":
    main()
