#!/usr/bin/env python3
"""
compile_dynamic_prompt.py - Dynamic System Prompt Compiler for ai-os

Assembles a minimal, tailored system prompt based on role (orchestrator vs leaf),
platform, and active rule toggles from config/rules_config.json.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
RULES_DIR = PROJECT_ROOT / ".rules"
CONFIG_PATH = PROJECT_ROOT / "config" / "rules_config.json"

def load_rules_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load {CONFIG_PATH}: {e}", file=sys.stderr)
    return {"rules": {}, "settings": {}}

def apply_rule_filters(content: str, config: dict) -> str:
    rules = config.get("rules", {})
    settings = config.get("settings", {})

    # Filter out disabled rule blocks
    for rule_id, rule_info in rules.items():
        tag = rule_info.get("tag")
        if not tag:
            continue
        is_enabled = rule_info.get("enabled", True)
        pattern = rf"<!--\s*RULE:{tag}\s*-->[\s\S]*?<!--\s*/RULE:{tag}\s*-->\n*"
        if not is_enabled:
            content = re.sub(pattern, "", content)
        else:
            # Strip the comment tags but keep the content
            content = re.sub(rf"<!--\s*RULE:{tag}\s*-->\n?", "", content)
            content = re.sub(rf"<!--\s*/RULE:{tag}\s*-->\n?", "", content)

    # Clean up any leftover unmatched RULE tags if any exist
    content = re.sub(r"<!--\s*/?RULE:[A-Z0-9_]+\s*-->\n?", "", content)

    # Dynamic settings interpolation
    high_reasoning_setting = settings.get("high_reasoning_model_default", {}).get("value", "grok")
    if high_reasoning_setting == "grok":
        engine_str = "`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model grok` (ai-os Grok Thinking) by default, with `Gemini 3.8 Flash (High)` as a fallback"
    elif high_reasoning_setting == "perplexity":
        engine_str = "`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity` (ai-os Perplexity) by default, with `Gemini 3.8 Flash (High)` as a fallback"
    elif high_reasoning_setting == "flash_high":
        engine_str = "`Gemini 3.8 Flash (High)` via `agymcp`"
    elif high_reasoning_setting == "sonnet":
        engine_str = "`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model sonnet` (ai-os Sonnet Thinking)"
    elif high_reasoning_setting in ["gemini", "gemini_flash", "flash"]:
        engine_str = "`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model gemini` (ai-os Gemini Flash Thinking) by default, with `Gemini 3.8 Flash (High)` as a fallback"
    else:
        engine_str = str(high_reasoning_setting)

    content = content.replace("{HIGH_REASONING_ENGINE}", engine_str)

    # Clean up excessive blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()

def read_rule(name: str, config: dict) -> str:
    path = RULES_DIR / f"{name}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            return apply_rule_filters(raw, config)
    return ""

def compile_stub(platform: str = "antigravity") -> str:
    return """# Antigravity Dynamic Context Stub
Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
"""

def detect_active_domains(workspace_root: Path, prompt_text: str = "") -> set:
    domains = set()
    p_lower = prompt_text.lower()

    # 1. Inspect prompt keywords
    if any(k in p_lower for k in ["ui", "css", "html", "react", "vue", "web", "frontend", "span", "thread.md"]):
        domains.add("ui_web")
    if any(k in p_lower for k in ["hammerspoon", "lua", "midi", "hotkey", "window", "axui"]):
        domains.add("hammerspoon")
    if any(k in p_lower for k in ["audio", "webaudio", "oscillator", "dsp", "sound", "synth"]):
        domains.add("audio")
    if any(k in p_lower for k in ["ios", "swift", "xcode", "apple", "reminders"]):
        domains.add("ios")

    # 2. Inspect workspace root & git files
    if workspace_root and workspace_root.exists():
        r_name = workspace_root.name.lower()
        if "hammerspoon" in r_name or "midi" in r_name:
            domains.add("hammerspoon")
        if "ios" in r_name or "swift" in r_name:
            domains.add("ios")
        if "audio" in r_name or "sound" in r_name:
            domains.add("audio")

    return domains

def compile_minimal_codex_prompt() -> str:
    return """# AI-OS Global Codex Instructions

## 1. Identity & Environment Baseline
- **User**: Matthew Daniel Murphy (Matt) | `matt@mattmurphy.ca` | America/Edmonton (MST/MDT)
- **Environment**: macOS Apple Silicon | Default shell: `zsh` | Package manager: `bun`
- **Path Guardrail**: Host migrated from `/Users/matthewmurphy/` to `/Users/matt/`. Always use `/Users/matt/`.
- **Model Family Naming**: Refer to model families by clean canonical brand names (Sonnet, Flash, Opus, Haiku, Gemini, GPT) without speculative version numbers.

## 2. Dynamic Policy Runtime Notice
- AI-OS employs dynamic environment hooks (`UserPromptSubmit` and `PreToolUse`).
- Project protocols (Git tracking, agent logs), personal context (reminders, IDs), and domain styling are injected on-demand into developer context per turn.
- Hard safety constraints (secret file isolation, trash vs. `rm`, `bun` enforcement) are actively intercepted and enforced at the execution boundary. Always follow dynamically supplied context and gate feedback.

## 3. macOS Orchestration & Delegation
- ChatGPT/Codex on macOS is Matt's daily conversational surface and dispatcher.
- For substantive engineering tasks requiring sustained multi-step planning or autonomous coding, prefer delegating to Antigravity (`agymcp:agy`) when quota is healthy.
- Keep casual queries, factual Q&A, and quick rewrites direct in Codex. Keep task handoffs to `agy` thin and verbatim.
"""

def extract_markdown_sections(text: str) -> dict:
    """Split markdown text into sections by heading (# and ##)."""
    sections = {}
    current_key = "header"
    current_lines = []
    
    for line in text.split("\n"):
        if re.match(r"^#{1,2}\s+", line):
            if current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = re.sub(r"^#{1,2}\s+", "", line).strip()
            current_lines = [line]
        else:
            current_lines.append(line)
            
    if current_lines:
        sections[current_key] = "\n".join(current_lines).strip()
    return sections

def compile_codex_policy_packs(output_dir: Path = None) -> dict:
    """
    Extracts modular policy packs from .rules/ for the Codex dynamic hook engine.
    Writes policy packs to output_dir if provided, and returns the dictionary of packs.
    """
    config = load_rules_config()
    core_safety_raw = read_rule("core_safety", config)
    git_proto_raw = read_rule("git_protocol", config)
    agent_logs_raw = read_rule("agent_logs", config)
    codex_only_raw = read_rule("codex_only", config)
    ui_web_raw = read_rule("ui_web", config)
    
    cs_sections = extract_markdown_sections(core_safety_raw)

    def find_cs(*keywords):
        for k, v in cs_sections.items():
            if any(kw.lower() in k.lower() for kw in keywords):
                return v
        return ""

    packs = {}

    # 1. policy_git: Project detection & Git protocol
    packs["policy_git"] = "\n\n".join(filter(None, [
        find_cs("Project Detection"),
        git_proto_raw
    ])).strip()

    # 2. policy_reminders: Apple Reminders protocol
    packs["policy_reminders"] = find_cs("Apple Reminders", "Personal To-Dos").strip()

    # 3. policy_music: Music recommendations & Apple Music links
    packs["policy_music"] = find_cs("Music Recommendations").strip()

    # 4. policy_personal_ids: Zero-placeholder personal context
    packs["policy_personal_ids"] = find_cs("Zero-Placeholder Policy").strip()

    # 5. policy_frontend: Non-destructive UI styling & span-only layouts
    packs["policy_frontend"] = "\n\n".join(filter(None, [
        find_cs("Architectural Preservation"),
        ui_web_raw
    ])).strip()

    # 6. policy_agy_delegation: Thin handoff, quota modeling, planner dispatch
    packs["policy_agy_delegation"] = "\n\n".join(filter(None, [
        codex_only_raw,
        find_cs("Strict Planner"),
        find_cs("Transparent Model Escalation")
    ])).strip()

    # 7. policy_database: VPS database infrastructure
    db_match = re.search(r"(\d+\.\s*\*\*Shared Infrastructure Database[\s\S]*?)(?=\n\n|\n##|\n#|\Z)", core_safety_raw)
    packs["policy_database"] = (db_match.group(1).strip() if db_match else "- Matt maintains a VPS with a hosted database used across various projects. When database provisioning is required for projects/services, consider/leverage the VPS database rather than defaulting strictly to external third-party managed database platforms.")

    # 8. policy_skills_authoring: Custom skill conventions
    packs["policy_skills_authoring"] = find_cs("Custom Skills Naming").strip()

    # 9. policy_rules_engine: Rule persistence and build_rules.py
    packs["policy_rules_engine"] = find_cs("Proactive System Directive").strip()

    # 10. policy_dev_workflow: Work logs, project board, search-to-memory, LLM wiki
    packs["policy_dev_workflow"] = "\n\n".join(filter(None, [
        agent_logs_raw,
        find_cs("Search-to-Memory"),
        find_cs("Personal Knowledge Base")
    ])).strip()

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in packs.items():
            file_path = output_dir / f"{name}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")

    return packs

def compile_prompt(role: str = "orchestrator", platform: str = "antigravity", prompt_text: str = "", stub: bool = False, workspace_root: Path = None, minimal: bool = True) -> str:
    if stub and role.lower() != "leaf":
        return compile_stub(platform)

    # For Codex / ChatGPT, default to the minimal, hook-backed instructions
    if platform.lower() in ("codex", "chatgpt") and minimal and role.lower() != "leaf":
        return compile_minimal_codex_prompt()

    config = load_rules_config()
    sections = []
    
    # Always include core safety
    core_safety = read_rule("core_safety", config)
    if core_safety:
        sections.append(core_safety)

    if role.lower() == "leaf":
        leaf_path = Path("/Users/matt/.gemini/config/rules/03-subagent.md")
        if leaf_path.exists():
            with open(leaf_path, "r", encoding="utf-8") as f:
                sections.append(apply_rule_filters(f.read().strip(), config))
        return "\n\n".join(sections)

    # Orchestrator mode: add protocols
    git_proto = read_rule("git_protocol", config)
    if git_proto:
        sections.append(git_proto)

    agent_logs = read_rule("agent_logs", config)
    if agent_logs:
        sections.append(agent_logs)

    # Platform specific rules
    if platform.lower() == "antigravity":
        gemini_rules = read_rule("gemini_only", config)
        if gemini_rules:
            sections.append(gemini_rules)
    elif platform.lower() == "claude":
        claude_rules = read_rule("claude_only", config)
        if claude_rules:
            sections.append(claude_rules)
    elif platform.lower() == "hermes":
        hermes_rules = read_rule("hermes_only", config)
        if hermes_rules:
            sections.append(hermes_rules)
    elif platform.lower() in ("codex", "chatgpt"):
        codex_rules = read_rule("codex_only", config)
        if codex_rules:
            sections.append(codex_rules)

    # Dynamic domain rules
    active_domains = detect_active_domains(workspace_root or PROJECT_ROOT, prompt_text)
    for domain in sorted(list(active_domains)):
        domain_rule = read_rule(domain, config)
        if domain_rule:
            sections.append(domain_rule)

    return "\n\n".join(sections)

def main():
    parser = argparse.ArgumentParser(description="Dynamic System Prompt Compiler")
    parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
    parser.add_argument("--platform", default="antigravity", choices=["antigravity", "claude", "hermes", "codex", "agy"], help="Target platform")
    parser.add_argument("--prompt", default="", help="User prompt string for keyword matching")

    args = parser.parse_args()
    compiled = compile_prompt(args.role, args.platform, args.prompt, workspace_root=Path.cwd())
    print(compiled)

if __name__ == "__main__":
    main()
