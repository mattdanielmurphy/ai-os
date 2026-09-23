# Telegram check-ins remain answerable

- Changed `services/assistant` so `silence_timeout_seconds=0` means an unanswered Telegram check-in never expires; positive values still enable the existing awake-time watchdog.
- Added regression coverage for unlimited mode; `services/assistant/.venv/bin/python -m pytest -q services/assistant/tests/test_assistant.py` passed with 18 tests.
- Restarted `aios-assistant` so the running launchd service loaded the change.
