#!/usr/bin/env python3
import sys
import os
import shutil
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8649

def swap_turn_by_url(url_str: str) -> str:
    """
    Parses ai-os-turn:// URL arguments and copies the specified history/turn_XX.md
    file over conversation_response.md in-place.
    Returns a status message.
    """
    print(f"Processing URL: {url_str}")
    parsed = urllib.parse.urlparse(url_str)
    
    # Check scheme
    if parsed.scheme != "ai-os-turn":
        raise ValueError(f"Invalid scheme: {parsed.scheme}. Expected ai-os-turn.")
        
    query_params = urllib.parse.parse_qs(parsed.query)
    
    conv_id = None
    turn_val = None
    
    # Try query parameters
    for key in ['conversation_id', 'conversation-id', 'conv', 'id']:
        if key in query_params:
            conv_id = query_params[key][0]
            break
            
    for key in ['turn_index', 'turn-index', 'turn', 'index', 'file']:
        if key in query_params:
            turn_val = query_params[key][0]
            break
            
    # Try parsing path segments/netloc if query parameters are missing
    if not conv_id or not turn_val:
        netloc = parsed.netloc
        path_parts = [p for p in parsed.path.split('/') if p]
        all_parts = []
        if netloc and netloc != 'swap':
            all_parts.append(netloc)
        all_parts.extend(path_parts)
        
        for part in all_parts:
            if 'turn' in part.lower() or part.endswith('.md') or part.isdigit():
                turn_val = part
            elif len(part) > 8:
                conv_id = part

    if not conv_id:
        raise ValueError("Could not extract conversation_id from URL.")
    if not turn_val:
        raise ValueError("Could not extract turn identifier/index from URL.")
        
    possible_dirs = [
        Path("/Users/matt/.gemini/antigravity/brain") / conv_id,
        Path("/Users/matt/.gemini/antigravity-cli/brain") / conv_id,
        Path("/Users/matt/.gemini/antigravity-ide/brain") / conv_id,
    ]
    brain_dir = None
    for pd in possible_dirs:
        if pd.is_dir():
            brain_dir = pd
            break

    if not brain_dir:
        raise FileNotFoundError(f"Conversation directory does not exist for ID: {conv_id}")
        
    history_dir = brain_dir / "history"
    
    candidates = []
    if turn_val.endswith('.md'):
        candidates.append(turn_val)
        stem = turn_val[:-3]
        if stem.isdigit():
            candidates.append(f"turn_{int(stem)}.md")
            candidates.append(f"turn_{int(stem):02d}.md")
    else:
        candidates.append(f"{turn_val}.md")
        if turn_val.isdigit():
            val_int = int(turn_val)
            candidates.append(f"turn_{val_int}.md")
            candidates.append(f"turn_{val_int:02d}.md")
        if not turn_val.startswith("turn_"):
            candidates.append(f"turn_{turn_val}.md")
            
    target_file = None
    for cand in candidates:
        cand_path = history_dir / cand
        if cand_path.is_file():
            target_file = cand_path
            break
            
    if not target_file and history_dir.is_dir():
        for f in history_dir.glob("*.md"):
            if turn_val in f.name:
                target_file = f
                break
                
    if not target_file:
        raise FileNotFoundError(f"Could not find turn file matching '{turn_val}' in {history_dir} (candidates: {candidates})")
        
    dest_file = brain_dir / "conversation_response.md"
    shutil.copy2(target_file, dest_file)
    msg = f"Successfully swapped {target_file.name} to {dest_file}"
    print(msg)
    return msg

class TurnSwapHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/swap":
            query = urllib.parse.parse_qs(parsed_path.query)
            url_param = query.get("url")
            if url_param:
                try:
                    msg = swap_turn_by_url(url_param[0])
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(f'{{"status": "success", "message": "{msg}"}}'.encode())
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode())
                    return
            
            conv_id = query.get("conversation_id") or query.get("id")
            turn = query.get("turn_index") or query.get("turn")
            if conv_id and turn:
                try:
                    mock_url = f"ai-os-turn://swap?conversation_id={conv_id[0]}&turn_index={turn[0]}"
                    msg = swap_turn_by_url(mock_url)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(f'{{"status": "success", "message": "{msg}"}}'.encode())
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode())
                    return
                    
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Missing url parameter or conversation_id and turn_index"}')
            return
            
        elif parsed_path.path in ["/", "/status", "/health"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "running", "service": "agent-turn-swap"}')
            return
            
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

def main():
    if len(sys.argv) > 1:
        url_arg = sys.argv[1]
        try:
            swap_turn_by_url(url_arg)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Starting agent-turn-swap HTTP server on port {PORT}...")
        server = HTTPServer(("127.0.0.1", PORT), TurnSwapHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server...")
            server.server_close()

if __name__ == "__main__":
    main()
