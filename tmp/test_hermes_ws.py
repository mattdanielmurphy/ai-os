#!/usr/bin/env python3
"""Quick end-to-end test: connect WS, create session, submit prompt, print events.
Uses only stdlib (no websockets package needed)."""
import asyncio
import json
import hashlib
import base64
import os
import socket
import struct
import sys

WS_URL_HOST = "127.0.0.1"
WS_URL_PORT = 9119
WS_URL_PATH = "/api/ws?token=ai_os_secret_token_123456"
next_id = 1

def make_request(method, params):
    global next_id
    rid = f"r{next_id}"
    next_id += 1
    return json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params}), rid

class SimpleWSClient:
    """Minimal blocking WebSocket client using raw sockets."""
    
    def __init__(self, host, port, path):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(5)
        # Handshake
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        self.sock.sendall(req.encode())
        # Read HTTP response
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise Exception("Connection closed during handshake")
            resp += chunk
        status_line = resp.split(b"\r\n")[0].decode()
        if "101" not in status_line:
            raise Exception(f"Handshake failed: {status_line}")
    
    def send(self, text):
        data = text.encode("utf-8")
        mask_key = os.urandom(4)
        masked = bytearray(len(data))
        for i in range(len(data)):
            masked[i] = data[i] ^ mask_key[i % 4]
        
        frame = bytearray()
        frame.append(0x81)  # FIN + text
        length = len(data)
        if length < 126:
            frame.append(0x80 | length)
        elif length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack("!H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack("!Q", length))
        frame.extend(mask_key)
        frame.extend(masked)
        self.sock.sendall(frame)
    
    def recv(self, timeout=5):
        self.sock.settimeout(timeout)
        try:
            header = self._recv_exact(2)
        except socket.timeout:
            return None
        
        opcode = header[0] & 0x0F
        masked = (header[1] & 0x80) != 0
        length = header[1] & 0x7F
        
        if length == 126:
            length = struct.unpack("!H", self._recv_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._recv_exact(8))[0]
        
        if masked:
            mask_key = self._recv_exact(4)
            data = bytearray(self._recv_exact(length))
            for i in range(length):
                data[i] ^= mask_key[i % 4]
        else:
            data = self._recv_exact(length)
        
        if opcode == 0x08:  # close
            return None
        if opcode == 0x09:  # ping
            # send pong
            pong = bytearray([0x8A, 0x80 | len(data)]) + os.urandom(4)
            self.sock.sendall(pong)
            return self.recv(timeout)
        
        return data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else data
    
    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise Exception("Connection closed")
            buf += chunk
        return buf
    
    def close(self):
        try:
            close_frame = bytearray([0x88, 0x80, 0, 0, 0, 0])
            self.sock.sendall(close_frame)
        except:
            pass
        self.sock.close()

def main():
    print(f"[TEST] Connecting to ws://{WS_URL_HOST}:{WS_URL_PORT}{WS_URL_PATH}...")
    try:
        ws = SimpleWSClient(WS_URL_HOST, WS_URL_PORT, WS_URL_PATH)
    except Exception as e:
        print(f"[TEST] FAILED to connect: {e}")
        return
    
    print("[TEST] Connected! Creating session...")
    
    req, rid = make_request("session.create", {"cols": 96, "source": "ai-os-test", "cwd": "/Users/matt/projects/ai-os"})
    ws.send(req)
    
    session_id = None
    # Read responses for up to 10 seconds
    import time
    deadline = time.time() + 10
    while time.time() < deadline:
        raw = ws.recv(timeout=3)
        if raw is None:
            continue
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                frame = json.loads(line)
            except:
                print(f"[TEST] Bad frame: {line[:200]}")
                continue
            
            if frame.get("id") == rid:
                if frame.get("error"):
                    print(f"[TEST] session.create ERROR: {frame['error']}")
                    ws.close()
                    return
                result = frame.get("result", {})
                session_id = result.get("session_id")
                print(f"[TEST] session.create OK! session_id={session_id}")
                print(f"[TEST] Full result: {json.dumps(result)[:300]}")
            elif frame.get("method") == "event":
                etype = frame.get("params", {}).get("type", "?")
                print(f"[TEST] EVENT: {etype}")
            else:
                print(f"[TEST] OTHER: {json.dumps(frame)[:200]}")
        
        if session_id:
            break
    
    if not session_id:
        print("[TEST] FAILED: never got session_id from session.create")
        ws.close()
        return
    
    # Submit a prompt
    print(f"\n[TEST] Submitting prompt 'say hi' to session {session_id}...")
    req, rid = make_request("prompt.submit", {"session_id": session_id, "text": "say hi"})
    ws.send(req)
    
    # Collect events for up to 60 seconds
    event_count = 0
    deadline = time.time() + 60
    got_complete = False
    while time.time() < deadline and not got_complete:
        raw = ws.recv(timeout=5)
        if raw is None:
            if event_count > 2:
                print("[TEST] Timeout waiting for more events, stopping.")
                break
            continue
        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                frame = json.loads(line)
            except:
                continue
            
            if frame.get("id") == rid:
                result = frame.get("result", {})
                err = frame.get("error")
                if err:
                    print(f"[TEST] prompt.submit ERROR: {err}")
                else:
                    print(f"[TEST] prompt.submit OK: {result}")
            elif frame.get("method") == "event":
                params = frame.get("params", {})
                etype = params.get("type", "?")
                payload = params.get("payload", {})
                text = payload.get("text", "") if isinstance(payload, dict) else ""
                event_count += 1
                if etype == "message.delta":
                    sys.stdout.write(text)
                    sys.stdout.flush()
                elif etype == "message.complete":
                    print(f"\n[TEST] COMPLETE!")
                    got_complete = True
                elif etype == "error":
                    msg = payload.get("message", "?") if isinstance(payload, dict) else str(payload)
                    print(f"[TEST] ERROR EVENT: {msg}")
                else:
                    print(f"[TEST] EVENT: {etype}")
    
    print(f"\n[TEST] Done. Got {event_count} events total. Success={got_complete}")
    ws.close()

main()
