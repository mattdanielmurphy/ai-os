import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

# Find all class="..." or className = `...`
# It's tricky to use a single regex for everything.
# We want to remove tailwind classes, leaving `ts-html-element-\d+` and `group`, `open-btn`, etc.
# Tailwind classes typically have: -, :, [, ], flex, block, inline, grid, w-, h-, p-, m-, text-, bg-, border, shadow, rounded, font-, opacity, transition, cursor, animate, relative, absolute, truncate, etc.
