import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

matches = re.findall(r'(class(?:Name)?\s*=\s*["`\'])(.*?)(["`\'])', content)
for m in matches:
    cls_str = m[1]
    if 'flex' in cls_str or 'text-' in cls_str or 'bg-' in cls_str or 'ts-html-element' in cls_str:
        print(cls_str)

