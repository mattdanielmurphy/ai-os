import os
import subprocess
import json
import uuid
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agy-proxy")

app = FastAPI()

# All available Antigravity models for agy routing
AVAILABLE_MODELS = [
    "agy",
    "gemini-3.6-flash-low",
    "gemini-3.6-flash-medium",
    "gemini-3.6-flash-high",
    "gemini-3.1-pro-low",
    "gemini-3.1-pro-high",
    "claude-sonnet-4-6",
    "claude-opus-4-6-thinking",
    "gpt-oss-120b-medium",
]

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
    
    # Send role start
    yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"

    # Build agy command — pass --model when a specific model is requested
    cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print"]
    if model_name and model_name != "agy":
        cmd.extend(["--model", model_name])
    cmd.append(prompt)
    logger.info(f"Running command: {' '.join(cmd)}")
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        for line in proc.stdout:
            payload = {
                'id': request_id, 
                'object': 'chat.completion.chunk', 
                'created': created_time, 
                'model': model_name, 
                'choices': [{
                    'index': 0, 
                    'delta': {'content': line}, 
                    'finish_reason': None
                }]
            }
            yield f"data: {json.dumps(payload)}\n\n"
        
        proc.wait()
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
    except Exception as e:
        logger.error(f"Stream error: {e}")
        error_payload = {
            'id': request_id, 
            'object': 'chat.completion.chunk', 
            'created': created_time, 
            'model': model_name, 
            'choices': [{
                'index': 0, 
                'delta': {'content': f'\n[Proxy Error]: {str(e)}'}, 
                'finish_reason': 'error'
            }]
        }
        yield f"data: {json.dumps(error_payload)}\n\n"
    finally:
        if proc.poll() is None:
            proc.kill()
        yield "data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    prompt = ""
    for msg in request.messages:
        prompt += f"{msg.role.upper()}: {msg.content}\n\n"
    
    logger.info(f"Received request for model: {request.model} (stream={request.stream})")
    
    if request.stream:
        return StreamingResponse(run_agy_stream(prompt, request.model), media_type="text/event-stream")
    else:
        cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print"]
        if request.model and request.model != "agy":
            cmd.extend(["--model", request.model])
        cmd.append(prompt)
        logger.info(f"Running sync command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result.stdout
                },
                "finish_reason": "stop"
            }]
        }

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "created": 1700000000, "owned_by": "agy"}
            for m in AVAILABLE_MODELS
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)