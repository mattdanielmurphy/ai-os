import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

whitelist = {
    'group', 'open-btn', 'delete-btn', 'action-btns', 'delete-thread-btn', 
    'copy-btn', 'new-thread-btn', 'threads-loading', 'file-item', 'folder-item',
    'prose', 'prose-sm', 'prose-invert'
}

def is_tailwind_class(token):
    # If it has a colon (hover:, dark:) or brackets (-[...]), it's tailwind
    if ':' in token or '[' in token or ']' in token:
        # prose-headings: is tailwind, but we whitelist prose
        if token.startswith('prose-headings') or token.startswith('prose-pre'):
            return False # treat as typography plugin
        return True
    
    # Common tailwind prefixes/exact
    tw_prefixes = (
        'text-', 'bg-', 'p-', 'pt-', 'pb-', 'pl-', 'pr-', 'px-', 'py-',
        'm-', 'mt-', 'mb-', 'ml-', 'mr-', 'mx-', 'my-', 'w-', 'h-',
        'border', 'rounded', 'shadow', 'font-', 'opacity-', 'z-',
        'flex', 'grid', 'absolute', 'relative', 'truncate', 'max-w-',
        'items-', 'justify-', 'overflow-', 'cursor-', 'transition',
        'duration-', 'transform', 'rotate-', 'animate-', 'select-',
        'aspect-', 'line-clamp-', 'leading-', 'tracking-', 'uppercase',
        'inline-flex', 'shrink-0', 'flex-1', 'min-w-', 'flex-col', 'flex-wrap'
    )
    for p in tw_prefixes:
        if token == p or token.startswith(p):
            return True
            
    # whitelist semantic names
    if token.startswith('ts-html-element-'): return False
    if token in whitelist: return False
    
    # If it's a template literal ${...}, not tailwind class literal (we keep it)
    if '${' in token or '}' in token: return False
    
    return False

def clean_class_string(cls_str):
    # Tokenize by whitespace
    tokens = re.split(r'(\s+)', cls_str)
    new_tokens = []
    
    for t in tokens:
        if not t.strip():
            new_tokens.append(t)
            continue
        if not is_tailwind_class(t):
            new_tokens.append(t)
            
    cleaned = ''.join(new_tokens)
    # Reduce multiple spaces
    cleaned = re.sub(r' {2,}', ' ', cleaned).strip()
    return cleaned

def replacer(match):
    prefix = match.group(1)
    cls_str = match.group(2)
    suffix = match.group(3)
    
    # Only clean if it contains ts-html-element
    if 'ts-html-element-' in cls_str:
        cleaned = clean_class_string(cls_str)
        return prefix + cleaned + suffix
    return match.group(0)

# Replace all class strings that contain ts-html-element
new_content = re.sub(r'(class(?:Name)?\s*=\s*["`\'])(.*?)(["`\'])', replacer, content)

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'w') as f:
    f.write(new_content)

