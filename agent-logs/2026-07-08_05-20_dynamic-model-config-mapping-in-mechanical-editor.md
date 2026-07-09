## Goal
Reconfigure `mechanical_editor.py` to parse `/Users/matt/litellm/config.yaml` to dynamically resolve actual backend model names (e.g. `deepseek-v4-pro`) to their CLI equivalent models (e.g. `claude-fable-5`) since LiteLLM serves these models transparently under alias flags.

## User Feedback & Decisions
- Map requests for `deepseek-v4-pro` to `claude-fable-5` which is mapped to the OpenRouter DeepSeek Pro endpoint, ensuring we actually call the correct target model through the Claude Code agent shell.

## Changes Made
- **[MODIFY] [mechanical_editor.py](file:///Users/matt/projects/ai-os/scripts/mechanical_editor.py)**: Added a parser to extract `model_name` $\rightarrow$ `model` bindings from `config.yaml`. The resolution logic substring-matches requested keys against target paths and returns the CLI option.

## What Worked
- Passing `--model deepseek-v4-pro` successfully resolved to the Fable placeholder and updated files using the DeepSeek V4 Pro backend endpoint.
