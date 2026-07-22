#!/usr/bin/env python3
"""
Background Review Extractor
Reads a session's transcript.jsonl, uses a fast LLM (Gemini Flash) to extract
durable facts, user preferences, and skill learnings, then saves candidate items
to ~/.gemini/staging_memories/ for the Meta-Curator to process.
"""

import os
import sys
import json
import glob
import datetime
from pathlib import Path

def extract_transcript_digest(transcript_path, max_events=35):
    """Parses transcript.jsonl into a concise turn digest."""
    if not os.path.exists(transcript_path):
        return ""

    events = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    step_type = data.get("type")
                    content = data.get("content") or ""
                    
                    if step_type == "USER_INPUT" and content:
                        events.append(f"USER: {content[:400]}")
                    elif data.get("tool_calls"):
                        tool_names = [tc.get("name") or (tc.get("function") or {}).get("name", "?") 
                                     for tc in data.get("tool_calls", []) if isinstance(tc, dict)]
                        events.append(f"ASSISTANT [tools: {', '.join(tool_names)}]")
                        if content and len(content) > 10:
                            events.append(f"ASSISTANT: {content[:200]}")
                except Exception:
                    continue
    except Exception as e:
        print(f"Error reading transcript {transcript_path}: {e}", file=sys.stderr)
        return ""

    # Return the tail max_events
    recent = events[-max_events:] if len(events) > max_events else events
    return "\n".join(recent)

def run_extraction(transcript_path, project_root):
    digest = extract_transcript_digest(transcript_path)
    if not digest:
        print("No transcript digest available for review.")
        return

    # Check for LiteLLM or Google API keys to run background extraction
    # We create a lightweight JSON candidate payload
    staging_dir = Path.home() / ".gemini" / "staging_memories"
    staging_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate_file = staging_dir / f"candidate_{timestamp}.json"

    prompt = f"""Review this conversation transcript digest and extract learning signals:

TRANSCRIPT DIGEST:
{digest}

Target signals:
1. USER PREFERENCES: Style, tone, verbosity, workflow constraints ("don't format like X", "prefer Y").
2. DURABLE FACTS: Project architecture, tools used, environment quirks.
3. SKILL CANDIDATES: Non-trivial fix, workaround, or workflow pattern that would help future sessions.

Write output as JSON with keys: 'user_preferences', 'durable_facts', 'skill_candidates'.
If nothing notable occurred, set arrays to empty.
"""

    try:
        # Import litellm dynamically if available
        import litellm
        model = os.environ.get("BACKGROUND_REVIEW_MODEL", "gemini/gemini-2.5-flash")
        
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        
        result_text = response.choices[0].message.content
        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        data = json.loads(result_text)
        data["project_root"] = project_root
        data["timestamp"] = timestamp
        data["transcript_path"] = transcript_path

        with open(candidate_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Extraction complete. Candidate saved to {candidate_file}")

    except Exception as e:
        print(f"Background review extraction notice: {e}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/background_review.py <transcript_path> [project_root]")
        sys.exit(1)

    transcript_path = sys.argv[1]
    project_root = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    run_extraction(transcript_path, project_root)

if __name__ == "__main__":
    main()
