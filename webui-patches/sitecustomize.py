"""
Hermes WebUI - AI-OS Triage Interceptor
========================================
This sitecustomize.py is auto-loaded by Python at startup when this directory
is on PYTHONPATH (set via the hermes-webui .env). It monkey-patches
agent.chat_completion_helpers.interruptible_api_call and
interruptible_streaming_api_call to intercept coding prompts and route them
through agy via a synthetic agy_start tool call response -- identical in logic
to aios_hermes_wrapper.py used by the TUI.
"""
import sys
import os
import json
import time as _time

_AIOS_SCRIPTS = "/Users/matt/projects/ai-os/scripts"
_PATCHED = False


def _install_patch():
    global _PATCHED
    if _PATCHED:
        return

    # Only patch when we're in the Hermes WebUI server process (not during unit
    # tests, bootstrap argument parsing, etc). We detect this by checking if
    # the hermes-agent path is on sys.path -- config.py adds it before imports.
    has_agent = any("hermes-agent" in p or "hermes_agent" in p for p in sys.path)
    if not has_agent:
        return

    try:
        if _AIOS_SCRIPTS not in sys.path:
            sys.path.insert(0, _AIOS_SCRIPTS)

        import triage_router
        import agent.chat_completion_helpers as helpers

        original_api_call = helpers.interruptible_api_call
        original_streaming_api_call = getattr(helpers, "interruptible_streaming_api_call", None)

        def _extract_prompt(api_kwargs):
            messages = api_kwargs.get("messages", [])
            if not messages:
                return ""
            last_msg = messages[-1]
            if isinstance(last_msg, dict):
                content = last_msg.get("content", "")
            else:
                content = getattr(last_msg, "content", "")
            if isinstance(content, list):
                parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                content = " ".join(parts)
            return str(content)

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

        def _synthetic_response(prompt):
            tc_id = f"call_agy_{int(_time.time())}"
            return _AttrDict({
                "id": f"chatcmpl-triage-{int(_time.time())}",
                "object": "chat.completion",
                "created": int(_time.time()),
                "model": "triage-interceptor",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Delegating task to agy.",
                        "tool_calls": [{
                            "id": tc_id,
                            "type": "function",
                            "function": {
                                "name": "agy_start",
                                "arguments": json.dumps({"PROMPT": str(prompt)}),
                            },
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
            })

        def _synthetic_stream(prompt):
            tc_id = f"call_agy_{int(_time.time())}"
            args_json = json.dumps({"PROMPT": str(prompt)})
            base_id = f"chatcmpl-triage-{int(_time.time())}"
            created = int(_time.time())

            yield _AttrDict({
                "id": base_id, "object": "chat.completion.chunk",
                "created": created, "model": "triage-interceptor",
                "choices": [{"index": 0, "delta": {
                    "role": "assistant", "content": "Delegating task to agy.",
                    "tool_calls": [{"index": 0, "id": tc_id, "type": "function",
                                    "function": {"name": "agy_start", "arguments": ""}}],
                }, "finish_reason": None}],
            })
            yield _AttrDict({
                "id": base_id, "object": "chat.completion.chunk",
                "created": created, "model": "triage-interceptor",
                "choices": [{"index": 0, "delta": {
                    "tool_calls": [{"index": 0, "function": {"arguments": args_json}}],
                }, "finish_reason": None}],
            })
            yield _AttrDict({
                "id": base_id, "object": "chat.completion.chunk",
                "created": created, "model": "triage-interceptor",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
            })

        _CODING_CATEGORIES = {"coding_standard", "coding_complex", "valve_boilerplate"}

        def patched_api_call(agent_instance, api_kwargs, *args, **kwargs):
            prompt = _extract_prompt(api_kwargs)
            if prompt:
                try:
                    category = triage_router.tier1_triage(prompt)
                    print(f"[AIOS WebUI Triage] category={category}", file=sys.stderr)
                    if category in _CODING_CATEGORIES:
                        print("[AIOS WebUI Triage] Intercepting → agy_start", file=sys.stderr)
                        return _synthetic_response(prompt)
                except Exception as e:
                    print(f"[AIOS WebUI Triage] triage error: {e}", file=sys.stderr)
            return original_api_call(agent_instance, api_kwargs, *args, **kwargs)

        def patched_streaming_api_call(agent_instance, api_kwargs, *args, **kwargs):
            prompt = _extract_prompt(api_kwargs)
            if prompt:
                try:
                    category = triage_router.tier1_triage(prompt)
                    print(f"[AIOS WebUI Triage] stream category={category}", file=sys.stderr)
                    if category in _CODING_CATEGORIES:
                        print("[AIOS WebUI Triage] Intercepting stream → agy_start", file=sys.stderr)
                        return _synthetic_stream(prompt)
                except Exception as e:
                    print(f"[AIOS WebUI Triage] triage stream error: {e}", file=sys.stderr)
            return original_streaming_api_call(agent_instance, api_kwargs, *args, **kwargs)

        helpers.interruptible_api_call = patched_api_call
        if original_streaming_api_call:
            helpers.interruptible_streaming_api_call = patched_streaming_api_call

        _PATCHED = True
        print("[AIOS WebUI Triage] Patch installed on agent.chat_completion_helpers", file=sys.stderr)

    except ImportError:
        # agent module not yet on path — will be applied lazily via import hook
        _register_lazy_hook()
    except Exception as e:
        print(f"[AIOS WebUI Triage] sitecustomize error: {e}", file=sys.stderr)


def _register_lazy_hook():
    """
    Register a meta_path finder that re-tries patching when 'agent' package
    is first imported. This handles the case where sitecustomize runs before
    the hermes-agent path has been added to sys.path by config.py.
    """
    class _TriageHook:
        def find_module(self, fullname, path=None):
            if fullname == "agent.chat_completion_helpers":
                return self
            return None

        def load_module(self, fullname):
            import importlib
            sys.meta_path.remove(self)
            mod = importlib.import_module(fullname)
            # Now that agent is loaded, apply the patch
            _install_patch()
            return mod

    sys.meta_path.append(_TriageHook())


# Run at import time (which is Python startup via PYTHONPATH-sitecustomize trick)
_install_patch()
