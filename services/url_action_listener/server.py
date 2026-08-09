#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import subprocess
import sys
from pathlib import Path

PORT = 8643

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class ActionHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        action = parsed.path.strip("/")

        print(f"[URL Listener] Received action: '{action}' with params: {params}", flush=True)

        if action == "open_zed":
            target_path = params.get("path", ["/Users/matt/projects/ai-os"])[0]
            print(f"[URL Listener] Opening in Zed: {target_path}", flush=True)
            subprocess.Popen(["zed", target_path])
        elif action == "set_delegation":
            mode = params.get("mode", ["light"])[0]
            print(f"[URL Listener] Setting delegation mode to: {mode}", flush=True)
        else:
            print(f"[URL Listener] Action '{action}' received.", flush=True)

        # Update test_zed_button.md artifact with fresh timestamp on EVERY action click!
        try:
            artifact_path = Path("/Users/matt/.gemini/antigravity/brain/9e52cc09-20b7-4831-8dfd-1077d1ecb5dc/test_zed_button.md")
            if artifact_path.exists():
                import time
                ts = int(time.time() * 1000)
                content = artifact_path.read_text()
                
                banner_html = f'''<div style="background: #11111b; border: 2px solid #a6e3a1; padding: 18px; border-radius: 12px; margin-bottom: 24px; text-align: center; color: #cdd6f4; font-family: system-ui, -apple-system, sans-serif;">
  <h3 style="margin-top:0; color: #a6e3a1; font-size: 16px;">🚀 Invisible HTTP URL Router & Zed Launcher Test</h3>
  <p style="font-size: 13px; color: #bac2de; max-width: 600px; margin: 8px auto;">
    Clicking these links targets <code>http://127.0.0.1:8643</code>. Backend auto-refreshes artifact timestamp ({ts}) on every click!
  </p>
  <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 14px;">
    <a href="http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/gen_conversation_md.py&ts={ts}" style="background: #1e1e2e; color: #a6e3a1; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; border: 1.5px solid #a6e3a1;">📝 Open gen_conversation_md.py in Zed</a>
    <a href="http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os&ts={ts}" style="background: #1e1e2e; color: #89b4fa; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; border: 1.5px solid #89b4fa;">📂 Open AI-OS Project in Zed</a>
    <a href="http://127.0.0.1:8643/set_delegation?mode=strict&ts={ts}" style="background: #1e1e2e; color: #fab387; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; border: 1.5px solid #fab387;">⚡ Set Strict Delegation Mode</a>
  </div>
</div>'''

                if '<div style="background: #11111b;' in content:
                    content = content.split('</div>\n\n', 1)[1]
                
                artifact_path.write_text(banner_html + '\n\n' + content)
                print(f"[URL Listener] Updated test_zed_button.md with timestamp {ts}", flush=True)
        except Exception as e:
            print(f"[URL Listener] Error updating artifact: {e}", flush=True)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def log_message(self, format, *args):
        sys.stderr.write(f"[URL Listener] {format % args}\n")

if __name__ == "__main__":
    with ReusableTCPServer(("127.0.0.1", PORT), ActionHandler) as httpd:
        print(f"[URL Listener] Listening for action links on http://127.0.0.1:{PORT}...", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[URL Listener] Shutting down.")
