---
title: "Implement Title Normalization Updates"
date: "2026-08-13"
conversation_id: "cad1c9a3-6701-4b9e-a7d4-68b47a68d661"
source: "antigravity"
---

# Implement Title Normalization Updates

## User

Update `spotapi-service/main.py` and `app/lib/urlResolver.ts` to make title normalization strip leading articles ("the", "a", "an") and handle article mismatches (e.g. "The Rave Death, 1972" vs "Rave Death, 1972").

In `spotapi-service/main.py`:
1. In `_normalize(s: str) -> str`:
   After converting to lowercase, stripping parenthetical/bracketed content, stripping edition suffixes, stripping non-alphanumeric punctuation to spaces, and stripping leading/trailing whitespace (`s = s.strip()`), strip leading articles ("the", "a", "an"):
   `s = re.sub(r"^(the|a|an)\s+", "", s)`
2. In `_classify_match(name_raw: str, artist_names_raw: list[str], norm_title: str, norm_artist: str)`:
   - Calculate `raw_name_exact = bool(norm_title) and _normalize_without_article_strip(name_raw) == _normalize_without_article_strip(title)` or check if `name == norm_title`.
   - Specifically: compute normalized title/name with and without leading articles (e.g. `norm_title` stripped of leading article vs `raw_norm_title` which preserves leading articles).
   - Let `title_exact = bool(norm_title) and name == norm_title` (matching normalized titles without leading articles).
   - Give exact raw title matches (including matching leading articles) a higher score/bonus (e.g., +5 score bonus) over matches that only match with leading articles stripped ("The Rave Death" vs "Rave Death").
   - Compute similarity score between normalized titles/artists.
   - Crucially, if `title_exact` is true (even if leading "the" differed), and artist matches, return `"high"` confidence with score.

In `app/lib/urlResolver.ts`:
1. In `normalizeForMatch(s: string | null | undefined): string`:
   After turning non-alphanumeric to spaces and trimming (`.trim()`):
   `.replace(/^(the|a|an)\s+/i, '')`
2. Update `classifyMatch`:
   - Compute `name` and `normTitle` with `normalizeForMatch` (which strips leading articles).
   - Ensure `titleExact` is true when `name === normTitle`.

Let's refine both files carefully:

In `spotapi-service/main.py`:
Replac
<truncated 1223 bytes>
d_match = False
    if norm_title and not title_is_single_word:
        pattern = re.compile(rf"\b{re.escape(norm_title)}\b")
        title_word_match = bool(pattern.search(name))

    artist_match = False
    if norm_artist:
        artist_match = norm_artist in artist_names or any(
            norm_artist in a or a in norm_artist for a in artist_names
        )
    artist_unknown = not norm_artist

    similarity = difflib.SequenceMatcher(
        None, f"{norm_artist} {norm_title}".strip(), f"{name} {' '.join(artist_names)}".strip()
    ).ratio()

    # Exact match bonus if the leading article also matches verbatim
    article_bonus = 0.0
    if title_exact:
        if _normalize_with_articles(name_raw) == _normalize_with_articles(norm_title):
            article_bonus = 2.0

    edition_penalty = min(len(name_raw) - len(name), 60) * 0.05

    if title_exact and (artist_match or artist_unknown):
        return "high", 100 + article_bonus + similarity * 10 - edition_penalty
    if (title_exact or title_word_match) and artist_match:
        return "low", 50 + article_bonus + similarity * 10 - edition_penalty
    if title_exact and not artist_unknown and not artist_match:
        return "low", 40 + article_bonus + similarity * 10 - edition_penalty
    if artist_match and similarity > 0.35:
        return "low", 20 + similarity * 10 - edition_penalty

    return "none", 0
```

And in `app/lib/urlResolver.ts`:
Update `normalizeForMatch`:
```typescript
function normalizeForMatch(s: string | null | undefined): string {
  if (!s) return '';
  return s
    .toLowerCase()
    .replace(/[\(\[\{].*?[\)\]\}]/g, ' ') // strip parenthetical/bracketed content
    .replace(/(?<=\d)\s*[\-–—]\s*(?=\d)/g, '-') // preserve hyphenated number ranges e.g. 85-92
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/^(the|a|an)\s+/i, '');
}
```

Check the files carefully and edit them using `replace_file_content`.

---

## Assistant

The `spotapi-service/main.py` and `app/lib/urlResolver.ts` files have been updated to support article-aware title normalization and improved match scoring.

### Changes Summary:

*   **`spotapi-service/main.py`**:
    *   Updated `_normalize(s: str) -> str` to strip leading "the", "a", "an" after other normalization steps.
    *   Added `_normalize_with_articles(s: str) -> str` to compute a version of the title that preserves leading articles, used for bonus scoring.
    *   Updated `_classify_match` to calculate a +2.0 bonus for exact raw title matches and integrated it into the confidence score calculations.
*   **`app/lib/urlResolver.ts`**:
    *   Updated `normalizeForMatch` to apply `.replace(/^(the|a|an)\s+/i, '')` after punctuation stripping and trimming.
    *   Verified `classifyMatch` correctly leverages this updated normalization to define `titleExact`.

---
