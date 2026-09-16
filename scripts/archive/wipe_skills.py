import shutil
from pathlib import Path

HOME = Path.home()
PRIMARY_SOURCE = HOME / "projects" / "ai-os" / "skills"
TARGET_DIRS = [
    HOME / ".hermes" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".agents" / "skills",
    HOME / ".gemini" / "config" / "skills",
    HOME / ".gemini" / "antigravity-cli" / "skills",
    HOME / ".agy" / "skills",
    HOME / ".gemini" / "antigravity" / "skills",
]

all_locations = [PRIMARY_SOURCE] + TARGET_DIRS

trash_skills = [
    "research-paper-writing", "openhue", "petdex", "polymarket", "powerpoint",
    "pretext", "remotion", "segment-anything", "sketch", "songsee",
    "songwriting-and-ai-music", "teams-meeting-pipeline", "touchdesigner-mcp",
    "yuanbao", "media", "research", "devops", "apple", "github"
]

custom_skills = [
    "music-cross-linker", "youtube-content", "simplify-code", "resume",
    "restore-context", "strict-delegation", "popular-web-designs", "plan",
    "plan-multi-step", "pdf", "xlsx", "docx"
]

for loc in all_locations:
    if loc.exists():
        for skill in trash_skills:
            path = loc / skill
            if path.exists():
                shutil.rmtree(path)
        for skill in custom_skills:
            path = loc / skill
            if path.exists():
                shutil.rmtree(path)

print("Wiped trash and un-isolated custom skills from all locations.")
