#!/bin/bash
set -e
PROJECT_ROOT="/Users/matt/projects/ai-os"
export PYTHONPATH="${PROJECT_ROOT}"
export PATH="/opt/homebrew/bin:/Users/matt/.local/bin:${PATH}"
cd "${PROJECT_ROOT}"
exec "${PROJECT_ROOT}/services/assistant/.venv/bin/python3" "${PROJECT_ROOT}/services/assistant/run.py"
