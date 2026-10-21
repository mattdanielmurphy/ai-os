"""Build the "Hey Claude" Shortcut: Dictate Text -> Run Shell Script (bin/hey-claude via stdin).

Vocal Shortcuts (System Settings > Accessibility) runs it on the trained "Hey Claude" phrase.
  python3 shortcuts/build_hey_claude.py      writes tmp/Hey Claude.shortcut (signed), then: open it to import
"""
import plistlib
import subprocess
import uuid
from pathlib import Path

AIOS = Path(__file__).resolve().parent.parent
OUT = AIOS / "tmp"


def U():
    return str(uuid.uuid4()).upper()


dictated = U()
actions = [
    {"WFWorkflowActionIdentifier": "is.workflow.actions.dictatetext", "WFWorkflowActionParameters": {
        "UUID": dictated, "WFDictateTextStopListening": "After Pause"}},
    {"WFWorkflowActionIdentifier": "is.workflow.actions.runshellscript", "WFWorkflowActionParameters": {
        "Shell": "/bin/zsh",
        "InputMode": "to stdin",
        "Input": {"Value": {"Type": "ActionOutput", "OutputUUID": dictated, "OutputName": "Dictated Text"},
                  "WFSerializationType": "WFTextTokenAttachment"},
        "Script": "$HOME/projects/ai-os/bin/hey-claude"}},
]
workflow = {
    "WFWorkflowActions": actions, "WFWorkflowClientVersion": "2900", "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4282601983, "WFWorkflowIconGlyphNumber": 59781},
    "WFWorkflowImportQuestions": [], "WFWorkflowInputContentItemClasses": ["WFStringContentItem"],
    "WFWorkflowTypes": [], "WFWorkflowHasShortcutInputVariables": False,
}
OUT.mkdir(exist_ok=True)
unsigned = OUT / "Hey Claude.unsigned.shortcut"
signed = OUT / "Hey Claude.shortcut"
with unsigned.open("wb") as f:
    plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)
subprocess.run(["shortcuts", "sign", "--mode", "anyone", "--input", str(unsigned), "--output", str(signed)], check=True)
print(signed)
