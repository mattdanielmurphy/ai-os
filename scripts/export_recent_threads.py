#!/usr/bin/env python3
"""
export_recent_threads.py — Collect and rename Antigravity thread.md files from the past month.

Scans brain directories across ~/.gemini/antigravity, ~/.gemini/antigravity-cli, and ~/.gemini/antigravity-ide,
resolves the conversation titles from protobuf summaries / json metadata / transcripts,
and saves renamed markdown files to docs/antigravity-threads/.
"""

import os
import sys
import json
import re
import shutil
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
DEFAULT_OUTPUT_DIR = Path("/Users/matt/projects/ai-os/docs/antigravity-threads")
BRAIN_DIRS = [
    Path.home() / ".gemini/antigravity/brain",
    Path.home() / ".gemini/antigravity-cli/brain",
    Path.home() / ".gemini/antigravity-ide/brain",
]
PB_PATH = Path.home() / ".gemini/antigravity/agyhub_summaries_proto.pb"


def load_pb_titles() -> dict[str, str]:
    titles = {}
    if not PB_PATH.exists():
        return titles

    data = PB_PATH.read_bytes()
    i = 0
    while i < len(data):
        tag = data[i]
        if tag != 0x0A:
            break
        i += 1
        l = 0
        s = 0
        while True:
            b = data[i]
            i += 1
            l |= (b & 0x7F) << s
            if not (b & 0x80):
                break
            s += 7
        chunk = data[i : i + l]
        i += l

        try:
            idx = 0
            if chunk[idx] == 0x0A:
                idx += 1
                l1 = 0
                s1 = 0
                while True:
                    b = chunk[idx]
                    idx += 1
                    l1 |= (b & 0x7F) << s1
                    if not (b & 0x80):
                        break
                    s1 += 7
                cid = chunk[idx : idx + l1].decode("utf-8")
                idx += l1
                if idx < len(chunk) and chunk[idx] == 0x12:
                    idx += 1
                    l2 = 0
                    s2 = 0
                    while True:
                        b = chunk[idx]
                        idx += 1
                        l2 |= (b & 0x7F) << s2
                        if not (b & 0x80):
                            break
                        s2 += 7
                    sub_bytes = chunk[idx : idx + l2]
                    if sub_bytes and sub_bytes[0] == 0x0A:
                        s_idx = 1
                        lt = 0
                        ss = 0
                        while True:
                            b = sub_bytes[s_idx]
                            s_idx += 1
                            lt |= (b & 0x7F) << ss
                            if not (b & 0x80):
                                break
                            ss += 7
                        title = sub_bytes[s_idx : s_idx + lt].decode("utf-8")
                        titles[cid] = title.strip()
        except Exception:
            pass

    return titles


def load_json_summaries() -> dict[str, str]:
    summaries = {}
    for p in [
        Path.home() / ".gemini/antigravity/brain/thread_summaries.json",
        Path.home() / ".gemini/antigravity-cli/brain/thread_summaries.json",
    ]:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v_clean = re.sub(r"^\[Gemini\]\s*", "", str(v)).strip()
                        summaries[k] = v_clean
            except Exception:
                pass
    return summaries


def sanitize_filename(title: str, max_len: int = 60) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', title).strip().lower()
    cleaned = re.sub(r'[-\s]+', '-', cleaned)
    cleaned = cleaned.strip('-')
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip('-')
    return cleaned or "conversation"


def extract_clean_transcript_md(transcript_path: Path, title: str, conv_id: str, date_str: str) -> str:
    """Extract plain markdown prompts and responses directly from transcript.jsonl."""
    turns = []
    current_user = []
    current_assistant = []

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue

                step_type = obj.get("type")
                content = obj.get("content", "")

                if step_type == "USER_INPUT":
                    if current_assistant:
                        turns.append(("Assistant", "\n\n".join(current_assistant)))
                        current_assistant = []
                    
                    m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, flags=re.DOTALL)
                    prompt_text = m.group(1).strip() if m else content.strip()
                    
                    prompt_text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", prompt_text, flags=re.DOTALL)
                    prompt_text = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", prompt_text, flags=re.DOTALL)
                    prompt_text = prompt_text.strip()
                    
                    if prompt_text and not prompt_text.startswith("You are a specialized subagent"):
                        current_user.append(prompt_text)

                elif step_type == "PLANNER_RESPONSE":
                    if current_user:
                        turns.append(("User", "\n\n".join(current_user)))
                        current_user = []
                    
                    if content and content.strip():
                        clean_content = re.sub(r"<THREAD_NAME>.*?</THREAD_NAME>", "", content).strip()
                        clean_content = re.sub(r'\[`?thread\.md`?\]\([^\)]*\)', '', clean_content)
                        if clean_content.strip():
                            current_assistant.append(clean_content.strip())

        if current_user:
            turns.append(("User", "\n\n".join(current_user)))
        if current_assistant:
            turns.append(("Assistant", "\n\n".join(current_assistant)))

    except Exception:
        pass

    if not turns:
        return ""

    md_lines = [
        "---",
        f'title: "{title}"',
        f'date: "{date_str}"',
        f'conversation_id: "{conv_id}"',
        'source: "antigravity"',
        "---",
        "",
        f"# {title}",
        "",
    ]

    for role, text in turns:
        md_lines.append(f"## {role}\n")
        md_lines.append(f"{text}\n")
        md_lines.append("---\n")

    return "\n".join(md_lines)


def export_threads(days: int = 31, output_dir: Path = DEFAULT_OUTPUT_DIR) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    output_dir.mkdir(parents=True, exist_ok=True)

    pb_titles = load_pb_titles()
    json_summaries = load_json_summaries()

    print(f"Scanning for conversations active since {cutoff.strftime('%Y-%m-%d')} (past {days} days)...")

    convs = {}
    for b_dir in BRAIN_DIRS:
        if not b_dir.exists():
            continue
        for d in b_dir.iterdir():
            if not d.is_dir() or d.is_symlink() or d.name.startswith("."):
                continue
            conv_id = d.name
            if conv_id in convs:
                continue

            t_file = d / ".system_generated/logs/transcript.jsonl"
            th_file = d / "thread.md"

            last_dt = None
            first_prompt = ""
            thread_name_tag = ""
            is_subagent = False
            step_count = 0

            if t_file.exists():
                try:
                    with open(t_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if not line.strip():
                                continue
                            step_count += 1
                            obj = json.loads(line)
                            ca = obj.get("created_at")
                            if ca:
                                dt = datetime.fromisoformat(ca.replace("Z", "+00:00"))
                                if dt.tzinfo is None:
                                    dt = dt.replace(tzinfo=timezone.utc)
                                if last_dt is None or dt > last_dt:
                                    last_dt = dt
                            if obj.get("type") == "USER_INPUT" and not first_prompt:
                                c = obj.get("content", "")
                                m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", c, flags=re.DOTALL)
                                prompt_text = m.group(1).strip() if m else c.strip()
                                first_prompt = prompt_text
                                if (
                                    "You are a specialized subagent" in prompt_text
                                    or "A clear, actionable task description" in prompt_text
                                    or "You are tasked with" in prompt_text
                                    or obj.get("source") == "SUBAGENT"
                                ):
                                    is_subagent = True
                            if obj.get("type") == "PLANNER_RESPONSE" and not thread_name_tag:
                                c = obj.get("content", "")
                                m = re.search(r"<THREAD_NAME>(.*?)</THREAD_NAME>", c)
                                if m:
                                    thread_name_tag = m.group(1).strip()
                except Exception:
                    pass

            if last_dt is None and th_file.exists():
                last_dt = datetime.fromtimestamp(th_file.stat().st_mtime, tz=timezone.utc)

            if last_dt and last_dt >= cutoff and not is_subagent and (step_count > 0 or th_file.exists()):
                title = pb_titles.get(conv_id) or json_summaries.get(conv_id) or thread_name_tag
                if not title and first_prompt:
                    first_line = first_prompt.split("\n")[0].strip()
                    title = first_line[:70]
                if not title:
                    title = f"Conversation {conv_id[:8]}"

                title = re.sub(r'[\r\n]+', ' ', title).strip()

                convs[conv_id] = {
                    "conv_id": conv_id,
                    "date": last_dt,
                    "title": title,
                    "dir": d,
                    "has_thread_md": th_file.exists() and th_file.stat().st_size > 100,
                    "th_file": th_file,
                    "t_file": t_file,
                }

    print(f"Found {len(convs)} user conversations from the past {days} days.")

    from sanitize_thread import SecretSanitizer
    sanitizer = SecretSanitizer()

    exported = 0
    for conv_id, info in convs.items():
        date_str = info["date"].strftime("%Y-%m-%d")
        title = info["title"]
        slug = sanitize_filename(title)
        filename = f"{date_str}-{slug}--[{conv_id[:8]}].md"
        target_path = output_dir / filename

        content = ""
        if info["has_thread_md"]:
            raw_thread = info["th_file"].read_text(encoding="utf-8", errors="ignore")
            if not raw_thread.startswith("---"):
                header = (
                    f"---\n"
                    f'title: "{title}"\n'
                    f'date: "{date_str}"\n'
                    f'conversation_id: "{conv_id}"\n'
                    f'source: "antigravity"\n'
                    f"---\n\n"
                )
                content = header + raw_thread
            else:
                content = raw_thread
        elif info["t_file"].exists():
            content = extract_clean_transcript_md(info["t_file"], title, conv_id, date_str)

        if content:
            sanitized_res = sanitizer.sanitize_content(content)
            target_path.write_text(sanitized_res.cleaned_text, encoding="utf-8")
            exported += 1

    print(f"[SUCCESS] Exported {exported} sanitized conversation markdown files to {output_dir}")
    return exported


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export recent Antigravity threads to markdown")
    parser.add_argument("--days", type=int, default=31, help="Number of days back to collect (default: 31)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Destination directory")
    args = parser.parse_args()

    export_threads(days=args.days, output_dir=args.output_dir)
