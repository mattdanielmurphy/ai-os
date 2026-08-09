#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import subprocess
import sys
from pathlib import Path

PORT = 8643

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

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def log_message(self, format, *args):
        sys.stderr.write(f"[URL Listener] {format % args}\n")

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), ActionHandler) as httpd:
        print(f"[URL Listener] Listening for action links on http://127.0.0.1:{PORT}...", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[URL Listener] Shutting down.")
