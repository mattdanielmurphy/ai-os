import asyncio
import sys

async def test():
    try:
        import websockets
    except ImportError:
        print("websockets package not installed")
        return

    import json
    uri = "ws://127.0.0.1:9119/api/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            req = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "session.create",
                "params": {"cols": 80, "source": "test"}
            }
            await websocket.send(json.dumps(req))
            resp = await websocket.recv()
            print("Response:", resp)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    asyncio.run(test())
