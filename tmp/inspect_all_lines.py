import os
import json

p = os.path.expanduser('~/.gemini/antigravity-cli/brain/e4da94f3-e096-4eb5-86ef-24b7e2740dee/.system_generated/logs/transcript.jsonl')
if os.path.exists(p):
    with open(p, 'r') as f:
        for idx, line in enumerate(f):
            if idx >= 15:
                break
            obj = json.loads(line)
            print(f"\nLine {idx}: source={obj.get('source')}, type={obj.get('type')}")
            # Print keys except content if too long
            keys = list(obj.keys())
            print("  Keys:", keys)
            if 'content' in obj:
                print("  Content snippet:", obj['content'][:200].replace('\n', ' '))
            if 'tool_calls' in obj:
                print("  Tool calls:", obj['tool_calls'])
