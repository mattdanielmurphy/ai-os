# AI-OS custom zshrc to hook shell startup and source user's zshrc

if [ -f "$HOME/.zshrc" ]; then
    # Temporarily reset ZDOTDIR to HOME so that sourcing ~/.zshrc works normally
    OLD_ZDOTDIR="$ZDOTDIR"
    export ZDOTDIR="$HOME"
    source "$HOME/.zshrc"
    export ZDOTDIR="$OLD_ZDOTDIR"
fi

# Source our AI-OS custom environment settings
if [ -f "/Users/matt/projects/ai-os/.zshrc_aios" ]; then
    source "/Users/matt/projects/ai-os/.zshrc_aios"
fi
