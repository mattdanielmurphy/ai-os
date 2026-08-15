import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

# Custom manual replacements for the dynamic classNames that were missed
content = content.replace("""        item.className = `flex flex-col p-1 rounded transition-all border ${
            isActive
                ? 'bg-gray-100 dark:bg-gray-800/40 border-gray-200 dark:border-gray-700/80 shadow-sm'
                : 'bg-transparent border-transparent'
        }`""", """        item.className = isActive ? 'project-item project-item-active' : 'project-item'""")

content = content.replace("""        header.className = `flex items-center justify-between p-1.5 rounded cursor-pointer transition-all ${
            isActive
                ? 'text-gray-900 dark:text-white font-semibold bg-gray-200/70 dark:bg-gray-800 border border-gray-300 dark:border-gray-700'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-250 hover:bg-gray-200/50 dark:hover:bg-gray-900/50'
        }`""", """        header.className = isActive ? 'project-item-header project-item-header-active' : 'project-item-header'""")

# Apply general tailwind cleanup
whitelist = {
    'group', 'open-btn', 'delete-btn', 'action-btns', 'delete-thread-btn', 
    'copy-btn', 'new-thread-btn', 'threads-loading', 'file-item', 'folder-item',
    'prose', 'prose-sm', 'prose-invert', 'file-btn', 'project-item', 'project-item-active',
    'project-item-header', 'project-item-header-active'
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
    
    cleaned = clean_class_string(cls_str)
    return prefix + cleaned + suffix

new_content = re.sub(r'(class(?:Name)?\s*=\s*["`\'])(.*?)(["`\'])', replacer, content)

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'w') as f:
    f.write(new_content)

