#!/Users/matt/.hermes/hermes-agent/venv/bin/python
import sys
import os
import json
import time
from types import SimpleNamespace

# Add ai-os scripts for triage router
sys.path.insert(0, "/Users/matt/projects/ai-os/scripts")
import triage_router

# Add hermes to path if not already there, just in case
hermes_path = "/Users/matt/.hermes/hermes-agent"
if hermes_path not in sys.path:
    sys.path.insert(0, hermes_path)

import agent.chat_completion_helpers as helpers

original_interruptible_api_call = helpers.interruptible_api_call
original_interruptible_streaming_api_call = getattr(helpers, 'interruptible_streaming_api_call', None)

def extract_prompt(api_kwargs):
    messages = api_kwargs.get("messages", [])
    if not messages:
        return ""
    last_msg = messages[-1]
    
    # Try to extract content safely whether it's a dict or object
    if isinstance(last_msg, dict):
        content = last_msg.get("content", "")
    else:
        content = getattr(last_msg, "content", "")
        
    if isinstance(content, list):
        # Flatten content if it's a list (e.g., multimodal)
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        content = " ".join(text_parts)
        
    return str(content)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = AttrDict(value)
            elif isinstance(value, list):
                self[key] = [AttrDict(x) if isinstance(x, dict) else x for x in value]
    def model_dump(self, *args, **kwargs):
        def _dump(obj):
            if isinstance(obj, AttrDict):
                return {k: _dump(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_dump(v) for v in obj]
            return obj
        return _dump(self)

def create_synthetic_response(prompt):
    tool_call_id = f"call_agy_{int(time.time())}"
    function_args = json.dumps({"PROMPT": str(prompt)})
    
    return AttrDict({
        "id": f"chatcmpl-triage-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "triage-interceptor",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Delegating task to agy.",
                "tool_calls": [{
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "agy_start",
                        "arguments": function_args
                    }
                }]
            },
            "finish_reason": "tool_calls"
        }]
    })

def create_synthetic_stream(prompt):
    tool_call_id = f"call_agy_{int(time.time())}"
    function_args = json.dumps({"PROMPT": str(prompt)})
    base_id = f"chatcmpl-triage-{int(time.time())}"
    created = int(time.time())
    
    # Chunk 1: The tool call ID and name
    yield AttrDict({
        "id": base_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": "triage-interceptor",
        "choices": [{
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": "Delegating task to agy.",
                "tool_calls": [{
                    "index": 0,
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "agy_start",
                        "arguments": ""
                    }
                }]
            },
            "finish_reason": None
        }]
    })

    # Chunk 2: The tool call arguments
    yield AttrDict({
        "id": base_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": "triage-interceptor",
        "choices": [{
            "index": 0,
            "delta": {
                "tool_calls": [{
                    "index": 0,
                    "function": {
                        "arguments": function_args
                    }
                }]
            },
            "finish_reason": None
        }]
    })

    # Chunk 3: The finish reason
    yield AttrDict({
        "id": base_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": "triage-interceptor",
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "tool_calls"
        }]
    })

def patched_api_call(agent_instance, api_kwargs, *args, **kwargs):
    prompt = extract_prompt(api_kwargs)
    if prompt:
        category = triage_router.tier1_triage(prompt)
        print(f"[Hermes Triage] Intercepted prompt category: {category}", file=sys.stderr)
        
        if category in ["coding_standard", "coding_complex", "valve_boilerplate"]:
            print("[Hermes Triage] Faking LLM response to force agy_start tool call.", file=sys.stderr)
            return create_synthetic_response(prompt)
    
    return original_interruptible_api_call(agent_instance, api_kwargs, *args, **kwargs)

def patched_streaming_api_call(agent_instance, api_kwargs, *args, **kwargs):
    prompt = extract_prompt(api_kwargs)
    if prompt:
        category = triage_router.tier1_triage(prompt)
        print(f"[Hermes Triage] Intercepted stream prompt category: {category}", file=sys.stderr)
        
        if category in ["coding_standard", "coding_complex", "valve_boilerplate"]:
            print("[Hermes Triage] Faking streaming LLM response to force agy_start tool call.", file=sys.stderr)
            return create_synthetic_stream(prompt)
            
    return original_interruptible_streaming_api_call(agent_instance, api_kwargs, *args, **kwargs)

# Apply patches
helpers.interruptible_api_call = patched_api_call
if original_interruptible_streaming_api_call:
    helpers.interruptible_streaming_api_call = patched_streaming_api_call
else:
    # Handle if hermes streaming is in another module or name
    pass

import hermes_cli.main
if __name__ == "__main__":
    hermes_cli.main.main()
