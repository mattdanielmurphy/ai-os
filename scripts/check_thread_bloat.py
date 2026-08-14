#!/usr/bin/env python3
import os
import sys
import glob
import json
import argparse
from pathlib import Path

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    try:
        import tiktoken
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return int(len(encoding.encode(text)))
        except Exception:
            pass
    except ImportError:
        pass
    return int(max(1, len(text) // 3.5))

def count_file_tokens(filepath: Path) -> int:
    try:
        if filepath.exists() and filepath.is_file():
            content = filepath.read_text(errors="ignore")
            return estimate_tokens(content)
    except Exception:
        pass
    return 0

def get_sys_prompt_tokens(project_root: Path):
    home = Path.home()
    
    # 1. Rules files
    rules_tokens = 0
    scanned_rules_files = set()
    
    gemini_candidates = [
        project_root / "GEMINI.md",
        project_root / "AGENTS.md",
        home / "projects/ai-os/GEMINI.md",
        home / "projects/ai-os/AGENTS.md",
        home / "GEMINI.md",
    ]
    for p in gemini_candidates:
        if p.exists() and str(p.resolve()) not in scanned_rules_files:
            rules_tokens += count_file_tokens(p)
            scanned_rules_files.add(str(p.resolve()))
            break

    rules_dirs = [project_root / ".rules", home / "projects/ai-os/.rules"]
    for r_dir in rules_dirs:
        if r_dir.exists() and r_dir.is_dir():
            for f in r_dir.glob("*.md"):
                if str(f.resolve()) not in scanned_rules_files:
                    rules_tokens += count_file_tokens(f)
                    scanned_rules_files.add(str(f.resolve()))

    # 2. Skill files
    skills_tokens = 0
    skill_paths = set(glob.glob(str(home / ".gemini/config/skills/**/SKILL.md"), recursive=True))
    skill_paths.update(glob.glob(str(home / ".gemini/config/plugins/**/SKILL.md"), recursive=True))
    skill_paths.update(glob.glob(str(home / ".gemini/antigravity/builtin/skills/**/SKILL.md"), recursive=True))
    for sp in skill_paths:
        try:
            content = Path(sp).read_bytes()[:2048].decode("utf-8", errors="ignore")
            if "---" in content:
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    fm = parts[1]
                    name = Path(sp).parent.name
                    desc = ""
                    for line in fm.split("\n"):
                        l = line.strip()
                        if l.startswith("name:"):
                            name = l.split("name:", 1)[1].strip().strip("\"'")
                        elif l.startswith("description:"):
                            desc = l.split("description:", 1)[1].strip().strip("\"'")
                    skills_tokens += estimate_tokens(f"- {name} ({sp}): {desc}\n")
        except Exception:
            pass

    # 3. MCP Schemas
    mcp_tokens = 3200
    
    # 4. AG_CONTEXT.md
    ag_context_tokens = 0
    ag_context_candidates = [project_root / "AG_CONTEXT.md", home / "projects/ai-os/AG_CONTEXT.md"]
    for ag_p in ag_context_candidates:
        if ag_p.exists():
            ag_context_tokens = count_file_tokens(ag_p)
            break
            
    base_system_tokens = 3500
    t_sys = base_system_tokens + rules_tokens + skills_tokens + mcp_tokens + ag_context_tokens
    
    breakdown = {
        "base_system_tokens": base_system_tokens,
        "rules_tokens": rules_tokens,
        "skills_tokens": skills_tokens,
        "mcp_tokens": mcp_tokens,
        "ag_context_tokens": ag_context_tokens,
    }
    return t_sys, breakdown

def extract_step_text(step: dict) -> str:
    step_type = step.get("type")
    content = step.get("content") or ""
    thinking = step.get("thinking") or ""
    tool_calls = step.get("tool_calls") or []
    
    parts = []
    if step_type == "USER_INPUT":
        parts.append(content)
    elif step_type in ("CONVERSATION_HISTORY", "SYSTEM_MESSAGE", "KNOWLEDGE_ARTIFACTS"):
        parts.append(content)
    elif step_type == "PLANNER_RESPONSE":
        if thinking:
            parts.append(thinking)
        if tool_calls:
            for tc in tool_calls:
                name = tc.get("name", "")
                args = tc.get("arguments") or tc.get("args") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                parts.append(f"{name} {json.dumps(args)}")
        if content:
            parts.append(content)
    elif content:
        parts.append(content)
        
    return "\n".join(parts)

def find_transcript_file(conv_id=None, explicit_transcript=None):
    if explicit_transcript and os.path.exists(explicit_transcript):
        return explicit_transcript

    home = Path.home()
    if conv_id:
        p = home / f".gemini/antigravity/brain/{conv_id}/.system_generated/logs/transcript.jsonl"
        if p.exists():
            return str(p)
            
    env_conv_id = os.environ.get("CONVERSATION_ID") or os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if env_conv_id:
        p = home / f".gemini/antigravity/brain/{env_conv_id}/.system_generated/logs/transcript.jsonl"
        if p.exists():
            return str(p)

    # Auto-detect latest transcript
    brain_dir = home / ".gemini/antigravity/brain"
    if brain_dir.exists():
        matches = glob.glob(str(brain_dir / "**/.system_generated/logs/transcript.jsonl"), recursive=True)
        if matches:
            matches.sort(key=os.path.getmtime, reverse=True)
            return matches[0]
            
    return None

def get_transcript_tokens(transcript_path: str) -> int:
    if not transcript_path or not os.path.exists(transcript_path):
        return 0

    t_hist = 0
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    step = json.loads(line)
                    text = extract_step_text(step)
                    t_hist += estimate_tokens(text)
                except Exception:
                    pass
    except Exception:
        pass
    return t_hist

def main():
    parser = argparse.ArgumentParser(description="Evaluate economic thread bloat status.")
    parser.add_argument("--conv-id", "-c", help="Conversation ID")
    parser.add_argument("--transcript", "-t", help="Path to transcript.jsonl")
    parser.add_argument("--project-root", "-p", default=os.getcwd(), help="Project root directory")
    parser.add_argument("--R", type=float, default=4.0, help="Ratio constant R (default: 4.0)")
    parser.add_argument("--S", type=float, default=1000.0, help="Compaction overhead constant S (default: 1000)")
    parser.add_argument("--M", type=float, default=5.0, help="Compaction factor constant M (default: 5.0)")
    parser.add_argument("--json-compact", "-j", action="store_true", help="Print compact JSON")
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root)
    t_sys, sys_breakdown = get_sys_prompt_tokens(project_root)
    
    transcript_path = find_transcript_file(conv_id=args.conv_id, explicit_transcript=args.transcript)
    t_hist = get_transcript_tokens(transcript_path)
    
    R = args.R
    S = args.S
    M = args.M
    
    # Formula: T_hist_threshold = S + ((R - 1) / M) * (T_sys + S)
    t_hist_threshold = round(S + ((R - 1.0) / M) * (t_sys + S), 2)
    is_bloated = t_hist > t_hist_threshold
    
    result = {
        "t_sys": t_sys,
        "t_hist": t_hist,
        "t_hist_threshold": t_hist_threshold,
        "is_bloated": is_bloated,
        "T_sys": t_sys,
        "T_hist": t_hist,
        "T_hist_threshold": t_hist_threshold,
        "breakdown": {
            "sys_base_tokens": sys_breakdown.get("base_system_tokens", 0),
            "sys_rules_tokens": sys_breakdown.get("rules_tokens", 0),
            "sys_skills_tokens": sys_breakdown.get("skills_tokens", 0),
            "sys_mcp_tokens": sys_breakdown.get("mcp_tokens", 0),
            "sys_context_tokens": sys_breakdown.get("ag_context_tokens", 0),
            "R": R,
            "S": S,
            "M": M
        },
        "transcript_path": transcript_path
    }
    
    if args.json_compact:
        print(json.dumps(result))
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
