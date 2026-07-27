#!/bin/zsh
# run_litellm.sh — Start LiteLLM proxy (simplified for tmux-agent-wrapper)
# Load user environment variables, then run litellm directly.
# The tmux-agent-wrapper handles tmux lifecycle and restart.

if [ -f ~/.zshrc ]; then
    source ~/.zshrc
fi

cd /Users/matt/projects/ai-os/litellm
exec /Users/matt/.local/bin/litellm --config config.yaml --port 8082