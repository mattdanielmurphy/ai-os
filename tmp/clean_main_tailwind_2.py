import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

whitelist = {
    'group', 'open-btn', 'delete-btn', 'action-btns', 'delete-thread-btn', 
    'copy-btn', 'new-thread-btn', 'threads-loading', 'file-item', 'folder-item',
    'prose', 'prose-sm', 'prose-invert', 'file-btn'
}

def is_tailwind_class(token):
    if ':' in token or '[' in token or ']' in token:
        if token.startswith('prose-headings') or token.startswith('prose-pre'):
            return False
        return True
    
    tw_prefixes = (
        'text-', 'bg-', 'p-', 'pt-', 'pb-', 'pl-', 'pr-', 'px-', 'py-',
        'm-', 'mt-', 'mb-', 'ml-', 'mr-', 'mx-', 'my-', 'w-', 'h-',
        'border', 'rounded', 'shadow', 'font-', 'opacity-', 'z-',
        'flex', 'grid', 'absolute', 'relative', 'truncate', 'max-w-',
        'items-', 'justify-', 'overflow-', 'cursor-', 'transition',
        'duration-', 'transform', 'rotate-', 'animate-', 'select-',
        'aspect-', 'line-clamp-', 'leading-', 'tracking-', 'uppercase',
        'inline-flex', 'shrink-0', 'flex-1', 'min-w-', 'flex-col', 'flex-wrap',
        'gap-', 'top-', 'bottom-', 'left-', 'right-', 'italic', 'underline',
        'self-', 'inline-block', 'whitespace-'
    )
    for p in tw_prefixes:
        if token == p or token.startswith(p):
            return True
            
    if token.startswith('ts-html-element-'): return False
    if token in whitelist: return False
    if '${' in token or '}' in token: return False
    
    return False

def clean_class_string(cls_str):
    tokens = re.split(r'(\s+)', cls_str)
    new_tokens = []
    
    for t in tokens:
        if not t.strip():
            new_tokens.append(t)
            continue
        if not is_tailwind_class(t):
            new_tokens.append(t)
            
    cleaned = ''.join(new_tokens)
    cleaned = re.sub(r' {2,}', ' ', cleaned).strip()
    return cleaned

def replacer(match):
    prefix = match.group(1)
    cls_str = match.group(2)
    suffix = match.group(3)
    
    # We will clean ALL class strings, regardless of whether they have ts-html-element
    cleaned = clean_class_string(cls_str)
    return prefix + cleaned + suffix

# First, replace `className = ...` where it uses template strings heavily without ts-html-element
# Actually, those lines 1305 and 1312 we should manually replace using regular expressions because we need to define semantic classes!
