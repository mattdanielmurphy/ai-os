import os
import re
import subprocess
import json
import uuid
import time
import logging
import urllib.request
import urllib.error
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agy-proxy")

LITELLM_URL = "http://127.0.0.1:8082"

AVAILABLE_MODELS = [
    "agy",
    "subagent",
    "gemini-3.6-flash-low",
    "gemini-3.6-flash-medium",
    "gemini-3.6-flash-high",
    "gemini-3.1-pro-low",
    "gemini-3.1-pro-high",
    "claude-sonnet-4-6",
    "claude-opus-4-6-thinking",
    "gpt-oss-120b-medium",
]

app = FastAPI()
_executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------------------------
# Pydantic schemas — full OpenAI chat completions format with tools
# ---------------------------------------------------------------------------
class FunctionDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ToolFunction(BaseModel):
    type: str = "function"
    function: FunctionDefinition


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]


class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    tools: Optional[List[ToolFunction]] = None
    tool_choice: Optional[Any] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


# ---------------------------------------------------------------------------
# agy CLI path (no tools — uses Matt's paid Google quota)
# ---------------------------------------------------------------------------
MODEL_OVERRIDE_RE = re.compile(r'\{MODEL=([^}]+)\}')


def _resolve_model(messages: List[Message], model_name: str) -> str:
    """Scan messages (first match wins) for {MODEL=alias}, strip the tag in-place,
    and return the alias. Falls back to model_name if no tag found.

    Pitfall: if model_name is the 'subagent' placeholder and no tag is found,
    this returns 'subagent' — callers must guard against that.
    """
    for msg in messages:
        if msg.content and MODEL_OVERRIDE_RE.search(msg.content):
            match = MODEL_OVERRIDE_RE.search(msg.content)
            override = match.group(1).strip()
            # Strip tag from ALL messages so nothing leaks to the LLM
            for m in messages:
                if m.content:
                    m.content = MODEL_OVERRIDE_RE.sub("", m.content).strip()
            logger.info(f"[model-override] {model_name!r} \u2192 {override!r}")
            return override
    return model_name


def _build_agy_prompt(messages: List[Message]) -> str:
    parts = []
    for msg in messages:
        role = msg.role.upper()
        content = msg.content or ""
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


def run_agy_stream(messages: List[Message], model_name: str):
    model_name = _resolve_model(messages, model_name)
    if model_name == "subagent":
        logger.warning("[model-override] No {MODEL=...} tag found; falling back to agy default")
        model_name = "agy"
    prompt = _build_agy_prompt(messages)
    request_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())

    yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"

    cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print"]
    if model_name and model_name != "agy":
        cmd.extend(["--model", model_name])
    cmd.append(prompt)
    logger.info(f"agy stream cmd: {' '.join(cmd[:5])}...")

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
                "id": request_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "delta": {"content": line},
                    "finish_reason": None,
                }],
            }
            yield f"data: {json.dumps(payload)}\n\n"

        proc.wait()
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
    except Exception as e:
        logger.error(f"agy stream error: {e}")
        err_msg = f"[Proxy Error]: {e}"
        payload = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model_name,
            "choices": [{
                "index": 0,
                "delta": {"content": err_msg},
                "finish_reason": "error",
            }],
        }
        yield f"data: {json.dumps(payload)}\n\n"
    finally:
        if proc.poll() is None:
            proc.kill()
    yield "data: [DONE]\n\n"


def run_agy_sync(messages: List[Message], model_name: str) -> dict:
    model_name = _resolve_model(messages, model_name)
    if model_name == "subagent":
        logger.warning("[model-override] No {MODEL=...} tag found; falling back to agy default")
        model_name = "agy"
    prompt = _build_agy_prompt(messages)
    cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print"]
    if model_name and model_name != "agy":
        cmd.extend(["--model", model_name])
    cmd.append(prompt)
    logger.info(f"agy sync cmd: {' '.join(cmd[:5])}...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result.stdout,
            },
            "finish_reason": "stop",
        }],
    }


# ---------------------------------------------------------------------------
# LiteLLM proxy path (supports tools)
# ---------------------------------------------------------------------------
def _urllib_post(url: str, data: dict) -> dict:
    """Synchronous POST with urllib — returns parsed JSON."""
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def _proxy_to_litellm(payload: dict) -> dict:
    """Forward a non-streaming request to the real LiteLLM proxy."""
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(
            _executor,
            _urllib_post,
            f"{LITELLM_URL}/v1/chat/completions",
            payload,
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LiteLLM HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"LiteLLM connection failed: {e.reason}") from e


async def _proxy_to_litellm_stream(payload: dict, request_model: str):
    """Stream a tool-enabled request from the real LiteLLM proxy using
    urllib in a thread (non-blocking via run_in_executor)."""
    request_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())

    stream_payload = {**payload, "stream": True}
    body = json.dumps(stream_payload).encode("utf-8")
    req = urllib.request.Request(
        f"{LITELLM_URL}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    loop = asyncio.get_event_loop()

    def _stream_lines():
        """Generator that yields SSE lines from LiteLLM."""
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if decoded:
                        yield decoded
        except Exception as e:
            yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': request_model, 'choices': [{'index': 0, 'delta': {'content': f'[Proxy Error]: {e}'}, 'finish_reason': 'error'}]})}"
            yield "data: [DONE]"

    def _iterate():
        for line_data in _stream_lines():
            if not line_data.startswith("data: "):
                continue
            yield line_data + "\n"

    # Run the blocking generator in a thread, yielding chunks asynchronously
    it = iter([])
    # Use a simple approach: collect all lines, then yield them
    all_lines = await loop.run_in_executor(_executor, lambda: list(_stream_lines()))

    for raw_line in all_lines:
        if raw_line.startswith("data: "):
            data_str = raw_line[6:].strip()
        else:
            data_str = raw_line.strip()

        if data_str == "[DONE]":
            yield "data: [DONE]\n\n"
            return

        try:
            chunk = json.loads(data_str)
            chunk["model"] = request_model
            chunk["id"] = request_id
            chunk["created"] = created_time
            yield f"data: {json.dumps(chunk)}\n\n"
        except json.JSONDecodeError:
            continue


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    has_tools = request.tools and len(request.tools) > 0
    logger.info(
        f"Request model={request.model} stream={request.stream} "
        f"tools={has_tools} messages={len(request.messages)}"
    )

    if has_tools:
        # Tools present — must route through real LiteLLM (agy can't handle tools)
        payload = request.model_dump(exclude_none=True)
        if request.stream:
            return StreamingResponse(
                _proxy_to_litellm_stream(payload, request.model),
                media_type="text/event-stream",
            )
        else:
            try:
                result = await _proxy_to_litellm(payload)
                return result
            except Exception as e:
                logger.error(f"LiteLLM proxy error: {e}")
                return JSONResponse(
                    status_code=502,
                    content={
                        "error": {
                            "message": f"LiteLLM proxy error: {e}",
                            "type": "proxy_error",
                        }
                    },
                )

    # No tools — use agy CLI path (preserves paid Google quota)
    if request.stream:
        return StreamingResponse(
            run_agy_stream(request.messages, request.model),
            media_type="text/event-stream",
        )
    else:
        return run_agy_sync(request.messages, request.model)


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": m, "object": "model", "created": 1700000000, "owned_by": "agy"}
            for m in AVAILABLE_MODELS
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)