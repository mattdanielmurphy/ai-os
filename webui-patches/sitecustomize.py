"""
Hermes WebUI - AI-OS Triage Interceptor
========================================
Loaded automatically at Python startup via PYTHONPATH (set in hermes-webui/.env).
Installs three patches into the Hermes agent process:

  1. agent.chat_completion_helpers.interruptible_api_call — intercepts coding
     prompts and returns a synthetic agy_start tool call instead of hitting any
     LLM provider. Mirrors aios_hermes_wrapper.py used by the TUI/gateway.

  2. agent.auxiliary_client.resolve_provider_client — adds native 'agy' support
     to old ~/.hermes/hermes-agent builds that predate the agy provider.

  3. os.environ AGY_API_KEY — sets the bypass key so PROVIDER_REGISTRY lookups
     and env-var checks in agent_init.py pass without a real API key.

All patches are installed via a sys.meta_path hook that fires the first time
agent.chat_completion_helpers is imported, which is after hermes-agent is on
sys.path but before any AIAgent is instantiated.
"""
import sys
import os
import json
import time as _time

# Fix NO_PROXY immediately — the system env may contain bare IPv6 ('::1') and
# CIDR entries ('127.0.0.0/8') which httpx can't parse as URL patterns. This
# must run before any OpenAI/httpx client is constructed.
_raw_no_proxy = os.environ.get("NO_PROXY", "") or os.environ.get("no_proxy", "")
if "::1" in _raw_no_proxy or "/8" in _raw_no_proxy:
    _safe = ",".join(
        p for p in _raw_no_proxy.split(",")
        if "::" not in p.strip() and "/" not in p.strip()
    )
    os.environ["NO_PROXY"] = _safe
    os.environ["no_proxy"] = _safe


_AIOS_SCRIPTS = "/Users/matt/projects/ai-os/scripts"
_PATCHED = False


# ── Helpers ──────────────────────────────────────────────────────────────────

class _AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        for k, v in list(self.items()):
            if isinstance(v, dict):
                self[k] = _AttrDict(v)
            elif isinstance(v, list):
                self[k] = [_AttrDict(x) if isinstance(x, dict) else x for x in v]

    def model_dump(self, *args, **kwargs):
        def _dump(obj):
            if isinstance(obj, _AttrDict):
                return {k: _dump(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_dump(v) for v in obj]
            return obj
        return _dump(self)


def _extract_prompt(api_kwargs):
    messages = api_kwargs.get("messages", [])
    if not messages:
        return ""
    last_msg = messages[-1]
    content = last_msg.get("content", "") if isinstance(last_msg, dict) else getattr(last_msg, "content", "")
    if isinstance(content, list):
        content = " ".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return str(content)


def _synthetic_response(prompt):
    tc_id = f"call_agy_{int(_time.time())}"
    return _AttrDict({
        "id": f"chatcmpl-triage-{int(_time.time())}",
        "object": "chat.completion",
        "created": int(_time.time()),
        "model": "triage-interceptor",
        "choices": [{"index": 0, "message": {
            "role": "assistant",
            "content": "Delegating task to agy.",
            "tool_calls": [{"id": tc_id, "type": "function", "function": {
                "name": "agy_start",
                "arguments": json.dumps({"PROMPT": str(prompt)}),
            }}],
        }, "finish_reason": "tool_calls"}],
    })


def _synthetic_stream(prompt):
    tc_id = f"call_agy_{int(_time.time())}"
    args_json = json.dumps({"PROMPT": str(prompt)})
    base_id = f"chatcmpl-triage-{int(_time.time())}"
    created = int(_time.time())
    yield _AttrDict({"id": base_id, "object": "chat.completion.chunk", "created": created,
                     "model": "triage-interceptor", "choices": [{"index": 0, "delta": {
                         "role": "assistant", "content": "Delegating task to agy.",
                         "tool_calls": [{"index": 0, "id": tc_id, "type": "function",
                                         "function": {"name": "agy_start", "arguments": ""}}],
                     }, "finish_reason": None}]})
    yield _AttrDict({"id": base_id, "object": "chat.completion.chunk", "created": created,
                     "model": "triage-interceptor", "choices": [{"index": 0, "delta": {
                         "tool_calls": [{"index": 0, "function": {"arguments": args_json}}],
                     }, "finish_reason": None}]})
    yield _AttrDict({"id": base_id, "object": "chat.completion.chunk", "created": created,
                     "model": "triage-interceptor",
                     "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]})


_CODING_CATEGORIES = {"coding_standard", "coding_complex", "valve_boilerplate"}


# ── Core patch installer ──────────────────────────────────────────────────────

def _apply_all_patches():
    """Apply all patches. Called once after hermes-agent is on sys.path."""
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    if _AIOS_SCRIPTS not in sys.path:
        sys.path.insert(0, _AIOS_SCRIPTS)

    # ── Patch A: AGY_API_KEY env var ─────────────────────────────────────────
    # Set before any PROVIDER_REGISTRY or env-var lookup in agent_init.py.
    os.environ.setdefault("AGY_API_KEY", "agy-native-bypass-key")
    print("[AIOS WebUI Triage] AGY_API_KEY env var set", file=sys.stderr)

    # ── Patch B: resolve_runtime_provider (WebUI credential resolver) ─────────
    # The WebUI calls resolve_runtime_provider(requested="agy") to get api_key,
    # base_url, and api_mode for _agent_kwargs. Without this, it warns
    # "Unknown provider 'agy'" and leaves _rt unbound, breaking api_mode lookup.
    try:
        import hermes_cli.runtime_provider as _rtp
        _orig_rtp = _rtp.resolve_runtime_provider

        def _patched_rtp(*, requested=None, **kwargs):
            if (requested or "").strip().lower() == "agy":
                return {
                    "provider": "agy",
                    "api_mode": "chat_completions",
                    "base_url": "http://127.0.0.1:8080/v1",
                    "api_key": "agy-native-bypass-key",
                    "source": "aios-webui-bypass",
                    "requested_provider": "agy",
                }
            return _orig_rtp(requested=requested, **kwargs)

        _rtp.resolve_runtime_provider = _patched_rtp
        print("[AIOS WebUI Triage] resolve_runtime_provider patched for agy", file=sys.stderr)
    except Exception as _e:
        print(f"[AIOS WebUI Triage] resolve_runtime_provider patch failed: {_e}", file=sys.stderr)


    # ── Patch B: resolve_provider_client (agy support for old builds) ────────
    try:
        import agent.auxiliary_client as _aux
        _orig_resolve = _aux.resolve_provider_client

        def _patched_resolve(provider, model=None, **kwargs):
            if (provider or "").strip().lower() == "agy":
                # agent_init.py only reads .api_key and .base_url off the returned
                # client — it doesn't make any calls at this stage. Return a stub.
                from types import SimpleNamespace
                stub = SimpleNamespace(
                    api_key="agy-native-bypass-key",
                    base_url="http://127.0.0.1:8080",
                    _custom_headers=None,
                    default_headers=None,
                    _default_headers=None,
                )
                return (stub, model or "agy")
            return _orig_resolve(provider, model=model, **kwargs)

        _aux.resolve_provider_client = _patched_resolve
        print("[AIOS WebUI Triage] resolve_provider_client patched for agy", file=sys.stderr)
    except Exception as _e:
        print(f"[AIOS WebUI Triage] resolve_provider_client patch failed: {_e}", file=sys.stderr)


    # ── Patch C: interruptible_api_call (triage interceptor) ─────────────────
    try:
        import triage_router
        import agent.chat_completion_helpers as helpers

        original_api_call = helpers.interruptible_api_call
        original_streaming = getattr(helpers, "interruptible_streaming_api_call", None)

        def patched_api_call(agent_instance, api_kwargs, *args, **kwargs):
            prompt = _extract_prompt(api_kwargs)
            if prompt:
                try:
                    category = triage_router.tier1_triage(prompt)
                    print(f"[AIOS WebUI Triage] category={category}", file=sys.stderr)
                    if category in _CODING_CATEGORIES:
                        print("[AIOS WebUI Triage] → agy_start (non-stream)", file=sys.stderr)
                        return _synthetic_response(prompt)
                except Exception as _e:
                    print(f"[AIOS WebUI Triage] triage error: {_e}", file=sys.stderr)
            return original_api_call(agent_instance, api_kwargs, *args, **kwargs)

        def patched_streaming(agent_instance, api_kwargs, *args, **kwargs):
            prompt = _extract_prompt(api_kwargs)
            if prompt:
                try:
                    category = triage_router.tier1_triage(prompt)
                    print(f"[AIOS WebUI Triage] stream category={category}", file=sys.stderr)
                    if category in _CODING_CATEGORIES:
                        print("[AIOS WebUI Triage] → agy_start (stream)", file=sys.stderr)
                        return _synthetic_stream(prompt)
                except Exception as _e:
                    print(f"[AIOS WebUI Triage] triage stream error: {_e}", file=sys.stderr)
            return original_streaming(agent_instance, api_kwargs, *args, **kwargs)

        helpers.interruptible_api_call = patched_api_call
        if original_streaming:
            helpers.interruptible_streaming_api_call = patched_streaming

        print("[AIOS WebUI Triage] All patches installed ✓", file=sys.stderr)

    except Exception as _e:
        print(f"[AIOS WebUI Triage] interruptible patch failed: {_e}", file=sys.stderr)


# ── Meta-path hook: fires when agent.* is first imported ──────────────────────
# Python 3.4+ only calls find_spec — find_module is never invoked.
# We return None (let normal import proceed) but fire patches as a side effect.

class _TriageInstallHook:
    """Fires _apply_all_patches the moment any agent.* module is imported."""

    def find_spec(self, fullname, path, target=None):
        if fullname in ("agent.chat_completion_helpers", "agent.auxiliary_client",
                        "agent.agent_init"):
            try:
                sys.meta_path.remove(self)
            except ValueError:
                pass
            _apply_all_patches()
        return None  # always let normal import machinery handle it


sys.meta_path.append(_TriageInstallHook())
print("[AIOS WebUI Triage] Hook registered — waiting for agent import", file=sys.stderr)
