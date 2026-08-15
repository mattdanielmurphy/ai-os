import re

with open('/Users/matthewmurphy/projects/ai-os/src/main.ts', 'r') as f:
    content = f.read()

# Define whitelisted class words/prefixes
whitelist = {
    'group', 'open-btn', 'delete-btn', 'action-btns', 'delete-thread-btn', 
    'copy-btn', 'new-thread-btn', 'threads-loading', 'file-item', 'folder-item'
}

def clean_class_string(cls_str):
    # Split by spaces but preserve ${...} blocks as whole words if possible.
    # We can use a regex to find ${...} or normal words.
    # Actually, simpler: 
    # Just split by whitespace.
    tokens = re.split(r'(\s+)', cls_str)
    new_tokens = []
    for token in tokens:
        if not token.strip():
            new_tokens.append(token) # keep whitespace
            continue
        
        # Keep if it starts with ts-html-element-
        if token.startswith('ts-html-element-'):
            new_tokens.append(token)
            continue
        
        # Keep if it's in whitelist
        if token in whitelist:
            new_tokens.append(token)
            continue
            
        # Keep if it contains ${...}
        if '${' in token:
            # Maybe it's a dynamic class. Keep it.
            # E.g. ${minRem < 0.2 ? 'text-red-400' : 'text-green-400'}
            # Oh wait, we probably should replace the text-red-400 inside the ${...} too? 
            # The user said "remove tailwind". Let's just keep the ${...} as is since it might have logic, or wait, we can just replace text-red-400 with its corresponding ts-html-element if we knew it. But we don't. We'll leave ${...} for now.
            new_tokens.append(token)
            continue
            
        # If it's a known non-tailwind word (like custom semantic classes), we keep it? 
        # Most of them are tailwind classes. We drop them!
        
    return ''.join(new_tokens).strip()

def replacer(match):
    prefix = match.group(1)
    cls_str = match.group(2)
    suffix = match.group(3)
    
    cleaned = clean_class_string(cls_str)
    # remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # If className=`...` and cleaned is empty, maybe keep it empty
    if not cleaned and prefix.strip() == 'className = `':
        return prefix + suffix
    
    return prefix + cleaned + suffix

new_content = re.sub(r'(class(?:Name)?\s*=\s*["`\'])(.*?)(["`\'])', replacer, content)

# But wait, what about lines like:
# item.className = `flex flex-col p-1 rounded transition-all border ${...}`
# They don't have ts-html-element! If we strip them, it becomes `item.className = \`${...}\``.
# That's probably exactly what we want, since the previous agent might have missed mapping them?
# Wait! Let's check if the previous agent mapped them. If they didn't map them, removing them will break the UI.
