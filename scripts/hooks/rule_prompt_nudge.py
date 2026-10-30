#!/usr/bin/env python3
"""UserPromptSubmit hook: when Matt states a standing rule, make the agent save it to disk.

Matt, 2026-10-29: agents forget they're ephemeral and "remember" things by promising to,
instead of storing a rule. Prompts with rule language get a reminder to save it in ai-os
`.rules/`, rebuild, and confirm. Pairs with `rule_promise_guard.py` (Stop). Fails open.
"""
import json
import re
import sys

RULE_WORDS = re.compile(
    r"\b(always|never|from now on|every time|each time|whenever|going forward|"
    r"make sure (?:you|to)|stop doing|don'?t ever|forever|in future)\b",
    re.I,
)


# App/system envelopes are not Matt's words; strip them before matching.
ENVELOPES = re.compile(
    r"<(side-sessions-event|cross-session-message|task-notification|system-reminder|wake|ci-monitor-event)\b"
    r"[^>]*>.*?(?:</\1>|\Z)", re.S)


def main() -> None:
    prompt = ENVELOPES.sub("", json.load(sys.stdin).get("prompt", ""))
    if prompt.lstrip().startswith("/") or not RULE_WORDS.search(prompt):
        return
    note = (
        "Matt's message has rule language. If it states a standing preference (not a one-off), "
        "draft it to `~/projects/ai-os/.rules/pending/<date>-<slug>.md` this turn. Show him the "
        "exact wording, what it replaces, and why. Do not save it to `.rules/` until he says yes. "
        "Promising to remember is not saving: you are ephemeral."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
