#!/usr/bin/env python3
import asyncio
import json
import logging
import sys
import os
import argparse
import websockets
from pathlib import Path

# Add current dir to path to import triage_router
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from triage_router import tier1_triage
except ImportError:
    print("Could not import triage_router")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [TriageProxy] - %(levelname)s - %(message)s")
logger = logging.getLogger("TriageProxy")

TARGET_HOST = "127.0.0.1"

async def handle_client(websocket, target_port):
    target_url = f"ws://{TARGET_HOST}:{target_port}/api/ws"
    logger.info(f"New client connected. Connecting to target {target_url}...")
    
    try:
        async with websockets.connect(target_url) as target_ws:
            logger.info("Connected to target Hermes server.")

            async def client_to_target():
                try:
                    async for message in websocket:
                        try:
                            # Because websockets may return bytes or string, handle accordingly
                            if isinstance(message, bytes):
                                text_msg = message.decode("utf-8")
                            else:
                                text_msg = message
                                
                            data = json.loads(text_msg)
                            if data.get("method") == "prompt.submit":
                                text = data.get("params", {}).get("text", "")
                                logger.info(f"Intercepted prompt.submit: {text[:50]}...")
                                category = tier1_triage(text)
                                logger.info(f"Triage category: {category}")
                                
                                if category == "valve_boilerplate":
                                    # Handle instantly without hitting Hermes Agent
                                    logger.info("Valve boilerplate intercepted. Sending instant response.")
                                    msg_id = f"msg-{int(asyncio.get_event_loop().time() * 1000)}"
                                    
                                    # Spoof boilerplate payload
                                    payload_instructions = (
                                        "== FIRE-AND-FORGET WEB UI VALVE ACTIVATED ==\n"
                                        "This is a massive boilerplate / isolated coding task. To conserve API quotas, run this on Perplexity or Gemini Web UI.\n\n"
                                        "COPY AND PASTE THE FOLLOWING PROMPT INTO THE WEB UI:\n"
                                        "--------------------------------------------------\n"
                                        f"Task instruction:\n{text}\n\n"
                                        "SYSTEM DIRECTIVE: When you have completed this code generation, you MUST conclude your response with a terminal tool-call block exactly formatted as:\n"
                                        "```tool-call\n"
                                        "write_file(path='path/to/target/file', content='...')\n"
                                        "```\n"
                                        "--------------------------------------------------\n"
                                        "The local userscript listener will automatically detect, scrape, and write this output to the codebase files.\n"
                                    )
                                    
                                    # Send message.start
                                    await websocket.send(json.dumps({
                                        "jsonrpc": "2.0",
                                        "method": "event",
                                        "params": {
                                            "type": "message.start",
                                            "payload": {"message_id": msg_id}
                                        }
                                    }))
                                    
                                    # Send message.delta
                                    await websocket.send(json.dumps({
                                        "jsonrpc": "2.0",
                                        "method": "event",
                                        "params": {
                                            "type": "message.delta",
                                            "payload": {"message_id": msg_id, "text": payload_instructions}
                                        }
                                    }))
                                    
                                    # Send message.complete
                                    await websocket.send(json.dumps({
                                        "jsonrpc": "2.0",
                                        "method": "event",
                                        "params": {
                                            "type": "message.complete",
                                            "payload": {"message_id": msg_id}
                                        }
                                    }))
                                    
                                    # Send success response to the rpc id
                                    if "id" in data:
                                        await websocket.send(json.dumps({
                                            "jsonrpc": "2.0",
                                            "id": data.get("id"),
                                            "result": {"status": "ok"}
                                        }))
                                    
                                    continue # Do not forward to target
                        except json.JSONDecodeError:
                            pass
                        except Exception as e:
                            logger.error(f"Error intercepting message: {e}")
                            
                        # Forward to target
                        await target_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Client connection closed.")

            async def target_to_client():
                try:
                    async for message in target_ws:
                        await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Target connection closed.")

            await asyncio.gather(
                client_to_target(),
                target_to_client()
            )
            
    except Exception as e:
        logger.error(f"Failed to connect to target {target_url}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Hermes Triage WebSocket Proxy")
    parser.add_argument("--port", type=int, default=9119, help="Port to listen on")
    parser.add_argument("--target", type=int, default=9120, help="Port of the real Hermes server")
    args = parser.parse_args()

    # Create handler with target port injected
    handler = lambda ws, path: handle_client(ws, args.target)

    logger.info(f"Starting Triage Proxy on ws://127.0.0.1:{args.port}, forwarding to 127.0.0.1:{args.target}")
    try:
        # Note: newer websockets serve only takes handler, host, port. path is for older versions.
        # We will use the standard handler.
        async with websockets.serve(lambda ws: handle_client(ws, args.target), "127.0.0.1", args.port):
            await asyncio.Future()  # run forever
    except OSError as e:
        logger.error(f"Failed to start server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
