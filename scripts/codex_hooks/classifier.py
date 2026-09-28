#!/usr/bin/env python3
"""
classifier.py - Dynamic Intent & Context Classifier for UserPromptSubmit Hook.

Implements a 3-tier routing architecture:
  - Tier 0: Heuristic CWD & Casual Gate (< 2ms):
            Returns additionalContext: null for casual, projectless queries
            (e.g. "What is the best milk chocolate?"). Zero token overhead!
  - Tier 1: Project & Keyword Domain Slicer (5-15ms):
            Selects and injects pre-compiled policy packs from ~/.codex/policies/
            based on active workspace CWD and prompt intent.
  - Tier 2: Conditional Mem0 Semantic Recall (30-60ms):
            Retrieves durable user memories from local Mem0 vector database ONLY
            when personal preferences, setup history, or user context could matter.
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Set, List

CODEX_DIR = Path.home() / ".codex"
POLICIES_DIR = CODEX_DIR / "policies"
CONFIG_FILE = CODEX_DIR / "hooks_config.json"
PROJECTS_ROOT = (Path.home() / "projects").resolve()
DOCUMENTS_CODEX = (Path.home() / "Documents" / "Codex").resolve()

# Ephemeral / Casual prompt patterns
CASUAL_START_PATTERNS = re.compile(
    r"^(hi|hello|hey|yo|good morning|good evening|good afternoon|"
    r"what is|what's|what are|who is|who was|who are|where is|"
    r"how do i (cook|bake|make|clean|fix a non-tech)|recipe|"
    r"translate|summarize|explain the difference between|tell me about|"
    r"why is|why does|recommend a good|best milk chocolate|rules of|"
    r"how many|when was|which is better|can you rewrite this sentence)\b",
    re.IGNORECASE
)

# Trigger keywords for substantive policies
TRIGGER_KEYWORDS = {
    "git", "commit", "push", "branch", "rebase", "repo", "repository", "pull request", "pr",
    "remind", "reminder", "todo", "task", "schedule", "calendar", "call them", "follow-up",
    "music", "song", "album", "artist", "track", "playlist", "apple music",
    "student id", "ccid", "asn", "pen", "resume", "application", "form", "fill out", "sin", "dob",
    "css", "html", "styling", "layout", "span", "thread.md", "dom", "component", "ui",
    "secret", "key", "token", ".env", "credential", "auth", "password",
    "database", "postgres", "sql", "vps", "server", "host",
    "skill", "workflow", "subagent", "agy", "antigravity", "planner", "query_aios",
    "python", "bun", "npm", "bash", "zsh", "terminal", "code", "debug", "test", "build"
}

# Domain keywords to policy pack mapping
DOMAIN_POLICY_MAP = {
    "policy_reminders": {"remind", "reminder", "todo", "task", "schedule", "calendar", "call them", "follow-up", "apple-reminders"},
    "policy_music": {"music", "song", "album", "artist", "track", "playlist", "apple music", "itunes"},
    "policy_personal_ids": {"student id", "ccid", "asn", "pen", "resume", "application", "form", "fill out", "date of birth", "sin", "dob"},
    "policy_frontend": {"css", "html", "styling", "layout", "span", "thread.md", "dom", "component", "frontend", "ui/web"},
    "policy_database": {"database", "postgres", "sql", "vps", "provisioning", "db host"},
    "policy_skills_authoring": {"custom skill", "skill authoring", "skill.md", "sync_skills"},
    "policy_rules_engine": {"system directive", "permanent rule", "always do", "from now on", "build_rules"},
    "policy_agy_delegation": {"agy", "antigravity", "delegate", "planner", "query_aios", "high reasoning"},
}

# Memory recall trigger patterns
MEMORY_RECALL_PATTERNS = re.compile(
    r"\b(my setup|my preferences?|what do i prefer|how do i usually|remember|"
    r"my configuration|my workflow|remind me|personal vault|what's my|what is my|"
    r"my personal|past decision|last time)\b",
    re.IGNORECASE
)


def is_ephemeral_cwd(cwd_str: str) -> bool:
    """Checks if cwd is an ephemeral chat folder or outside projects."""
    if not cwd_str:
        return True
    try:
        p = Path(cwd_str).resolve()
        # Direct match for ~/Documents/Codex/...
        if DOCUMENTS_CODEX in p.parents or p == DOCUMENTS_CODEX:
            return True
        # If cwd is ~ or temporary scratch
        if p == Path.home() or "/.tmp" in str(p) or "/tmp" in str(p):
            return True
    except Exception:
        pass
    return False


def is_git_repository(cwd_str: str) -> bool:
    """Detects whether cwd is inside an active git workspace."""
    if not cwd_str:
        return False
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd_str,
            capture_output=True,
            text=True,
            timeout=1
        )
        return res.returncode == 0 and res.stdout.strip() == "true"
    except Exception:
        return False


def load_policy_pack(pack_name: str) -> str:
    """Reads a compiled policy pack from ~/.codex/policies/ or in-repo fallback."""
    pack_file = POLICIES_DIR / f"{pack_name}.md"
    if pack_file.exists():
        try:
            with open(pack_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    # In-repo fallback
    repo_pack_file = Path("/Users/matt/projects/ai-os/config/codex_policies") / f"{pack_name}.md"
    if repo_pack_file.exists():
        try:
            with open(repo_pack_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    return ""


def is_mem0_prompt_enabled() -> bool:
    """Checks hooks_config.json to see if Mem0 retrieval is enabled on prompt submission."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("enable_mem0_on_prompt", False))
        except Exception:
            pass
    return False


def retrieve_mem0_context(prompt: str) -> str:
    """Queries local Mem0 via aios_memory.py for relevant user facts."""
    try:
        current_script_dir = Path(__file__).resolve().parent.parent
        worktree_aios_memory = current_script_dir / "aios_memory.py"
        aios_memory_path = worktree_aios_memory if worktree_aios_memory.exists() else Path("/Users/matt/projects/ai-os/scripts/aios_memory.py")
        if not aios_memory_path.exists():
            return ""

        # Prefer hermes venv python where mem0 and dependencies are installed
        hermes_python = Path("/Users/matt/.hermes/hermes-agent/venv/bin/python")
        python_exec = str(hermes_python) if hermes_python.exists() else sys.executable

        # Run query with 2.5s timeout (within Codex 3.0s hook budget)
        res = subprocess.run(
            [python_exec, str(aios_memory_path), "prefetch", prompt],
            capture_output=True,
            text=True,
            timeout=2.5
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def classify_and_inject(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main UserPromptSubmit hook handler.
    Analyzes prompt and CWD, returning wire-compliant output with additionalContext.
    """
    prompt = payload.get("prompt", "").strip()
    cwd = payload.get("cwd", "")

    # Blank prompt fast exit
    if not prompt:
        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": None
            }
        }

    p_lower = prompt.lower()
    has_trigger_word = any(k in p_lower for k in TRIGGER_KEYWORDS)
    ephemeral = is_ephemeral_cwd(cwd)

    # ─────────────────────────────────────────────────────────────
    # TIER 0: Heuristic Casual / Ephemeral Gate (< 2ms)
    # ─────────────────────────────────────────────────────────────
    if ephemeral and not has_trigger_word:
        # Zero extra overhead for casual queries
        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": None
            }
        }

    # If prompt clearly matches casual conversational phrasing and has no triggers
    if CASUAL_START_PATTERNS.search(prompt) and not has_trigger_word and len(prompt) < 150:
        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": None
            }
        }

    # ─────────────────────────────────────────────────────────────
    # TIER 1: Project & Intent Policy Slicer (5-15ms)
    # ─────────────────────────────────────────────────────────────
    selected_packs: Set[str] = set()

    # If inside an active git workspace, include git & dev workflow
    if is_git_repository(cwd):
        selected_packs.add("policy_git")
        selected_packs.add("policy_dev_workflow")

    # Match domain trigger keywords
    for pack_name, keywords in DOMAIN_POLICY_MAP.items():
        if any(kw in p_lower for kw in keywords):
            selected_packs.add(pack_name)

    # Collect policy pack texts
    context_chunks: List[str] = []
    for pack in sorted(list(selected_packs)):
        content = load_policy_pack(pack)
        if content:
            context_chunks.append(f"<!-- {pack} -->\n{content}")

    # ─────────────────────────────────────────────────────────────
    # TIER 2: Conditional Mem0 Semantic Recall (Cold: ~2.0s, Warm: ~1.8s)
    # ─────────────────────────────────────────────────────────────
    # Only retrieve from Mem0 if explicitly enabled in hooks_config.json AND user asked for preferences/setup
    if is_mem0_prompt_enabled():
        if MEMORY_RECALL_PATTERNS.search(prompt) or "policy_reminders" in selected_packs:
            mem0_block = retrieve_mem0_context(prompt)
            if mem0_block:
                context_chunks.append(mem0_block)

    # Assemble final additionalContext string
    if not context_chunks:
        additional_context = None
    else:
        header = "=== AI-OS DYNAMIC DEVELOPER CONTEXT (JIT POLICY) ==="
        footer = "=== END DYNAMIC CONTEXT ==="
        body = "\n\n".join(context_chunks)
        # Cap total injected length at 4,000 characters to prevent prompt bloat
        if len(body) > 4000:
            body = body[:4000] + "\n...[truncated dynamic policy context]"
        additional_context = f"{header}\n\n{body}\n\n{footer}"

    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context
        }
    }
