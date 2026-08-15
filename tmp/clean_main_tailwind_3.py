import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

# Just quickly remove those specific missed ones
content = content.replace("ts-html-element-15 -top-3 -right-2", "ts-html-element-15")
content = content.replace("ts-html-element-18 -top-3 -left-2", "ts-html-element-18")

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'w') as f:
    f.write(content)
