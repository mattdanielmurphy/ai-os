import os

dirs = ['src', 'src-tauri']
old_str = 'matthewmurphy'
new_str = 'matt'

for d in dirs:
    for root, _, files in os.walk(d):
        for f in files:
            if not f.endswith(('.ts', '.tsx', '.rs', '.json', '.html')):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except Exception:
                continue
            
            if old_str in content:
                print(f"Replacing in {path}")
                content = content.replace(old_str, new_str)
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
