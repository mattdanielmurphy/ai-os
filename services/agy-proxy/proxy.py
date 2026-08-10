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
    user: Optional[str] = None


# ---------------------------------------------------------------------------
# agy CLI path (no tools — uses Matt's paid Google quota)
# ---------------------------------------------------------------------------
MODEL_OVERRIDE_RE = re.compile(r'\{MODEL=([^}]+)\}')
SESSION_FILE = os.path.expanduser("~/.hermes/agy_proxy_sessions.json")
THREAD_RE = re.compile(r'/brain/([a-f0-9\-]+)/thread\.md')
# Emit compact tool-activity markers (e.g. "⌛ list_dir ✓") into the SSE stream
# so the Hermes chat shows agy working (mirrors the live step_update events).
SHOW_TOOL_MARKERS = os.environ.get("AGY_PROXY_TOOL_MARKERS", "1") == "1"


def _load_sessions() -> dict:
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_session(key: str, conv_id: str):
    sessions = _load_sessions()
    sessions[key] = conv_id
    try:
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        with open(SESSION_FILE, "w") as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save agy session: {e}")


def _get_session_key(messages: List[Message], user_tag: Optional[str] = None) -> str:
    """Stable per-conversation identity.

    Priority:
    1. `user` field of the OpenAI request, when present (best — Hermes may
       tag sessions with it; truly unique per conversation).
    2. messages[0] (system prompt) — stable across turns within a session.
       messages[1] is NOT included: it can appear/disappear as history grows
       (1 message on turn 1, 3+ later), which would silently change the key.
    """
    import hashlib
    if user_tag:
        return hashlib.sha256(f"user:{user_tag}".encode("utf-8")).hexdigest()[:16]
    if not messages:
        return "default"
    first = messages[0]
    anchor = first.content if first else ""
    return hashlib.sha256(f"{first.role if first else ''}|{anchor}".encode("utf-8")).hexdigest()[:16]


def _build_cmd_and_prompt(messages: List[Message], model_name: str,
                          output_format: Optional[str] = None,
                          user_tag: Optional[str] = None) -> tuple:
    """Build the agy CLI invocation.

    CRITICAL flag order: `--print` consumes the NEXT argument as the prompt
    text, so the prompt must come immediately after `--print` and ALL other
    flags (--conversation/--model/--output-format) must follow it. Putting
    flags before the prompt makes agy treat them as the prompt text.
    """
    session_key = _get_session_key(messages, user_tag)
    sessions = _load_sessions()
    conv_id = sessions.get(session_key)

    last = messages[-1] if messages else None
    resume = bool(conv_id and len(messages) > 1 and last is not None and last.role == "user")

    if resume:
        prompt = last.content or ""
    else:
        prompt = _build_agy_prompt(messages)

    cmd = ["/Users/matt/.local/bin/agy", "--print", prompt, "--dangerously-skip-permissions"]
    if resume and conv_id:
        cmd.extend(["--conversation", conv_id])
        logger.info(f"[agy-session] Resuming session {session_key} -> conversation {conv_id}")
    else:
        logger.info(f"[agy-session] Starting fresh session {session_key} (no conversation yet)")

    if model_name and model_name != "agy":
        cmd.extend(["--model", model_name])
    if output_format:
        cmd.extend(["--output-format", output_format])
    return cmd, session_key


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


def _log_usage(usage: dict, session_key: str):
    """Log token/cache metrics so we can verify session resume actually hits KV cache."""
    if not usage:
        return
    logger.info(
        f"[agy-usage] session={session_key} "
        f"input={usage.get('input_tokens')} output={usage.get('output_tokens')} "
        f"cache_read={usage.get('cache_read_tokens')} total={usage.get('total_tokens')}"
    )


def run_agy_stream(messages: List[Message], model_name: str, user_tag: Optional[str] = None):
    model_name = _resolve_model(messages, model_name)
    if model_name == "subagent":
        logger.warning("[model-override] No {MODEL=...} tag found; falling back to agy default")
        model_name = "agy"

    cmd, session_key = _build_cmd_and_prompt(
        messages, model_name, output_format="stream-json", user_tag=user_tag)
    request_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())

    yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': model_name, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"

    logger.info(f"agy stream cmd: {' '.join(cmd[:4])}...")

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    conv_id = None
    saw_result = False
    streamed_response = False  # True once agent_response text_delta has been streamed

    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                # Non-JSON output — forward raw (defensive fallback)
                payload = {"id": request_id, "object": "chat.completion.chunk",
                           "created": created_time, "model": model_name,
                           "choices": [{"index": 0, "delta": {"content": line},
                                        "finish_reason": None}]}
                yield f"data: {json.dumps(payload)}\n\n"
                continue

            ev = event.get("event")
            if ev == "init":
                conv_id = event.get("conversation_id")
                if conv_id:
                    _save_session(session_key, conv_id)
                    logger.info(f"[agy-session] init: saved {session_key} -> {conv_id}")
            elif ev == "step_update":
                s = event.get("step_update", {})
                s_type = s.get("step_type")
                if s_type == "tool" and SHOW_TOOL_MARKERS:
                    tool = s.get("tool_name", "tool")
                    markers = "\n`⚙️ running {tool}`\n".format(tool=tool) if s.get("state") == "ACTIVE" else f"`✅ {tool} done`"
                    payload = {"id": request_id, "object": "chat.completion.chunk",
                               "created": created_time, "model": model_name,
                               "choices": [{"index": 0, "delta": {"content": markers},
                                            "finish_reason": None}]}
                    yield f"data: {json.dumps(payload)}\n\n"
                elif s_type == "agent_response" and s.get("text_delta"):
                    # True incremental response streaming
                    streamed_response = True
                    payload = {"id": request_id, "object": "chat.completion.chunk",
                               "created": created_time, "model": model_name,
                               "choices": [{"index": 0, "delta": {"content": s["text_delta"]},
                                            "finish_reason": None}]}
                    yield f"data: {json.dumps(payload)}\n\n"
            elif ev == "result":
                saw_result = True
                if not conv_id:
                    conv_id = event.get("conversation_id")
                    if conv_id:
                        _save_session(session_key, conv_id)
                _log_usage(event.get("usage") or {}, session_key)
                if streamed_response:
                    continue  # text_delta deltas already covered the response
                # result is a repr()'d Python dict, e.g.
                # "{'conversation_id': ..., 'status': 'SUCCESS', 'response': '...'}"
                import ast
                content = ""
                raw = event.get("result")
                if raw:
                    if isinstance(raw, str):
                        try:
                            result_dict = ast.literal_eval(raw)
                            if isinstance(result_dict, dict):
                                content = result_dict.get("response", "")
                        except (ValueError, SyntaxError):
                            content = raw
                    elif isinstance(raw, dict):
                        content = raw.get("response", "")
                if content:
                    payload = {"id": request_id, "object": "chat.completion.chunk",
                               "created": created_time, "model": model_name,
                               "choices": [{"index": 0, "delta": {"content": content},
                                            "finish_reason": None}]}
                    yield f"data: {json.dumps(payload)}\n\n"

        proc.wait()

        if conv_id:
            _save_session(session_key, conv_id)
            logger.info(f"[agy-session] Saved session {session_key} -> {conv_id}")

        payload = {"id": request_id, "object": "chat.completion.chunk",
                   "created": created_time, "model": model_name,
                   "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
        yield f"data: {json.dumps(payload)}\n\n"
    except Exception as e:
        logger.error(f"agy stream error: {e}")
        err_msg = f"[Proxy Error]: {e}"
        payload = {"id": request_id, "object": "chat.completion.chunk",
                   "created": created_time, "model": model_name,
                   "choices": [{"index": 0, "delta": {"content": err_msg},
                                "finish_reason": "error"}]}
        yield f"data: {json.dumps(payload)}\n\n"
    finally:
        if proc.poll() is None:
            proc.kill()
    yield "data: [DONE]\n\n"


def run_agy_sync(messages: List[Message], model_name: str, user_tag: Optional[str] = None) -> dict:
    model_name = _resolve_model(messages, model_name)
    if model_name == "subagent":
        logger.warning("[model-override] No {MODEL=...} tag found; falling back to agy default")
        model_name = "agy"

    cmd, session_key = _build_cmd_and_prompt(
        messages, model_name, output_format="json", user_tag=user_tag)
    logger.info(f"agy sync cmd: {' '.join(cmd[:4])}...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout or ""

    # Parse JSON envelope: {conversation_id, status, response, usage}
    conv_id = None
    content = out
    usage = None
    try:
        data = json.loads(out)
        conv_id = data.get("conversation_id")
        content = data.get("response") or out
        usage = data.get("usage") or {}
    except json.JSONDecodeError:
        match = THREAD_RE.search(out)
        if match:
            conv_id = match.group(1)

    if conv_id:
        _save_session(session_key, conv_id)
    _log_usage(usage or {}, session_key)

    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content,
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
            run_agy_stream(request.messages, request.model, user_tag=request.user),
            media_type="text/event-stream",
        )
    else:
        return run_agy_sync(request.messages, request.model, user_tag=request.user)


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