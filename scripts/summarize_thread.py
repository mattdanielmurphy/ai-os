import os
import sys
import json
import urllib.request

def summarize(conv_id):
    brain_dirs = [
        os.path.expanduser("~/.gemini/antigravity-ide/brain"),
        os.path.expanduser("~/.gemini/antigravity/brain"),
        os.path.expanduser("~/.gemini/antigravity-cli/brain"),
    ]
    transcript_path = None
    target_brain = None
    for b in brain_dirs:
        p = f"{b}/{conv_id}/.system_generated/logs/transcript.jsonl"
        if os.path.exists(p):
            transcript_path = p
            target_brain = b
            break
            
    if not transcript_path or not target_brain:
        return
        
    registry_path = f"{target_brain}/thread_summaries.json"

    first_user = None
    final_model = None

    with open(transcript_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("type") == "USER_INPUT" and first_user is None:
                    first_user = entry.get("content", "")
                if entry.get("type") in ("PLANNER_RESPONSE", "ASSISTANT_RESPONSE"):
                    final_model = entry.get("content", "")
            except json.JSONDecodeError:
                continue

    if not first_user or not final_model:
        return

    prompt = f"Summarize this thread briefly (2 sentences max). User request: {first_user[:1000]}... Final response: {final_model[:1000]}..."
    
    url = "http://localhost:8082/v1/chat/completions"
    data = json.dumps({
        "model": "deepseek-v4-flash-low",
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            summary = resp_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return

    registry = {}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        except:
            registry = {}
    
    registry[conv_id] = summary
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        summarize(sys.argv[1])
