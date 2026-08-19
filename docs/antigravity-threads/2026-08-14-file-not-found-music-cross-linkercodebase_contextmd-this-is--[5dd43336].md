---
title: "[File not found: music-cross-linker/codebase_context.md] This is a Next.js..."
date: "2026-08-14"
conversation_id: "5dd43336-17b4-4a04-b4e5-caf29a79636e"
source: "antigravity"
---

# [File not found: music-cross-linker/codebase_context.md] This is a Next.js...

## User

[File not found: music-cross-linker/codebase_context.md]

This is a Next.js music cross-linking app (URL shortener that matches songs/albums across YouTube, Spotify, Apple Music). I have two bugs to fix, and I've attached the relevant source as codebase context.

BUG 1: Visiting /yes/fragile shows a "Track Link" badge even though "Fragile" by Yes is obviously an album. The badge is driven by `ctx.isAlbum` in TrackView.tsx, which is set in `resolveEntity()` in urlResolver.ts. Currently `isAlbum` is only guessed from the literal shape of `sourceUrl` (e.g. contains `/album/`, `entity=album`, `list=`). For a known slug route like `/yes/fragile` there is no sourceUrl at all, so it always defaults to false/track, even after we already have a cached Spotify/Apple album match.

I've already made a small patch: after loading `cached` matches from `entity_matches`, if `isAlbum` is still false, set it to true if any cached match URL contains `/album/`. Please critique this fix and tell me if there are edge cases/better approaches (e.g. should we also persist an `is_album` column on `resolved_entities`, should uncertain matches count, what about Apple Music album URLs which use `/album/` too so should be covered, what about the very first resolution before anything is cached yet).

BUG 2 (the important one): Spotify matching via spotapi-service (main.py, `_classify_match` + `_search_spotify`) fails to match Yes's album "Fragile" because the only Spotify release is titled "Fragile (Super Deluxe)". Our `_normalize()` strips anything in parens/brackets before comparing, so "Fragile (Super Deluxe)" normalizes to "fragile" too... so why would this NOT already match as 'high' confidence currently? Look closely at `_classify_match` and `_search_spotify` and tell me:
1. Why "Fragile (Super Deluxe)" likely is NOT currently winning as the top candidate for query "Yes Fragile" / title="Fragile" artist="Yes" — is it a candidate ranking/scoring issue, or is the Spotify search literally not returning it as a top-N item, or something in item extraction?
2. The requirement: always prefer the closest-matching album by the correct artist over any exact-title album by a different artist — i.e. artist match should dominate over literal title match when there's ambiguity, and appending extra descriptive words to an otherwise-exact title (like "(Super Deluxe)", "(Deluxe Edition)", "(Remastered)") should NOT prevent a 'high' confidence match when the artist matches, as long as there's no better/closer option.

Please give me a concrete, targeted patch to `_classify_match` (and `_search_spotify` if needed) that: (a) fixes this Fragile case, (b) keeps the existing 'low'/'none' semantics for genuinely different albums/artists, (c) still prefers an exact plain-title match over a "(Super Deluxe)"-style one when both exist for the same artist, (d) doesn't accidentally make some other artist's differently-titled album with a shared common word start matching 'high'.

---

## Assistant

## Perplexity — 08:28 PM

I couldn’t inspect the attached `codebase_context.md` because it was unavailable, and the connected GitHub search did not find these symbols in an accessible repository. [github_mcp_direct] Based on the behavior you described, the likely fix is to separate **candidate retrieval**, **artist correctness**, **title similarity**, and **candidate ranking** rather than relying on `_normalize()` alone.

Bug 1: `isAlbum`

Your cached-match fallback is a reasonable short-term fix:


```
ts
if (!isAlbum && cached.some(match =>
  match.url.toLowerCase().includes("/album/")
)) {
  isAlbum = true;
}
```


It handles both Spotify and Apple Music because both commonly use `/album/` in album URLs. However, it has three important weaknesses.

1. It infers type from URLs

URL shape is weaker than provider metadata. These are preferable, in order:

The entity type returned by the provider.

A persisted `resolved_entities.is_album` value.

The type of a high-confidence cached provider match.

URL heuristics as a final fallback.

A better schema is tri-state rather than Boolean:


```
sql
ALTER TABLE resolved_entities
ADD COLUMN is_album boolean NULL;
```


Interpret the values as:

`true`: confidently known to be an album.

`false`: confidently known to be a track.

`NULL`: not resolved yet or ambiguous.

Do not immediately persist `false` merely because the route had no `sourceUrl`. That would permanently encode “unknown” as “track.”

2. Any cached match may be too permissive

Only use a cached match if it is sufficiently trustworthy. For example:


```
ts
const albumMatch = cached.find(match =>
  match.confidence === "high" &&
  match.entityType === "album"
);

if (isAlbum === false && albumMatch) {
  isAlbum = true;
}
```


If the cache does not currently store `entityType`, a temporary URL-based version should at least restrict itself to high-confidence matches:


```
ts
const cachedAlbum = cached.some(match =>
  match.confidence === "high" &&
  /\/album(?:\/|[/?#])/i.test(match.url)
);

if (!isAlbum && cachedAlbum) {
  isAlbum = true;
}
```


Avoid treating an uncertain or `low` match as authoritative. Otherwise, a wrong provider match could change the UI from “Track Link” to “Album Link.”

3. It does not fix the first resolution

For a first-time `/yes/fragile` visit, there may be no cache yet. The resolver should derive `isAlbum` while resolving the provider candidates:


```
ts
type ResolvedMatch = {
  url: string;
  confidence: "high" | "low" | "none";
  entityType?: "track" | "album";
};

function inferAlbumFromMatch(match: ResolvedMatch): boolean | null {
  if (match.entityType === "album") return true;
  if (match.entityType === "track") return false;

  if (
    match.confidence === "high" &&
    /\/album(?:\/|[/?#])/i.test(match.url)
  ) {
    return true;
  }

  return null;
}
```


Then use a tri-state aggregation:


```
ts
const highConfidenceMatches = matches.filter(
  match => match.confidence === "high"
);

const entityTypes = highConfidenceMatches
  .map(inferAlbumFromMatch)
  .filter((value): value is boolean => value !== null);

const inferredIsAlbum =
  entityTypes.length > 0 && entityTypes.every(Boolean)
    ? true
    : entityTypes.length > 0 && entityTypes.every(value => !value)
      ? false
      : null;
```


In practice, provider response metadata is better than URL parsing. Spotify album search results already identify albums, and Apple Music responses generally distinguish albums from songs. Store that information with the match.

Why Bug 2 can happen

The fact that `_normalize("Fragile (Super Deluxe)")` becomes `"fragile"` does not prove that the candidate will match. Normalization only matters **after the candidate reaches `_classify_match`**.

There are three likely failure points.

Candidate ranking

If `_search_spotify` returns only the first few Spotify results and `_classify_match` examines them in order, Spotify may return an exact-title album by another artist before Yes’s deluxe release.

For example:


```
text
Fragile — Some Other Artist
Fragile (Super Deluxe) — Yes
```


If the classifier accepts or ranks the first exact-title result too highly, the Yes result loses despite having the correct artist.

This is the most likely architectural problem if the Yes album appears in Spotify’s raw response but is not selected.

Spotify result truncation

If `_search_spotify` requests a small `limit`, or slices before scoring:


```
text
items = response["albums"]["items"][:5]
```


then the Yes release may never reach `_classify_match`. In that case, changing `_classify_match` cannot fix the problem.

You should score every returned candidate, or at least increase the search limit and score the whole returned page.

Item extraction

Spotify album search results are nested under:


```
text
response["albums"]["items"]
```


A common bug is accidentally extracting track results:


```
text
response["tracks"]["items"]
```


or assuming an album has a singular `artist` field rather than:


```
text
item["artists"]
```


The extraction should preserve the album title and all contributing artists:


```
text
def _extract_spotify_albums(response):
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "artists": [
                artist["name"]
                for artist in item.get("artists", [])
            ],
            "url": item["external_urls"]["spotify"],
            "release_date": item.get("release_date"),
        }
        for item in response.get("albums", {}).get("items", [])
    ]
```


Add temporary logging before classification:


```
text
logger.info(
    "Spotify candidates for %r by %r: %s",
    title,
    artist,
    [
        (candidate["name"], candidate["artists"])
        for candidate in candidates
    ],
)
```


That immediately distinguishes “not retrieved” from “retrieved but ranked incorrectly.”

Targeted classifier patch

The important rule is:

Exact or descriptive-suffix title similarity is only allowed to become `high` when the artist also matches.

A different artist’s exact title should remain `low`, not `high`.

Here is a focused implementation. Adapt the return object to your existing shape.


```
text
import re
import unicodedata
from difflib import SequenceMatcher


_DESCRIPTIVE_SUFFIX_RE = re.compile(
    r"""
    \s*
    (?:
        \(?
        (?:
            super\s+deluxe
            |deluxe(?:\s+edition)?
            |remaster(?:ed)?
            |anniversary(?:\s+edition)?
            |expanded(?:\s+edition)?
            |special(?:\s+edition)?
            |complete(?:\s+edition)?
            |bonus(?:\s+tracks?)?
        )
        [^)]*
        \)?
    )
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _normalize(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        character for character in value
        if not unicodedata.combining(character)
    )

    value = value.casefold()
    value = re.sub(r"[\(\[\{].*?[\)\]\}]", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _normalize_album_title(value: str | None) -> str:
    """
    Removes only recognized release-description suffixes.

    This is safer than removing every parenthetical expression because
    parentheses can sometimes be part of the actual title.
    """
    if not value:
        return ""

    stripped = _DESCRIPTIVE_SUFFIX_RE.sub("", value).strip()
    return _normalize(stripped)


def _artist_matches(query_artist: str, candidate_artists: list[str]) -> bool:
    query = _normalize(query_artist)

    if not query:
        return False

    normalized_candidates = {
        _normalize(candidate)
        for candidate in candidate_artists
        if candidate
    }

    # Deliberately require an exact normalized artist match.
    # Do not use substring matching here.
    return query in normalized_candidates


def _title_score(query_title: str, candidate_title: str) -> tuple[int, float]:
    query_raw = _normalize(query_title)
    candidate_raw = _normalize(candidate_title)

    query_base = _normalize_album_title(query_title)
    candidate_base = _normalize_album_title(candidate_title)

    if not query_raw or not candidate_raw:
        return 0, 0.0

    # Best: exact title as displayed by the provider.
    if query_raw == candidate_raw:
        return 3, 1.0

    # Also exact after removing a known descriptive release suffix.
    if query_base and query_base == candidate_base:
        return 2, 1.0

    similarity = SequenceMatcher(
        None,
        query_base or query_raw,
        candidate_base or candidate_raw,
    ).ratio()

    return 1, similarity


def _classify_match(
    *,
    title: str,
    artist: str,
    candidate_title: str,
    candidate_artists: list[str],
) -> str:
    artist_match = _artist_matches(artist, candidate_artists)
    title_kind, title_similarity = _title_score(title, candidate_title)

    if artist_match:
        # Exact plain title, or exact title plus a recognized suffix.
        if title_kind in (3, 2):
            return "high"

        # A genuinely close title by the correct artist can still be useful,
        # but do not make arbitrary shared words high confidence.
        if title_kind == 1 and title_similarity >= 0.90:
            return "high"

        if title_similarity >= 0.70:
            return "low"

        return "none"

    # Wrong artist: never high, even when the title is exact.
    if title_kind == 3:
        return "low"

    if title_kind == 2 and title_similarity >= 0.90:
        return "low"

    return "none"
```


The crucial properties are:

`Fragile (Super Deluxe)` by Yes receives `high`.

`Fragile` by another artist receives at most `low`.

`Fragile` by Yes outranks `Fragile (Super Deluxe)` by Yes.

A different album by another artist that merely contains a common word does not become `high`.

Artist matching is exact after normalization rather than substring-based.

If your existing `_normalize()` already removes parenthesized text, you can keep it for general comparisons, but I would introduce `_normalize_album_title()` separately. Removing every parenthesized expression can incorrectly collapse genuinely distinct titles.

Candidate ranking patch

Classification alone is insufficient if `_search_spotify` returns the wrong candidate. Rank by artist correctness before title closeness.


```
text
def _candidate_rank(
    *,
    query_title: str,
    query_artist: str,
    candidate: dict,
) -> tuple[int, int, float]:
    artist_match = _artist_matches(
        query_artist,
        candidate.get("artists", []),
    )

    title_kind, title_similarity = _title_score(
        query_title,
        candidate.get("name", ""),
    )

    # Higher values sort first.
    #
    # Artist match dominates everything else:
    # correct artist > wrong artist.
    #
    # Within the correct artist:
    # exact plain title > descriptive suffix > fuzzy title.
    return (
        int(artist_match),
        title_kind,
        title_similarity,
    )


def _search_spotify(title: str, artist: str):
    response = spotify.search(
        q=f"album:{title} artist:{artist}",
        type="album",
        limit=50,
    )

    candidates = _extract_spotify_albums(response)

    candidates.sort(
        key=lambda candidate: _candidate_rank(
            query_title=title,
            query_artist=artist,
            candidate=candidate,
        ),
        reverse=True,
    )

    for candidate in candidates:
        confidence = _classify_match(
            title=title,
            artist=artist,
            candidate_title=candidate["name"],
            candidate_artists=candidate["artists"],
        )

        if confidence == "high":
            return {
                **candidate,
                "confidence": "high",
            }

    for candidate in candidates:
        confidence = _classify_match(
            title=title,
            artist=artist,
            candidate_title=candidate["name"],
            candidate_artists=candidate["artists"],
        )

        if confidence == "low":
            return {
                **candidate,
                "confidence": "low",
            }

    return None
```


The ranking tuple gives the intended ordering:

Candidate	Artist match	Title form	Result
Yes — `Fragile`	Yes	Exact plain title	Highest
Yes — `Fragile (Super Deluxe)`	Yes	Descriptive suffix	High, but below plain title
Other artist — `Fragile`	No	Exact title	Low only
Other artist — `Fragile Deluxe`	No	Similar title	Low or none
Yes — unrelated album containing “Fragile”	Yes	Fuzzy title	Low unless genuinely close

One subtlety: if Spotify’s `artist:` query is too restrictive and fails to return the Yes deluxe release, issue a second broader search and merge the candidates:


```
text
def _search_spotify(title: str, artist: str):
    responses = [
        spotify.search(
            q=f"album:{title} artist:{artist}",
            type="album",
            limit=50,
        ),
        spotify.search(
            q=title,
            type="album",
            limit=50,
        ),
    ]

    by_id = {}

    for response in responses:
        for candidate in _extract_spotify_albums(response):
            by_id[candidate["id"]] = candidate

    candidates = list(by_id.values())
    candidates.sort(
        key=lambda candidate: _candidate_rank(
            query_title=title,
            query_artist=artist,
            candidate=candidate,
        ),
        reverse=True,
    )

    # Classify after merging, not before truncating.
    for confidence in ("high", "low"):
        for candidate in candidates:
            result = _classify_match(
                title=title,
                artist=artist,
                candidate_title=candidate["name"],
                candidate_artists=candidate["artists"],
            )
            if result == confidence:
                return {
                    **candidate,
                    "confidence": confidence,
                }

    return None
```


Use the broader fallback only if needed, because an unrestricted title search can produce more noise. The key is that all candidates must be ranked using **artist-first ordering**, and Spotify must not be truncated before that ranking occurs.

---
