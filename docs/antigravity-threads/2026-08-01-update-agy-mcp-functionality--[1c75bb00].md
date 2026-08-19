---
title: "Update Agy MCP Functionality"
date: "2026-08-01"
conversation_id: "1c75bb00-ce7c-4539-bd26-c9018cdf0f9f"
source: "antigravity"
---

# Update Agy MCP Functionality

## User

Please update the agy-mcp package files to add support for model parameters and improve tmux job spawning reliability.

Target Files:
1. /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/adapters/agy.py
- Add a static method `_parse_model_flags(model_str: str) -> list[str]` to `AgyPrintBackend`:
```python
    @staticmethod
    def _parse_model_flags(model_str: str) -> list[str]:
        if not model_str or not model_str.strip():
            return []

        m_raw = model_str.strip()
        m_lower = m_raw.lower()

        effort = None
        if m_lower.endswith("-low") or "(low)" in m_lower:
            effort = "low"
        elif m_lower.endswith("-medium") or "(medium)" in m_lower:
            effort = "medium"
        elif m_lower.endswith("-high") or "(high)" in m_lower:
            effort = "high"

        if "3.6-flash" in m_lower or "3.6 flash" in m_lower or "gemini-3.6" in m_lower:
            return ["--model", "gemini-3.6-flash", "--effort", effort or "low"]

        if "3.5-flash" in m_lower or "3.5 flash" in m_lower or "gemini-3.5" in m_lower:
            return ["--model", "gemini-3.5-flash", "--effort", effort or "low"]

        if "3.1-pro" in m_lower or "3.1 pro" in m_lower or "gemini-3.1" in m_lower:
            return ["--model", "gemini-3.1-pro", "--effort", effort or "low"]

        if "sonnet" in m_lower:
            return ["--model", "Claude Sonnet 4.6 (Thinking)"]

        if "opus" in m_lower:
            return ["--model", "Claude Opus 4.6 (Thinking)"]

        if "gpt-oss" in m_lower or "oss" in m_lower:
            return ["--model", "GPT-OSS 120B (Medium)"]

        if "(" in m_raw and ")" in m_raw:
            return ["--model", m_raw]

        if effort:
            clean_model = re.sub(r"-(low|medium|high)$", "", m_raw, flags=re.IGNORECASE).strip()
            clean_model = re.sub(r"\s*\((low|medium|high)\)$", "", clean_model, flags=re.IGNORECASE).strip()
            return ["--model", clean_model, "--effort", effort]

        return ["--model", m_raw]
```
- In `AgyPrintBackend.build_command`:
Add logic right after checking `cap.supports_print`:
```python
        if request.model:
            argv.extend(self._parse_model_flags(request.model))
```

2. /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py
- In `agy_tool` and `agy_continue_tool`:
Ensure `session_id` matches `job_` prefix if not already (e.g. `session_id = request.session_id if (request.session_id and request.session_id.startswith("job_")) else (f"job_{request.session_id}" if request.session_id else f"job_{uuid.uuid4().hex[:8]}")`).
Update the tmux spawn execution:
```python
    try:
        res = subprocess.run(popen_arg, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            err = res.stderr.strip() or res.stdout.strip() or f"exit code {res.returncode}"
            return _structured_failure(safety, RuntimeError(f"tmux spawn failed: {err}"), cwd=cd)
    except OSError as exc:
        return _structured_failure(safety, exc, cwd=cd)

    try:
        store = _ensure_state()[2]
        store.create_job(
            job_id=session_id,
            session_id=session_id,
            cwd=cd,
            request=request.model_dump(mode="json"),
            backend="agy",
        )
    except FileExistsError:
        pass
    except Exception:
        pass
```

3. /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/bridge.py
- Update the help text for `--model` to: `"Optional model override for backends that support model flags (agy and gemini)."`

---

## Assistant

Created At: 2026-07-31T21:21:51-06:00
Completed At: 2026-07-31T21:21:51-06:00
File Path: `file:///Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/adapters/agy.py`
Total Lines: 1156
Total Bytes: 44114
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: """AgyPrintBackend — wraps Google Antigravity CLI (`agy --print`).
2: 
3: Strategy (see docs/output-strategy.md for the full rationale):
4: 
5: 1. Spawn ``agy --print <prompt> --print-timeout <dur> --log-file <tmp>
6:    [--conversation <id> | --continue] [--sandbox]`` with stdout/stderr piped.
7: 2. Three concurrent readers:
8:    - **stdout**: agy prints the final assistant text once at the end (no
9:      token streaming). Buffer it; emit one ``assistant/text`` event when
10:      the process exits.
11:    - **klog tail of --log-file**: emit lifecycle events on the fly.
12:    - **transcript.jsonl watcher** (optional, best-effort): pass through
13:      any subagent NDJSON the CLI writes.
14: 3. On exit, emit ``result/success`` or ``result/error`` with timing /
15:    exit code / extracted conversation_id.
16: """
17: 
18: from __future__ import annotations
19: 
20: import json
21: import os
22: import re
23: import stat
24: import subprocess
25: import threading
26: import time
27: from dataclasses import dataclass
28: from pathlib import Path
29: 
30: from agy_mcp.adapters.base import (
31:     _MAX_LINE_BYTES,
32:     AdapterRunResult,
33:     BaseAdapter,
34:     EventSink,
35:     _drain_stream,
36:     _process_group_kwargs,
37:     _RunContext,
38:     _shutdown_cascade,
39:     has_flag,
40:     resolve_cwd,
41: )
42: from agy_mcp.models import BackendName, BridgeRequest, CanonicalEvent, Capability
43: from agy_mcp.utils import (
44:     augment_path_env_for_windows,
45:     is_windows,
46:     prepare_subproces
<truncated 32928 bytes>
# Two-pass: extract the body, then parse key=value pairs from it.
753:         # Tolerates extra/missing fields between agy versions.
754:         body = m.group("body")
755:         kv = {
756:             pair.group("k"): (pair.group("qv") if pair.group("qv") is not None else pair.group("rv"))
757:             for pair in _RE_PRINT_START_KV.finditer(body)
758:         }
759:         try:
760:             prompt_len = int(kv.get("promptLength", "0"))
761:         except ValueError:
762:             prompt_len = 0
763:         model = kv.get("model") or None
764:         sid = kv.get("conversationID") or None
765:         if sid:
766:             with ctx.lock:
767:                 ctx.seen_session_id[0] = sid
768:         adapter._emit(
769:             ctx,
770:             CanonicalEvent(
771:                 type="system",
772:                 subtype="print_starting",
773:                 session_id=sid,
774:                 metadata={"prompt_length": prompt_len, "model": model, "fields": kv},
775:             ),
776:         )
777:         return
778:     if m := _RE_NEW_CONV.search(msg):
779:         adapter._emit(
780:             ctx,
781:             CanonicalEvent(
782:                 type="system",
783:                 subtype="turn_start",
784:                 metadata={"agent_mode": m.group(1) == "true"},
785:             ),
786:         )
787:         return
788:     if m := _RE_AUTO_FLUSH.search(msg):
789:         adapter._emit(
790:             ctx,
791:             CanonicalEvent(
792:                 type="user",
793:                 subtype="input_flush",
794:                 metadata={
795:                     "input_count": int(m.group(1)),
796:                     "combined_chars": int(m.group(2)),
797:                     "media": int(m.group(3)),
798:                 },
799:             ),
800:         )
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T21:21:52-06:00
Completed At: 2026-07-31T21:21:52-06:00
File Path: `file:///Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py`
Total Lines: 1258
Total Bytes: 46141
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: """FastMCP server exposing the agy-mcp toolkit over stdio.
2: 
3: Tools (all return dicts with stable keys; never raise across the wire):
4: 
5: * ``agy`` — synchronous one-shot bridge call.
6: * ``agy_start`` — spawn a background job, return ``status="running"`` envelope.
7: * ``agy_continue`` — like ``agy``, but ``SESSION_ID`` is required.
8: * ``agy_status`` — poll a running job's :class:`JobRecord`.
9: * ``agy_read`` — read events from a job (raw or translated).
10: * ``agy_result`` — fetch captured output for a finished job.
11: * ``agy_cancel`` — signal a running job to stop.
12: * ``agy_sessions`` — list recent jobs.
13: * ``agy_doctor`` — environment + capability probe.
14: * ``agy_install_skill`` — write the scaffold skill into target dirs.
15: 
16: Threading model: the FastMCP runtime drives tools from an asyncio loop and
17: calls sync tool functions inline. ``agy`` and ``agy_continue`` would block
18: that loop while ``_bridge_run`` waits on a subprocess, so they are declared
19: ``async def`` and dispatch the blocking work to a worker thread via
20: :func:`anyio.to_thread.run_sync` (Phase 5 R1 arch P1.1).
21: 
22: Every tool routes its output through :class:`SafetyPolicy` before
23: serialisation — adapter buffers, capability warnings, and error strings
24: have already been scrubbed by the lower layers, but the doctor / install
25: helpers also redact their own paths so a transcript capture never leaks
26: a ``/Users/<user>/`` path.
27: """
28: 
29: from __future__ import annotations
30: 
31: im
<truncated 30763 bytes>
)
760:     except Exception as exc:  # noqa: BLE001
761:         return _structured_failure(safety, exc, cwd=cd)
762:     if job_id is not None:
763:         err = _validate_job_id(safety, job_id)
764:         if err is not None:
765:             return _structured_failure(safety, ValueError(err), cwd=cd)
766:     try:
767:         response = supervisor.start(request, job_id=job_id)
768:     except Exception as exc:  # noqa: BLE001 - top-level guard
769:         return _structured_failure(safety, exc, cwd=cd)
770:     return response
771: 
772: 
773: # ---------------------------------------------------------------------------
774: # Tool: agy_status — poll a job's JobRecord
775: # ---------------------------------------------------------------------------
776: 
777: 
778: @mcp.tool(
779:     name="agy_status",
780:     description="Return the JobRecord (status, exit code, error, timestamps) for a job_id.",
781: )
782: def agy_status_tool(job_id: str) -> StatusToolResponse:
783:     config, safety, _store_, supervisor = _ensure_state()
784:     err = _validate_job_id(safety, job_id)
785:     if err is not None:
786:         return _wrapper_failure(safety, ValueError(err), StatusToolResponse)
787:     try:
788:         record = supervisor.status(job_id)
789:     except Exception as exc:  # noqa: BLE001
790:         return _wrapper_failure(safety, exc, StatusToolResponse)
791:     if record is None:
792:         # Use the same envelope shape as other failures so consumers can
793:         # rely on ``success/error`` keys regardless of why the lookup
794:         # failed. (Phase 5 R1 arch P1.3)
795:         return _wrapper_failure(
796:             safety,
797:             ValueError(f"job_id {job_id!r} not found"),
798:             StatusToolResponse,
799:         )
800:     return StatusToolResponse(success=True, record=record)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T21:21:53-06:00
Completed At: 2026-07-31T21:21:53-06:00
File Path: `file:///Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/bridge.py`
Total Lines: 633
Total Bytes: 23982
Showing lines 1 to 633
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: """Bridge CLI — the entry point skills shell out to.
2: 
3: Responsibilities:
4: 
5: 1. Parse argv into a :class:`BridgeRequest`.
6: 2. Load :class:`Config` (config.toml + env-var overrides) and apply
7:    per-call defaults (worktree, allow_write, backend, output_protocol).
8: 3. Apply :meth:`SafetyPolicy.gate_request` — deny on destructive prompts,
9:    reject write-mode without explicit ``--allow-write``, etc.
10: 4. Route to ``AgyPrintBackend`` or ``GeminiCliBackend`` (auto chooses
11:    first available; explicit backend errors fast if unavailable).
12: 5. Optionally create a git worktree (execute + allow_write +
13:    worktree_default OR --worktree explicit). Successful write runs leave
14:    the worktree in place for review and merge.
15: 6. Run the adapter, translate events via :class:`ProtocolTranslator`,
16:    and emit a :class:`BridgeResponse` JSON envelope on stdout.
17: 
18: The CLI never crashes the user-facing layer: errors land in a
19: ``BridgeResponse(success=False, error=...)`` so skills get a stable JSON
20: shape regardless of failure mode.
21: """
22: 
23: from __future__ import annotations
24: 
25: import argparse
26: import json
27: import re
28: import sys
29: import tempfile
30: import traceback
31: import uuid
32: from pathlib import Path
33: 
34: from agy_mcp.adapters import (
35:     BaseAdapter,
36:     ListEventSink,
37:     ProtocolTranslator,
38: )
39: from agy_mcp.config import Config, get_config
40: from agy_mcp.models import (
41:     AdapterMetadata,
42:     BridgeRequest,
43:     Bridge
<truncated 23514 bytes>
577:         SESSION_ID=request.session_id or "",
578:         status="completed",
579:         cwd=_response_cwd(safety, cwd),
580:         adapter=_adapter_meta(adapter, request, safety),
581:         command_preview=preview,
582:         warnings=warnings,
583:     ).touch()
584: 
585: 
586: # ---------------------------------------------------------------------------
587: # Helpers
588: # ---------------------------------------------------------------------------
589: 
590: 
591: def _with_cwd(request: BridgeRequest, new_cwd: Path) -> BridgeRequest:
592:     return request.model_copy(update={"cwd": str(new_cwd)})
593: 
594: 
595: def _adapter_meta(
596:     adapter: BaseAdapter,
597:     request: BridgeRequest,
598:     safety: SafetyPolicy,
599: ) -> AdapterMetadata:
600:     cap = adapter.detect()
601:     return AdapterMetadata(
602:         backend=cap.backend,
603:         bin_path=safety.redact(cap.bin_path) if cap.bin_path else None,
604:         version=cap.version,
605:         model=request.model or cap.model,
606:         output_protocol=request.output_protocol,
607:         supports_streaming=cap.supports_streaming,
608:         supports_tool_events=cap.supports_tool_events,
609:     )
610: 
611: 
612: def _pick_assistant_text(events: list[CanonicalEvent]) -> str:
613:     for event in reversed(events):
614:         if event.type == "assistant" and event.text:
615:             return event.text
616:     return ""
617: 
618: 
619: def _pick_error_text(events: list[CanonicalEvent]) -> str | None:
620:     for event in reversed(events):
621:         if event.type == "error" and event.text:
622:             return event.text
623:         if event.type == "result" and event.subtype not in ("success",) and event.text:
624:             return event.text
625:     return None
626: 
627: 
628: if __name__ == "__main__":  # pragma: no cover
629:     raise SystemExit(main(sys.argv[1:]))
630: 
631: 
632: __all__ = ["main"]
633: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:21:55-06:00
Completed At: 2026-07-31T21:21:55-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/adapters/agy.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -285,6 +285,8 @@
             argv.append("--sandbox")
         if request.dangerously_skip_permissions and cap.supports_dangerously_skip_permissions:
             argv.append("--dangerously-skip-permissions")
+        if request.model:
+            argv.extend(self._parse_model_flags(request.model))
         if request.session_id:
             if cap.supports_conversation:
                 # ``--conversation=<id>`` for the same reason as --print=
@@ -298,6 +298,50 @@
         return argv
 
     @staticmethod
+    def _parse_model_flags(model_str: str) -> list[str]:
+        if not model_str or not model_str.strip():
+            return []
+
+        m_raw = model_str.strip()
+        m_lower = m_raw.lower()
+
+        effort = None
+        if m_lower.endswith("-low") or "(low)" in m_lower:
+            effort = "low"
+        elif m_lower.endswith("-medium") or "(medium)" in m_lower:
+            effort = "medium"
+        elif m_lower.endswith("-high") or "(high)" in m_lower:
+            effort = "high"
+
+        if "3.6-flash" in m_lower or "3.6 flash" in m_lower or "gemini-3.6" in m_lower:
+            return ["--model", "gemini-3.6-flash", "--effort", effort or "low"]
+
+        if "3.5-flash" in m_lower or "3.5 flash" in m_lower or "gemini-3.5" in m_lower:
+            return ["--model", "gemini-3.5-flash", "--effort", effort or "low"]
+
+        if "3.1-pro" in m_lower or "3.1 pro" in m_lower or "gemini-3.1" in m_lower:
+            return ["--model", "gemini-3.1-pro", "--effort", effort or "low"]
+
+        if "sonnet" in m_lower:
+            return ["--model", "Claude Sonnet 4.6 (Thinking)"]
+
+        if "opus" in m_lower:
+            return ["--model", "Claude Opus 4.6 (Thinking)"]
+
+        if "gpt-oss" in m_lower or "oss" in m_lower:
+            return ["--model", "GPT-OSS 120B (Medium)"]
+
+        if "(" in m_raw and ")" in m_raw:
+            return ["--model", m_raw]
+
+        if effort:
+            clean_model = re.sub(r"-(low|medium|high)$", "", m_raw, flags=re.IGNORECASE).strip()
+            clean_model = re.sub(r"\s*\((low|medium|high)\)$", "", clean_model, flags=re.IGNORECASE).strip()
+            return ["--model", clean_model, "--effort", effort]
+
+        return ["--model", m_raw]
+
+    @staticmethod
     def _prepare_prompt(prompt: str) -> str:
         return windows_escape(prompt) if is_windows() else prompt
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T21:22:01-06:00
Completed At: 2026-07-31T21:22:01-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -510,7 +510,7 @@
         return _structured_failure(safety, exc, cwd=cd)
 
     import uuid, shlex, subprocess
-    session_id = request.session_id or f"job_{uuid.uuid4().hex[:8]}"
+    session_id = request.session_id if (request.session_id and request.session_id.startswith("job_")) else (f"job_{request.session_id}" if request.session_id else f"job_{uuid.uuid4().hex[:8]}")
     tmux_session = f"ai_os_agy_{session_id}"
 
     # We want agy to stay open in the tmux session so Hermes can attach to it.
@@ -540,9 +540,26 @@
     popen_arg = ["tmux", "new-session", "-d", "-s", tmux_session, "-c", str(Path(cd).expanduser().resolve()), "bash", "-c", debug_wrapper]
 
     try:
-        subprocess.run(popen_arg, check=False)
-    except OSError as exc:
-        return _structured_failure(safety, exc, cwd=cd)
+        res = subprocess.run(popen_arg, capture_output=True, text=True, check=False)
+        if res.returncode != 0:
+            err = res.stderr.strip() or res.stdout.strip() or f"exit code {res.returncode}"
+            return _structured_failure(safety, RuntimeError(f"tmux spawn failed: {err}"), cwd=cd)
+    except OSError as exc:
+        return _structured_failure(safety, exc, cwd=cd)
+
+    try:
+        store = _ensure_state()[2]
+        store.create_job(
+            job_id=session_id,
+            session_id=session_id,
+            cwd=cd,
+            request=request.model_dump(mode="json"),
+            backend="agy",
+        )
+    except FileExistsError:
+        pass
+    except Exception:
+        pass
 
     return BridgeResponse(
         success=True,
@@ -639,40 +639,57 @@
         return _structured_failure(safety, exc, cwd=cd)
<truncated 1913 bytes>
]
+    skip_next = False
+    for a in argv:
+        if skip_next:
+            skip_next = False
+            continue
+        if a == "--print-timeout":
+            skip_next = True
+            continue
+        if a.startswith("--print="):
+            interactive_argv.append(a.replace("--print=", "--prompt-interactive=", 1))
+        else:
+            interactive_argv.append(a)
+
+    tmux_cmd = " ".join(shlex.quote(a) for a in interactive_argv)
+    if "--dangerously-skip-permissions" not in tmux_cmd:
+        tmux_cmd += " --dangerously-skip-permissions"
+    if "--add-dir" not in tmux_cmd:
+        tmux_cmd += f" --add-dir={shlex.quote(str(cd))}"
+
+    # Add debugging: if agy crashes, keep the pane open so we can investigate.
+    debug_wrapper = f"{tmux_cmd} || {{ echo 'Agy crashed or stopped prematurely! Exit code: $?'; sleep 86400; }}"
+
+    popen_arg = ["tmux", "new-session", "-d", "-s", tmux_session, "-c", str(Path(cd).expanduser().resolve()), "bash", "-c", debug_wrapper]
+
+    try:
+        res = subprocess.run(popen_arg, capture_output=True, text=True, check=False)
+        if res.returncode != 0:
+            err = res.stderr.strip() or res.stdout.strip() or f"exit code {res.returncode}"
+            return _structured_failure(safety, RuntimeError(f"tmux spawn failed: {err}"), cwd=cd)
+    except OSError as exc:
+        return _structured_failure(safety, exc, cwd=cd)
+
+    try:
+        store = _ensure_state()[2]
+        store.create_job(
+            job_id=session_id,
+            session_id=session_id,
+            cwd=cd,
+            request=request.model_dump(mode="json"),
+            backend="agy",
+        )
+    except FileExistsError:
+        pass
+    except Exception:
+        pass
 
     return BridgeResponse(
         success=True,
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T21:22:02-06:00
Completed At: 2026-07-31T21:22:02-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/bridge.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -95,7 +95,7 @@
     p.add_argument("--model", default=None,
                    help=(
                        "Optional model override for backends that support "
-                       "model flags (currently gemini)."
+                       "model flags (agy and gemini)."
                    ))
     p.add_argument("--sandbox", action="store_true",
                    help="Pass --sandbox to the underlying CLI when supported.")
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T21:22:04-06:00
Completed At: 2026-07-31T21:22:04-06:00
Message sent to "5938612c-c640-4aa9-b6ef-4afbb050920a".

The `agy-mcp` package files have been updated according to your request.

*   **`adapters/agy.py`**: Added `_parse_model_flags` method to `AgyPrintBackend` to support model parameter parsing and integrated it into `build_command`.
*   **`server.py`**: Refined `agy_tool` and `agy_continue_tool` to enforce `job_` prefix for `session_id`, improved error handling for `tmux` subprocess execution, and added job state registration.
*   **`bridge.py`**: Updated the help text for the `--model` CLI argument.

---
