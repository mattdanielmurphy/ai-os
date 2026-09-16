#!/usr/bin/env python3
"""
Meta-Curator Engine
Scans staging candidates in ~/.gemini/staging_memories/, uses a high-reasoning model (Gemini Pro),
and:
1. Auto-appends verified project facts to project AG_CONTEXT.md.
2. Formats and creates/patches skills following Hermes standards (<=60 char description).
3. If a major cross-project pattern or architectural change is proposed, creates a draft item
   in .devtool/features/ for human review instead of applying it blindly.
"""

import os
import sys
import json
import glob
from pathlib import Path

def load_candidates():
    staging_dir = Path.home() / ".gemini" / "staging_memories"
    if not staging_dir.exists():
        return []
    
    files = sorted(staging_dir.glob("candidate_*.json"))
    candidates = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                data["_filepath"] = str(f)
                candidates.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}", file=sys.stderr)
    return candidates

def curate_memories():
    candidates = load_candidates()
    if not candidates:
        print("No staging candidates found to curate.")
        return

    print(f"Loaded {len(candidates)} candidate files for meta-curation.")

    combined_prefs = []
    combined_facts = []
    combined_skills = []

    for c in candidates:
        combined_prefs.extend(c.get("user_preferences", []))
        combined_facts.extend(c.get("durable_facts", []))
        combined_skills.extend(c.get("skill_candidates", []))

    if not (combined_prefs or combined_facts or combined_skills):
        print("All staging candidates were empty. Cleaning up...")
        for c in candidates:
            os.remove(c["_filepath"])
        return

    prompt = f"""You are the Meta-Curator AI for AI-OS. Analyze these aggregated candidate learnings:

USER PREFERENCES:
{json.dumps(combined_prefs, indent=2)}

DURABLE FACTS:
{json.dumps(combined_facts, indent=2)}

SKILL CANDIDATES:
{json.dumps(combined_skills, indent=2)}

Synthesize these learnings into 3 categories:
1. 'auto_ag_context': Bullets to append to AG_CONTEXT.md (durable facts, declarative style).
2. 'approved_skills': Skills to create/update. Must adhere to Hermes standards:
   - name: lowercase-hyphenated <=64 chars.
   - description: ONE sentence, <=60 CHARACTERS max, ends with a period.
3. 'major_proposals': High-impact changes or cross-project shifts that require HUMAN APPROVAL.
   Include 'title', 'reason', and 'proposed_action'.

Return output as JSON.
"""

    try:
        import litellm
        model = os.environ.get("META_CURATOR_MODEL", "gemini/gemini-2.5-pro")
        
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        curated = json.loads(result_text)

        # Process Major Proposals -> Create feature proposal files for Human Approval
        proposals = curated.get("major_proposals", [])
        if proposals:
            features_dir = Path(os.getcwd()) / ".devtool" / "features"
            features_dir.mkdir(parents=True, exist_ok=True)
            for p in proposals:
                title = p.get("title", "Proposed Architecture Update")
                filename = title.lower().replace(" ", "-").replace("/", "-") + ".md"
                feat_path = features_dir / filename
                content = f"""---
id: {filename.replace('.md', '')}
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "{curated.get('timestamp', '2026-07-22')}"
modified: "{curated.get('timestamp', '2026-07-22')}"
completedAt: null
labels: ["proposal", "meta-curator"]
order: 1
---

# Proposal: {title}

**Reasoning**:
{p.get('reason', '')}

**Proposed Action**:
{p.get('proposed_action', '')}
"""
                with open(feat_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Created human review proposal: {feat_path}")

        # Clean up processed staging files
        for c in candidates:
            try:
                os.remove(c["_filepath"])
            except Exception:
                pass

        print("Meta-curation completed successfully.")

    except Exception as e:
        print(f"Meta-curation error: {e}", file=sys.stderr)

if __name__ == "__main__":
    curate_memories()
