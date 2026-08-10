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
from typing import List, Optional, Dict, Any, Union

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
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
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
    """Stable per-conversation identity based on user tag or first system/user anchor message."""
    import hashlib
    if user_tag:
        return hashlib.sha256(f"user:{user_tag}".encode("utf-8")).hexdigest()[:16]
    if not messages:
        return "default"
    # Find first system or user message as session anchor
    anchor = ""
    for msg in messages:
        if msg.role in ("user", "system") and msg.content:
            anchor = msg.content
            break
    if not anchor and messages[0].content:
        anchor = messages[0].content
    return hashlib.sha256(anchor.encode("utf-8")).hexdigest()[:16]


def _build_cmd_and_prompt(messages: List[Message], model_name: str,
                          output_format: Optional[str] = None,
                          user_tag: Optional[str] = None) -> tuple:
    """Build the agy CLI invocation."""
    session_key = _get_session_key(messages, user_tag)
    sessions = _load_sessions()
    conv_id = sessions.get(session_key)

    last_user_parts = []
    for m in reversed(messages):
        if m.role == "user" and m.content:
            if isinstance(m.content, str):
                last_user_parts.append(m.content)
            elif isinstance(m.content, list):
                for part in m.content:
                    if part.get("type") == "text":
                        last_user_parts.append(part.get("text", ""))
                    elif part.get("type") in ("image_url", "image"):
                        img_info = part.get("image_url", part.get("image"))
                        if isinstance(img_info, dict):
                            url = img_info.get("url")
                        else:
                            url = img_info
                        if url:
                            last_user_parts.append(f"[Attached Image: {url}]")
            if last_user_parts:
                last_user = "\n".join(reversed(last_user_parts))
                break

    resume = bool(conv_id and len(messages) > 1 and last_user is not None)

    if resume:
        prompt = last_user or ""
    else:
        prompt = _build_agy_prompt(messages)

    cmd = ["/Users/matt/.local/bin/agy", "--print", prompt, "--dangerously-skip-permissions", "--print-timeout", "10m"]
    if resume and conv_id:
        cmd.extend(["--conversation", conv_id])
        logger.info(f"[agy-session] RESUMING session {session_key} -> conversation {conv_id}")
    else:
        logger.info(f"[agy-session] STARTING FRESH session {session_key} (no previous conversation)")


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
    upload_dir = "./tmp/agy_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    import base64
    
    for msg in messages:
        role = msg.role.upper()
        content = msg.content
        
        if isinstance(content, str):
            parts.append(f"{role}: {content}")
        elif isinstance(content, list):
            block_texts = []
            for part in content:
                if part.get("type") == "text":
                    block_texts.append(part.get("text", ""))
                elif part.get("type") in ("image_url", "image"):
                    img_info = part.get("image_url", part.get("image"))
                    url = img_info.get("url") if isinstance(img_info, dict) else img_info
                    
                    if url and url.startswith("data:image/"):
                        try:
                            header, b64 = url.split(",", 1)
                            ext = header.split(";")[0].split("/")[1]
                            fname = f"{uuid.uuid4()}.{ext}"
                            fpath = os.path.join(upload_dir, fname)
                            with open(fpath, "wb") as f:
                                f.write(base64.b64decode(b64))
                            block_texts.append(f"[Attached Image: {fpath}]")
                        except Exception as e:
                            logger.error(f"Failed to process image attachment: {e}")
                            block_texts.append(f"[Attached Image: (error)]")
                    elif url:
                        block_texts.append(f"[Attached Image: {url}]")
            parts.append(f"{role}: {' '.join(block_texts)}")
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
    has_emitted_any_tool = False
    streamed_response = False
    streamed_final_content = False

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
                # 1. Check for auth login / verification URL keywords
                if "auth login" in line.lower() or "accounts.google.com/o/oauth2" in line.lower() or "enter code" in line.lower():
                    try:
                        cmd_warp = "tell application \"Warp\" to activate"
                        subprocess.run(["osascript", "-e", cmd_warp], capture_output=True)
                        cmd_term = "tell application \"Terminal\" to do script \"/Users/matt/.local/bin/agy auth login\""
                        subprocess.run(["osascript", "-e", cmd_term], capture_output=True)
                    except Exception as ex:
                        logger.error(f"Failed to open terminal for auth: {ex}")

                    # 2. Stream notification
                    auth_msg = (
                        "⚠️ **`agy` OAuth re-authorization required!**\n"
                        "Opening Terminal with `agy auth login` to enter code...\n\n"
                    )
                    payload = {
                        "id": request_id, "object": "chat.completion.chunk",
                        "created": created_time, "model": model_name,
                        "choices": [{"index": 0, "delta": {"reasoning_content": auth_msg}, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

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
                    # Emit reasoning_content badge RIGHT AWAY
                    badge_text = f"agy --conversation {conv_id} --dangerously-skip-permissions\n\n"
                    badge_payload = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": model_name,
                        "choices": [{
                            "index": 0,
                            "delta": {"reasoning_content": badge_text},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(badge_payload)}\n\n"
            elif ev == "step_update":
                s = event.get("step_update", {})
                s_type = s.get("step_type")
                state = s.get("state")

                if s_type == "tool" and state == "ACTIVE":
                    has_emitted_any_tool = True
                    tool_name = s.get("tool_name") or "tool"
                    tool_info = s.get("tool_info") or {}
                    tool_call_id = f"call_{uuid.uuid4().hex[:8]}"

                    tc_payload = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": model_name,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "tool_calls": [{
                                    "id": tool_call_id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": json.dumps(tool_info) if isinstance(tool_info, dict) else str(tool_info)
                                    }
                                }]
                            },
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(tc_payload)}\n\n"

                elif s_type == "agent_response" and s.get("text_delta"):
                    text_delta = s["text_delta"]
                    delta = {"content": text_delta}
                    streamed_response = True

                    payload = {
                        "id": request_id, "object": "chat.completion.chunk",
                        "created": created_time, "model": model_name,
                        "choices": [{"index": 0, "delta": delta, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

            elif ev == "result":
                if not conv_id:
                    conv_id = event.get("conversation_id")
                    if conv_id:
                        _save_session(session_key, conv_id)
                
                # Always process the final result to emit content
                if not streamed_response:
                    raw = event.get("result")
                    content = ""
                    if isinstance(raw, dict):
                        content = raw.get("response", "")
                    elif isinstance(raw, str):
                        content = raw
                if content:
                    payload = {
                        "id": request_id, "object": "chat.completion.chunk",
                        "created": created_time, "model": model_name,
                        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                _log_usage(event.get("usage") or {}, session_key)

        await loop.run_in_executor(_executor, proc.wait)

        if conv_id:
            _save_session(session_key, conv_id)

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
        or request.model.startswith("custom/")
        or request.model.startswith("custom:")
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