---
title: "Update String Normalization Logic"
date: "2026-08-12"
conversation_id: "883a26f0-855a-487b-9793-0494c089c84b"
source: "antigravity"
---

# Update String Normalization Logic

## User

Update `normalizeForMatch` in `app/lib/urlResolver.ts` and `_normalize` in `spotapi-service/main.py`.

In `app/lib/urlResolver.ts`:
Modify `normalizeForMatch`:
```ts
function normalizeForMatch(s: string | null | undefined): string {
  if (!s) return '';
  return s
    .toLowerCase()
    .replace(/[\(\[\{].*?[\)\]\}]/g, ' ') // strip parenthetical/bracketed content
    .replace(/(?<=\d)\s*[\-–—]\s*(?=\d)/g, '-') // preserve hyphenated number ranges e.g. 85-92
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}
```

In `spotapi-service/main.py`:
Modify `_normalize`:
```python
def _normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[\(\[\{].*?[\)\]\}]", "", s)  # strip parenthetical/bracketed content
    s = _EDITION_SUFFIX_RE.sub("", s)  # strip dash-suffixed edition descriptors
    s = re.sub(r"(?<=\d)\s*[\-–—]\s*(?=\d)", "-", s)  # preserve hyphenated number ranges e.g. 85-92
    s = re.sub(r"[^a-z0-9]+", " ", s)  # strip punctuation
    return s.strip()
```

Target files:
- /Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts
- /Users/matt/projects/music-cross-linker/spotapi-service/main.py

---

## Assistant

DONE

---
