#!/usr/bin/env python3
"""
tool_guard.py - PreToolUse Hard Guardrail Engine for Codex.

Provides deterministic enforcement for AI-OS safety invariants:
  1. Destructive Shell Commands: Blocks 'rm' / 'rmdir' (instructs 'mv <path> ~/.Trash/').
  2. Secret File Isolation: Blocks reads/prints of .env, *credentials*, private keys.
  3. Tooling Policy: Blocks npm, pnpm, yarn (instructs 'bun').
  4. Home Directory Git Guard: Blocks 'git init ~' in home root.
  5. System Temp Guard: Blocks writes/creates in system /tmp (instructs ./tmp).
  6. Bare Container Guard: Blocks creating loose files directly in ~/projects/.

Supports Shadow Mode (logs violations without blocking) and Enforce Mode (hard halts).
"""

import os
import sys
import json
import shlex
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

CODEX_DIR = Path.home() / ".codex"
CONFIG_FILE = CODEX_DIR / "hooks_config.json"
AUDIT_LOG_FILE = CODEX_DIR / "hooks_audit.log"

HOME_DIR = str(Path.home().resolve())
PROJECTS_ROOT = str((Path.home() / "projects").resolve())

# Secret filename patterns
SECRET_PATTERNS = [
    re.compile(r"(^|/)\.env(\.[a-zA-Z0-9_-]+)?$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]*credentials[^/]*$", re.IGNORECASE),
    re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)(|\.pub)$", re.IGNORECASE),
    re.compile(r"(^|/)[^/]*\.(pem|key|p12|pfx)$", re.IGNORECASE),
]

# Destructive command tokens
DESTRUCTIVE_COMMANDS = {"rm", "rmdir"}

# Tooling command tokens
FORBIDDEN_TOOLING = {"npm", "pnpm", "yarn"}


def get_hook_mode() -> str:
    """Returns 'shadow', 'enforce', or 'disabled'."""
    if os.environ.get("CODEX_HOOKS_SHADOW") == "1":
        return "shadow"
    if os.environ.get("CODEX_HOOKS_DISABLED") == "1":
        return "disabled"
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mode", "enforce")
        except Exception:
            pass
    return "enforce"


def log_audit_event(event_type: str, violation: str, tool_name: str, tool_input: Any, cwd: str, blocked: bool):
    """Logs security audit events to ~/.codex/hooks_audit.log."""
    try:
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event": event_type,
            "blocked": blocked,
            "violation": violation,
            "tool_name": tool_name,
            "cwd": cwd,
            "tool_input": tool_input,
        }
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass


def split_pipeline_commands(cmd_str: str) -> List[List[str]]:
    """Splits shell command chains (;, &&, ||, |) into lists of individual argument tokens."""
    # Simple regex split on chain operators
    segments = re.split(r"(?:&&|\|\||;|\||\n)", cmd_str)
    token_lists = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
            if tokens:
                token_lists.append(tokens)
        except Exception:
            # Fallback whitespace split if shlex fails on syntax error
            parts = seg.split()
            if parts:
                token_lists.append(parts)
    return token_lists


def check_destructive_commands(tokens: List[str]) -> Optional[str]:
    """Inspects tokens for rm/rmdir invocations."""
    if not tokens:
        return None

    cmd = Path(tokens[0]).name.lower()
    if cmd in DESTRUCTIVE_COMMANDS:
        # Check node_modules exception
        args = tokens[1:]
        is_node_modules = any("node_modules" in a for a in args)
        if is_node_modules:
            return None
        return (
            "AI-OS Guardrail Violation: 'rm' and 'rmdir' are strictly prohibited. "
            "You MUST use 'mv <path> ~/.Trash/' instead (Exception: node_modules)."
        )
    return None


def check_secret_file_access(command_str: str, tokens: List[str]) -> Optional[str]:
    """Inspects commands for reading/dumping raw secret files."""
    if not tokens:
        return None

    cmd = Path(tokens[0]).name.lower()
    # Reading tools: cat, head, tail, less, more, source, ., grep, view_file
    read_tools = {"cat", "head", "tail", "less", "more", "source", ".", "grep", "rg", "bat", "open"}

    # Allowed safe tooling
    if "aios-env" in command_str:
        return None

    # Check if any token looks like a secret file being targeted
    for token in tokens[1:]:
        clean_token = token.strip("\"' ")
        for pattern in SECRET_PATTERNS:
            if pattern.search(clean_token):
                if cmd in read_tools or len(tokens) == 2:
                    return (
                        f"AI-OS Secret Isolation Violation: Access to raw secret file '{clean_token}' is blocked. "
                        "Never inspect or print raw secret files. Use 'aios-env check --key <KEY>' or 'aios-env list' instead."
                    )
    return None


def check_tooling_policy(tokens: List[str]) -> Optional[str]:
    """Inspects tokens for npm, pnpm, yarn."""
    if not tokens:
        return None

    cmd = Path(tokens[0]).name.lower()
    if cmd in FORBIDDEN_TOOLING:
        return (
            f"AI-OS Tooling Policy Violation: '{cmd}' is prohibited. "
            "ALWAYS use 'bun' instead (e.g. 'bun install', 'bun add <pkg>', 'bun run <script>')."
        )
    return None


def check_home_git_init(tokens: List[str], cwd: str) -> Optional[str]:
    """Inspects tokens for git init or git clone in ~."""
    if not tokens:
        return None

    cmd = Path(tokens[0]).name.lower()
    if cmd == "git" and len(tokens) > 1 and tokens[1] == "init":
        target = tokens[2] if len(tokens) > 2 else "."
        abs_target = str(Path(cwd, target).resolve()) if cwd else target
        if abs_target in (HOME_DIR, "/Users/matt", "/Users/matthewmurphy"):
            return (
                "AI-OS Safety Violation: NEVER initialize a git repository directly in the home root directory (~). "
                "Standalone repositories must reside in dedicated subdirectories (e.g. ~/projects/<project-name>)."
            )
    return None


def check_system_tmp_write(command_str: str) -> Optional[str]:
    """Inspects for redirection or creation in /tmp instead of ./tmp."""
    # Match output redirection to /tmp/ or /tmp
    if re.search(r">\s*/tmp(/|\s|\Z)", command_str) or re.search(r"\b(mkdir|touch|tee)\s+(-\w+\s+)*/tmp/", command_str):
        # Exclude benign /tmp access like reading or sockets
        return (
            "AI-OS Environment Violation: NEVER use system-level /tmp for temporary files or scripts. "
            "ALWAYS create and use a ./tmp folder within the current project directory."
        )
    return None


def check_bare_projects_container(command_str: str, cwd: str) -> Optional[str]:
    """Inspects for creating loose files directly inside ~/projects/ instead of a project subfolder."""
    clean_cwd = str(Path(cwd).resolve()) if cwd else ""
    if clean_cwd == PROJECTS_ROOT:
        # If in ~/projects bare folder, block file creation commands
        if re.search(r"\b(touch|echo|cat|cp|mv)\b.*>", command_str) or re.search(r"\b(touch|git init)\s+[a-zA-Z0-9_.-]+", command_str):
            # Check if creating a file directly (e.g. touch script.py) rather than a folder
            parts = command_str.split()
            if len(parts) >= 2 and "." in parts[-1] and not parts[-1].startswith("-"):
                return (
                    "AI-OS Target Folder Violation: Do not create files directly in generic parent container ~/projects/. "
                    "Create a dedicated project subdirectory and place all new files inside."
                )
    return None


def evaluate_command_string(command_str: str, cwd: str) -> Optional[str]:
    """Evaluates a raw shell command string against all security policies."""
    commands = split_pipeline_commands(command_str)
    for tokens in commands:
        violation = check_destructive_commands(tokens)
        if violation:
            return violation

        violation = check_secret_file_access(command_str, tokens)
        if violation:
            return violation

        violation = check_tooling_policy(tokens)
        if violation:
            return violation

        violation = check_home_git_init(tokens, cwd)
        if violation:
            return violation

    violation = check_system_tmp_write(command_str)
    if violation:
        return violation

    violation = check_bare_projects_container(command_str, cwd)
    if violation:
        return violation

    return None


def evaluate_file_tool(tool_name: str, tool_input: Any, cwd: str) -> Optional[str]:
    """Inspects file viewing/editing tool arguments for secret isolation and temp rules."""
    path_val = None
    if isinstance(tool_input, dict):
        for key in ["path", "target_file", "TargetFile", "file", "filename", "uri", "AbsolutePath"]:
            if key in tool_input and isinstance(tool_input[key], str):
                path_val = tool_input[key]
                break
    elif isinstance(tool_input, str):
        path_val = tool_input

    if not path_val:
        return None

    # Secret file check
    for pattern in SECRET_PATTERNS:
        if pattern.search(path_val):
            return (
                f"AI-OS Secret Isolation Violation: Access to raw secret file '{path_val}' is blocked. "
                "Never inspect or read raw secret files. Use 'aios-env check --key <KEY>' or 'aios-env list' instead."
            )

    # System /tmp write check
    if tool_name in ["write_to_file", "replace_file_content", "create_file"] and path_val.startswith("/tmp/"):
        return (
            "AI-OS Environment Violation: NEVER write files to system-level /tmp. "
            "ALWAYS create and use a ./tmp folder within the current project directory."
        )

    return None


def evaluate_tool_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main PreToolUse policy evaluator.
    Returns compliant Wire format for Codex Rust hook engine.
    """
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", "")
    mode = get_hook_mode()

    if mode == "disabled":
        return {
            "continue": True,
            "decision": "approve",
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }

    violation: Optional[str] = None

    # 1. Shell commands (execute_command, Bash, bash, sh, zsh, terminal)
    if any(k in tool_name.lower() for k in ["command", "bash", "sh", "exec", "terminal"]):
        cmd_str = ""
        if isinstance(tool_input, dict):
            for key in ["command", "cmd", "CommandLine", "script"]:
                if key in tool_input and isinstance(tool_input[key], str):
                    cmd_str = tool_input[key]
                    break
        elif isinstance(tool_input, str):
            cmd_str = tool_input

        if cmd_str:
            violation = evaluate_command_string(cmd_str, cwd)

    # 2. File operations (view_file, read_file, write_to_file, replace_file_content)
    if not violation and any(k in tool_name.lower() for k in ["file", "view", "read", "write", "replace"]):
        violation = evaluate_file_tool(tool_name, tool_input, cwd)

    # If violation detected
    if violation:
        if mode == "shadow":
            # Shadow mode: log would-be block but approve
            log_audit_event("PRE_TOOL_USE_SHADOW_VIOLATION", violation, tool_name, tool_input, cwd, blocked=False)
            return {
                "continue": True,
                "decision": "approve",
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow"
                }
            }
        else:
            # Enforce mode: HARD BLOCK
            log_audit_event("PRE_TOOL_USE_BLOCKED", violation, tool_name, tool_input, cwd, blocked=True)
            return {
                "continue": False,
                "decision": "block",
                "reason": violation,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": violation
                }
            }

    # Safe tool call: Approve
    return {
        "continue": True,
        "decision": "approve",
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow"
        }
    }
