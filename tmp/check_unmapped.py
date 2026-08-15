import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

matches = re.findall(r'(class(?:Name)?\s*=\s*["`\'])(.*?)(["`\'])', content)
for m in matches:
    cls_str = m[1]
    # Check if it has tailwind-like classes but NO ts-html-element
    if 'ts-html-element' not in cls_str:
        if 'flex' in cls_str or 'text-' in cls_str or 'bg-' in cls_str or 'p-' in cls_str or 'm-' in cls_str or 'w-' in cls_str or 'border' in cls_str:
            print("UNMAPPED:", cls_str)

