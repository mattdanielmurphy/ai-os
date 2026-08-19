---
title: "Update Gemini Search Query"
date: "2026-08-14"
conversation_id: "6604dbc7-e1bf-4631-8f06-d5a3ee189f0a"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua`:

Update `searchThreads(query)` so that it searches BOTH:
1. Full-text messages via `messages_fts`
2. Session titles directly via `sessions.title LIKE ?`

Use this robust query:
```lua

local term = "%" .. query:gsub("'", "''") .. "%"
local terms = {}
for word in query:gmatch("%S+") do
    local clean = word:gsub("[^%w_-]", "")
    if #clean > 0 then
        table.insert(terms, clean .. "*")
    end
end
local ftsQuery = table.concat(terms, " ")

local sql = [[
    SELECT s.id, s.title, (strftime('%Y-%m-%d', datetime(s.started_at, 'unixepoch', 'localtime')) || '  ' || coalesce(f.snip, '[Title Match]')) as subText, coalesce(f.rank, 0) as score
    FROM sessions s
    LEFT JOIN (
        SELECT m.session_id, snippet(messages_fts, 0, '»', '«', '...', 12) as snip, rank
        FROM messages_fts
        JOIN messages m ON messages_fts.rowid = m.rowid
        WHERE messages_fts MATCH ?
    ) f ON s.id = f.session_id
    WHERE s.source = 'gemini-archive' AND (f.session_id IS NOT NULL OR s.title LIKE ?)
    GROUP BY s.id
    ORDER BY (case when s.title LIKE ? then -100 else 0 end) + score ASC
    LIMIT 35;
]]
local stmt = db:prepare(sql)
if stmt then
    stmt:bind_values(ftsQuery, term, term)
    for row in stmt:nrows() do
        table.insert(results, {
            text = row.title or "Untitled Thread",
            subText = row.subText or "",
            id = row.id
        })
    end
    stmt:finalize()
end
```

Also ensure that when `ftsQuery == ""`, it just runs `SELECT id, title, strftime('%Y-%m-%d %H:%M', datetime(started_at, 'unixepoch', 'localtime')) as dt FROM sessions WHERE source = 'gemini-archive' AND title LIKE ? ORDER BY started_at DESC LIMIT 30;` with `term`.

Update `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua`.

</span>



<span title="Responded at 1:27am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua` file has been updated. The `searchThreads(query)` function now correctly handles both full-text searches (via `messages_fts`) and session title searches (`sessions.title LIKE ?`) using the requested robust query structure.
Additionally, the empty query case has been updated to filter by `title LIKE ?` for consistency and performance as specified.

</span>



</span>

</span>