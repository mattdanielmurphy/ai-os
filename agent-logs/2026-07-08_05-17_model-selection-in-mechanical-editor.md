## Goal
Extend `mechanical_editor.py` to support model selection so agents can specify which model to use for edits, while mapping the selected key to the "Anthropic equivalent" model accepted by the `claude` CLI.

## User Feedback & Decisions
- Map model arguments (`flash`, `pro`, `gemini-pro`, etc.) to the Anthropic model placeholders (`claude-3-5-haiku-20241022`, `claude-fable-5`, `claude-3-opus-20240229`) that route to the correct actual backend models (DeepSeek V4 Flash, DeepSeek V4 Pro, Gemini 2.5 Pro) in `config.yaml`.

## Changes Made
- **[MODIFY] [mechanical_editor.py](file:///Users/matt/projects/ai-os/scripts/mechanical_editor.py)**: Added a `--model` argparse parameter (defaulting to `"flash"`). Included a `model_map` dictionary that resolves the request and passes it to the `claude` CLI using the `--model` flag.

## What Worked
- Passing `--model pro` successfully mapped to `claude-fable-5` and completed the edit using DeepSeek V4 Pro.
- Default execution continues to run Haiku (`claude-3-5-haiku-20241022`), pointing to the cheap DeepSeek V4 Flash backend.

## Architecture Notes
- The model mapping decouples the agent's target intent (e.g. asking for "pro" or "flash") from the specific model names required by the Claude Code CLI structure, ensuring configuration changes in `config.yaml` don't break agent execution.
