import os
import re
import subprocess
import json
import uuid
import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agy-proxy")

LITELLM_URL = "http://127.0.0.1:8082"

AGY_MODELS = [
    {"id": "gemini-3.6-flash-low", "name": "Gemini 3.6 Flash (Low)"},
    {"id": "gemini-3.6-flash-medium", "name": "Gemini 3.6 Flash (Medium)"},
    {"id": "gemini-3.6-flash-high", "name": "Gemini 3.6 Flash (High)"},
    {"id": "gemini-3.1-pro-low", "name": "Gemini 3.1 Pro (Low)"},
    {"id": "gemini-3.1-pro-high", "name": "Gemini 3.1 Pro (High)"},
    {"id": "claude-sonnet-4.6", "name": "Claude Sonnet 4.6 (Thinking)"},
    {"id": "claude-opus-4.6", "name": "Claude Opus 4.6 (Thinking)"},
    {"id": "gpt-oss-120b", "name": "GPT-OSS 120B (Medium)"},
]

AVAILABLE_MODELS = [m["id"] for m in AGY_MODELS]

MODEL_ALIAS_MAP = {
    "agy-flash-low": "gemini-3.6-flash-low",
    "agy-flash-med": "gemini-3.6-flash-medium",
    "agy-flash-high": "gemini-3.6-flash-high",
    "agy-pro-low": "gemini-3.1-pro-low",
    "agy-pro-high": "gemini-3.1-pro-high",
    "claude-sonnet-4-6": "claude-sonnet-4.6",
    "claude-opus-4-6-thinking": "claude-opus-4.6",
    "gpt-oss-120b-medium": "gpt-oss-120b",
}

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


def normalize_model_name(model_name: str) -> str:
    """Normalize model string by stripping provider prefixes and expanding aliases."""
    m = model_name.strip()
    if m.startswith("@custom:agy:"):
        m = m[len("@custom:agy:"):]
    elif m.startswith("agy/"):
        m = m[len("agy/"):]
    elif m.startswith("custom/"):
        m = m[len("custom/"):]
    elif m.startswith("custom:"):
        m = m[len("custom:"):]
    return MODEL_ALIAS_MAP.get(m, m)


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
    """Stable per-conversation identity."""
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
    """Build the agy CLI invocation."""
    session_key = _get_session_key(messages, user_tag)
    sessions = _load_sessions()
    conv_id = sessions.get(session_key)

    last = messages[-1] if messages else None
    resume = bool(conv_id and len(messages) > 1 and last is not None and last.role == "user")

    if resume:
        prompt = last.content or ""
    else:
        prompt = _build_agy_prompt(messages)

    cmd = ["/Users/matt/.local/bin/agy", "--print", prompt, "--dangerously-skip-permissions", "--print-timeout", "10m"]
    if resume and conv_id:
        cmd.extend(["--conversation", conv_id])
        logger.info(f"[agy-session] Resuming session {session_key} -> conversation {conv_id}")
    else:
        logger.info(f"[agy-session] Starting fresh session {session_key} (no conversation yet)")

    resolved_model = normalize_model_name(model_name)
    if resolved_model in ("agy", "subagent", ""):
        resolved_model = "gemini-3.6-flash-low"

    effort = None
    base_model = resolved_model
    for eff in ("-low", "-medium", "-high"):
        if resolved_model.endswith(eff):
            effort = eff[1:]
            base_model = resolved_model[:-len(eff)]
            break

    if base_model:
        cmd.extend(["--model", base_model])
    if effort:
        cmd.extend(["--effort", effort])
    if output_format:
        cmd.extend(["--output-format", output_format])
    return cmd, session_key


def _resolve_model(messages: List[Message], model_name: str) -> str:
    """Scan messages (first match wins) for {MODEL=alias}, strip the tag in-place,
    and return the alias. Falls back to model_name if no tag found.
    """
    for msg in messages:
        if msg.content and MODEL_OVERRIDE_RE.search(msg.content):
            match = MODEL_OVERRIDE_RE.search(msg.content)
            override = match.group(1).strip()
            for m in messages:
                if m.content:
                    m.content = MODEL_OVERRIDE_RE.sub("", m.content).strip()
            logger.info(f"[model-override] {model_name!r} → {override!r}")
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
    if not usage:
        return
    logger.info(
        f"[agy-usage] session={session_key} "
        f"input={usage.get('input_tokens')} output={usage.get('output_tokens')} "
        f"cache_read={usage.get('cache_read_tokens')} total={usage.get('total_tokens')}"
    )


async def run_agy_stream(messages: List[Message], model_name: str, user_tag: Optional[str] = None):
    model_name = _resolve_model(messages, model_name)
    if model_name in ("subagent", "agy"):
        model_name = "gemini-3.6-flash-low"

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
    streamed_response = False

    try:
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(_executor, proc.stdout.readline)
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
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
                    tool_id = f"call_{tool}_{int(time.time()*1000)}"
                    
                    if s.get("state") == "ACTIVE":
                        payload = {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": model_name,
                            "choices": [{
                                "index": 0,
                                "delta": {
                                    "tool_calls": [{
                                        "index": 0,
                                        "id": tool_id,
                                        "type": "function",
                                        "function": {
                                            "name": tool,
                                            "arguments": "{}"
                                        }
                                    }]
                                },
                                "finish_reason": None
                            }]
                        }
                    else:
                        # Send a finish chunk or empty delta to signify completion
                        payload = {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": model_name,
                            "choices": [{
                                "index": 0,
                                "delta": {
                                    "tool_calls": [{
                                        "index": 0,
                                        "id": tool_id,
                                        "type": "function",
                                        "function": {
                                            "name": tool,
                                            "arguments": "{}"
                                        }
                                    }]
                                },
                                "finish_reason": None
                            }]
                        }
                    yield f"data: {json.dumps(payload)}\n\n"

                elif s_type == "agent_response" and s.get("text_delta"):
                    streamed_response = True
                    payload = {"id": request_id, "object": "chat.completion.chunk",
                               "created": created_time, "model": model_name,
                               "choices": [{"index": 0, "delta": {"content": s["text_delta"]},
                                            "finish_reason": None}]}
                    yield f"data: {json.dumps(payload)}\n\n"
            elif ev == "result":
                if not conv_id:
                    conv_id = event.get("conversation_id")
                    if conv_id:
                        _save_session(session_key, conv_id)
                _log_usage(event.get("usage") or {}, session_key)
                if streamed_response:
                    continue
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

        await loop.run_in_executor(_executor, proc.wait)

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
    if model_name in ("subagent", "agy"):
        model_name = "gemini-3.6-flash-low"

    cmd, session_key = _build_cmd_and_prompt(
        messages, model_name, output_format="json", user_tag=user_tag)
    logger.info(f"agy sync cmd: {' '.join(cmd[:4])}...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout or ""

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
# LiteLLM proxy path (supports tools and real-time streaming)
# ---------------------------------------------------------------------------
async def _proxy_to_litellm(payload: dict) -> dict:
    """Forward a non-streaming request to LiteLLM."""
    normalized_model = normalize_model_name(payload.get("model", "gemini-3.6-flash-low"))
    payload["model"] = normalized_model
    timeout = httpx.Timeout(timeout=600.0, connect=30.0, read=300.0, write=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{LITELLM_URL}/v1/chat/completions", json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"LiteLLM HTTP {resp.status_code}: {resp.text}")
        return resp.json()


async def _proxy_to_litellm_stream(payload: dict, request_model: str):
    """Stream a tool-enabled request from LiteLLM using true real-time async chunk streaming."""
    request_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())

    normalized_model = normalize_model_name(request_model)
    stream_payload = {**payload, "stream": True, "model": normalized_model}

    # Connect with generous timeout and no read timeout during streaming
    timeout = httpx.Timeout(timeout=600.0, connect=30.0, read=None, write=60.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{LITELLM_URL}/v1/chat/completions",
                json=stream_payload,
            ) as resp:
                if resp.status_code != 200:
                    err_text = await resp.aread()
                    err_msg = f"[Proxy Error]: LiteLLM returned {resp.status_code}: {err_text.decode('utf-8', errors='replace')}"
                    logger.error(err_msg)
                    payload_err = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": request_model,
                        "choices": [{"index": 0, "delta": {"content": err_msg}, "finish_reason": "error"}],
                    }
                    yield f"data: {json.dumps(payload_err)}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for raw_line in resp.aiter_lines():
                    if not raw_line:
                        continue
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
                        if "id" not in chunk:
                            chunk["id"] = request_id
                        if "created" not in chunk:
                            chunk["created"] = created_time
                        yield f"data: {json.dumps(chunk)}\n\n"
                    except json.JSONDecodeError:
                        yield f"{raw_line}\n\n"

    except Exception as e:
        logger.error(f"LiteLLM stream exception: {e}")
        payload_err = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": request_model,
            "choices": [{"index": 0, "delta": {"content": f"[Proxy Error]: {e}"}, "finish_reason": "error"}],
        }
        yield f"data: {json.dumps(payload_err)}\n\n"
        yield "data: [DONE]\n\n"


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

    # STRICT AGY GUARANTEE:
    # If request is an agy model (or default agy prefix), ALWAYS route to agy CLI directly.
    # NEVER fall back to LiteLLM or paid Google / OpenRouter APIs.
    norm_model = normalize_model_name(request.model)
    is_agy_model = (
        request.model.startswith("agy/")
        or request.model.startswith("@custom:agy:")
        or norm_model in AVAILABLE_MODELS
        or norm_model in MODEL_ALIAS_MAP.values()
        or norm_model in ("agy", "subagent")
    )

    if has_tools and not is_agy_model:
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

    if request.stream:
        return StreamingResponse(
            run_agy_stream(request.messages, request.model, user_tag=request.user),
            media_type="text/event-stream",
        )
    else:
        return run_agy_sync(request.messages, request.model, user_tag=request.user)



@app.get("/v1/models")
@app.get("/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": m["id"],
                "name": m["name"],
                "object": "model",
                "created": 1700000000,
                "owned_by": "antigravity",
            }
            for m in AGY_MODELS
        ],
    }


@app.get("/v1/models/{model_id:path}")
@app.get("/models/{model_id:path}")
async def get_model(model_id: str):
    normalized = normalize_model_name(model_id)
    return {
        "id": model_id,
        "object": "model",
        "created": 1700000000,
        "owned_by": "agy",
        "parent": normalized,
    }


@app.get("/v1/props")
@app.get("/props")
@app.get("/version")
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.3.0", "provider": "agy-proxy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)