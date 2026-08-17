---
name: _link-youtube-highlights
description: "Formats and generates YouTube video URLs with highlight reel timestamp parameters for automated segment skipping in Matt's YouTube userscript."
---

# Link YouTube Highlights

Whenever recommending, referencing, or summarizing a YouTube video for Matt, format the YouTube URL with the `highlights` query parameter. Matt's YouTube Master userscript automatically intercepts these parameters on page load, generates scrubber heatmap markers, jumps to the first highlight segment, and automatically skips non-highlight portions during playback.

## URL Syntax & Formats

The primary URL parameter is `highlights` (aliases `reel` or `segments` are also supported).

### Integer Seconds / Timestamp Intervals with Labels (Standard)
Format: `&highlights=start-end:Title,start-end:Title` (use `+` for spaces)
```markdown
[https://www.youtube.com/watch?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo](https://www.youtube.com/watch?v=VIDEO_ID&highlights=0:42-1:25:Core+Problem,2:00-2:30:Demo)
```
