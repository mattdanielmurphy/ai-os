import re

def replace_classes(match):
    cls_str = match.group(1)
    classes = cls_str.split()
    new_classes = []
    
    mapping = {
        'bg-gray-900': 'bg-gray-50 dark:bg-gray-900',
        'bg-gray-950': 'bg-white dark:bg-gray-950',
        'bg-gray-950/40': 'bg-white/40 dark:bg-gray-950/40',
        'bg-gray-850': 'bg-gray-100 dark:bg-gray-850',
        'bg-gray-850/50': 'bg-gray-100/50 dark:bg-gray-850/50',
        'bg-gray-850/80': 'bg-gray-100/80 dark:bg-gray-850/80',
        'bg-gray-800': 'bg-gray-200 dark:bg-gray-800',
        'bg-gray-800/80': 'bg-gray-200/80 dark:bg-gray-800/80',
        'bg-gray-700': 'bg-gray-300 dark:bg-gray-700',
        'bg-black': 'bg-white dark:bg-black',
        'bg-black/65': 'bg-white/65 dark:bg-black/65',
        'text-white': 'text-gray-900 dark:text-white',
        'text-gray-200': 'text-gray-800 dark:text-gray-200',
        'text-gray-300': 'text-gray-700 dark:text-gray-300',
        'text-gray-400': 'text-gray-600 dark:text-gray-400',
        'text-gray-500': 'text-gray-500 dark:text-gray-500',
        'text-gray-600': 'text-gray-400 dark:text-gray-600',
        'border-gray-800': 'border-gray-200 dark:border-gray-800',
        'border-gray-850': 'border-gray-200 dark:border-gray-850',
        'border-gray-700': 'border-gray-300 dark:border-gray-700',
        'hover:bg-gray-800': 'hover:bg-gray-200 dark:hover:bg-gray-800',
        'hover:bg-gray-700': 'hover:bg-gray-300 dark:hover:bg-gray-700',
        'hover:bg-gray-900/50': 'hover:bg-gray-100/50 dark:hover:bg-gray-900/50',
        'hover:bg-gray-850': 'hover:bg-gray-100 dark:hover:bg-gray-850',
        'hover:text-white': 'hover:text-gray-900 dark:hover:text-white',
        'hover:text-gray-200': 'hover:text-gray-800 dark:hover:text-gray-200',
    }

    for c in classes:
        # Don't double replace if we run it twice
        if c.startswith('dark:'):
            new_classes.append(c)
            continue
            
        if c in mapping:
            # check if dark:c is already in classes, to avoid duplicates
            if f"dark:{c}" not in classes:
                new_classes.extend(mapping[c].split())
            else:
                new_classes.append(c)
        else:
            new_classes.append(c)
            
    # remove duplicates but preserve order
    seen = set()
    final_classes = []
    for c in new_classes:
        if c not in seen:
            seen.add(c)
            final_classes.append(c)
            
    return 'class="' + ' '.join(final_classes) + '"'

with open('index.html', 'r') as f:
    content = f.read()

content = re.sub(r'class="([^"]*)"', replace_classes, content)

with open('index.html', 'w') as f:
    f.write(content)
