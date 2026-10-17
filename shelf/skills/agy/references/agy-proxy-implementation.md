# Agy Proxy Implementation Reference

This reference implementation uses FastAPI to expose `agy --print` as an OpenAI-compatible `/v1/chat/completions` endpoint.

## Proxy Server (`proxy.py`)

```python
import os
import subprocess
import json
import uuid
import time
import logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False

def run_agy_stream(prompt: str, model_name: str):
    request_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())
    yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"

    # CRITICAL: Use absolute path to agy
    cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print", prompt]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    try:
        for line in proc.stdout:
            payload = {
                'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name,
                'choices': [{'index': 0, 'delta': {'content': line}, 'finish_reason': None}]
            }
            yield f"data: {json.dumps(payload)}\n\n"
        proc.wait()
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
    finally:
        if proc.poll() is None: proc.kill()
        yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    prompt = "\n\n".join([f"{m.role.upper()}: {m.content}" for m in request.messages])
    if request.stream:
        return StreamingResponse(run_agy_stream(prompt, request.model), media_type="text/event-stream")
    else:
        cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "id": f"chatcmpl-{uuid.uuid4()}", "object": "chat.completion", "created": int(time.time()), "model": request.model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result.stdout}, "finish_reason": "stop"}]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
```

## Launch Agent Plist (`com.matt.agent.agy-proxy.plist`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matt.agent.agy-proxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/matt/Library/Scripts/tmux-agent-wrapper.sh</string>
        <string>keepalive</string>
        <string>agent-agy-proxy</string>
        <string>/Users/matt/projects/hermes-agent/venv/bin/python3</string>
        <string>/Users/matt/projects/ai-os/services/agy-proxy/proxy.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```
