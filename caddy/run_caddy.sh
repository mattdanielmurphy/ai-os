#!/bin/zsh
# run_caddy.sh — Start Caddy reverse proxy for LLM/LiteLLM

if [ -f ~/.zshrc ]; then
    source ~/.zshrc
fi

cd /Users/matt/projects/ai-os
exec /opt/homebrew/bin/caddy run --config /Users/matt/projects/ai-os/Caddyfile
