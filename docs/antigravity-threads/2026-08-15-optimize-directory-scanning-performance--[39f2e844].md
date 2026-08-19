---
title: "Optimize Directory Scanning Performance"
date: "2026-08-15"
conversation_id: "39f2e844-5160-4bfc-beb9-8ed2838c22a6"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

In `/Users/matt/projects/ai-os/scripts/watch_transcripts.py`, optimize `get_active_convs` so it does NOT run `brain_dir.iterdir()` across 500+ directories every 50ms.

Cache the directory scan:
```python

_last_dir_scan = 0
_cached_active_convs = {}
_cached_sub_map = {}

def get_active_convs(brain_dir: Path, max_age_secs: int = 1800) -> tuple[dict, dict]:
    global _last_dir_scan, _cached_active_convs, _cached_sub_map
    now = time.time()

    # Full directory discovery only every 2 seconds
    if (now - _last_dir_scan) > 2.0:
        _last_dir_scan = now
        active = {}
        subagent_to_parent = {}
        if not brain_dir.exists():
            return active, subagent_to_parent

        for conv_dir in brain_dir.iterdir():
            if not conv_dir.is_dir() or conv_dir.name.startswith('.'):
                continue
            transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript.exists():
                try:
                    stat = transcript.stat()
                    if (now - stat.st_mtime) < max_age_secs:
                        active[conv_dir.name] = (stat.st_mtime, stat.st_size)
                        cached = _subagent_cache.get(conv_dir.name)
                        if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
                            subagent_to_parent.update(cached[2])
                        else:
                            sub_map = {}
                            try:
                                with open(transcript, 'r', encoding='utf-8', errors='ignore') as f:
                                    for line in f:
                                        if 'invoke_subagent' in line or 'agy_start' in line or 'agy' in line:
                                            matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', line)
                                            for m in matches:
                                                if m != conv_dir.name:
                                                    sub_map[m] = conv_dir.name
                            except Exception:
                                pass
                            _subagent_cache[conv_dir.name] = (stat.st_mtime, stat.st_size, sub_map)
                            subagent_to_parent.update(sub_map)
                except Exception:
                    continue
        _cached_active_convs = active
        _cached_sub_map = subagent_to_parent
        return active, subagent_to_parent

    # Fast path on 50ms ticks: only stat previously known active conversations
    active = {}
    for cid in list(_cached_active_convs.keys()):
        transcript = brain_dir / cid / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            try:
                stat = transcript.stat()
                if (now - stat.st_mtime) < max_age_secs:
                    active[cid] = (stat.st_mtime, stat.st_size)
            except Exception:
                pass
    _cached_active_convs = active
    return active, _cached_sub_map
```

</span>



<span title="Responded at 9:17am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

*(response in progress or not recorded)*

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~30k / ~400k 🟢 (optimal) | 4:15am | 107 ❓, 16 📤 |

</span>

</span>