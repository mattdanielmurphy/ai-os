# services/lecture_mode/server.py
import asyncio
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from services.lecture_mode.config import LectureConfig
from services.lecture_mode.engine import LectureEngine
from services.lecture_mode.transcript_store import TranscriptSegment

logger = logging.getLogger("lecture_mode.server")

def create_app(engine: Optional[LectureEngine] = None) -> FastAPI:
    config = LectureConfig()
    app_engine = engine or LectureEngine(config=config)
    app = FastAPI(title="AI-OS Lecture HUD", version="1.0.0")

    # Store active SSE subscriber queues
    sse_queues: set[asyncio.Queue] = set()

    def on_new_segment(seg: TranscriptSegment) -> None:
        payload = json.dumps(seg.to_dict())
        for q in list(sse_queues):
            try:
                q.put_nowait(payload)
            except Exception:
                pass

    app_engine.subscribe(on_new_segment)

    class StartRequest(BaseModel):
        course: str
        slide_path: Optional[str] = None
        engage_lock: bool = True

    class SlideRequest(BaseModel):
        slide_path: str

    @app.get("/api/status")
    async def get_status():
        elapsed = 0.0
        if app_engine.is_running and app_engine.start_monotonic:
            import time
            elapsed = round(time.monotonic() - app_engine.start_monotonic, 1)

        seg_count = len(app_engine.store.segments) if app_engine.store else 0
        return {
            "is_running": app_engine.is_running,
            "course": app_engine.active_course,
            "elapsed_seconds": elapsed,
            "segment_count": seg_count,
            "terms_of_art": app_engine.terms_of_art,
            "session_dir": str(app_engine.session_dir) if app_engine.session_dir else None,
        }

    @app.get("/api/transcript")
    async def get_transcript():
        if not app_engine.store:
            return {"course": None, "segments": []}
        return {
            "course": app_engine.active_course,
            "segments": app_engine.store.to_json(),
        }

    @app.get("/api/recent")
    async def get_recent(seconds: float = Query(60.0, ge=5.0, le=600.0)):
        if not app_engine.store:
            return {"segments": []}
        recent = app_engine.store.get_recent(seconds_back=seconds)
        return {"segments": [s.to_dict() for s in recent]}

    @app.get("/api/events")
    async def sse_events(request: Request):
        queue = asyncio.Queue()
        sse_queues.add(queue)

        async def event_generator():
            try:
                # Send initial ping
                yield "event: ping\ndata: {}\n\n"
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        data = await asyncio.wait_for(queue.get(), timeout=15.0)
                        yield f"event: segment\ndata: {data}\n\n"
                    except asyncio.TimeoutError:
                        # Keep-alive heartbeat
                        yield ": keepalive\n\n"
            finally:
                sse_queues.discard(queue)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.post("/api/start")
    async def start_lecture(req: StartRequest):
        res = await app_engine.start_lecture(
            course_name=req.course,
            slide_path=req.slide_path,
            engage_hammerspoon_lock=req.engage_lock,
        )
        return res

    @app.post("/api/stop")
    async def stop_lecture(disengage_lock: bool = True):
        res = await app_engine.stop_lecture(disengage_hammerspoon_lock=disengage_lock)
        return res

    @app.post("/api/slides")
    async def ingest_slides(req: SlideRequest):
        path = Path(req.slide_path).expanduser()
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Slide file not found: {path}")
        terms = app_engine.ingest_slides(path)
        return {"status": "ok", "terms": terms}

    @app.get("/", response_class=HTMLResponse)
    async def get_hud_html():
        return HTMLResponse(content=HUD_HTML_TEMPLATE, status_code=200)

    return app

HUD_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI-OS Lecture HUD</title>
<style>
  :root {
    --bg: #0d0f12;
    --surface: #15181e;
    --surface-hover: #1c212b;
    --border: #262c38;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --accent: #388bfd;
    --accent-glow: rgba(56, 139, 253, 0.15);
    --red: #f85149;
    --green: #3fb950;
    --yellow: #d29922;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background-color: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  /* Header */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-shrink: 0;
  }
  .title-area {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .live-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: var(--red);
    box-shadow: 0 0 8px var(--red);
    animation: pulse 1.8s infinite;
  }
  .live-dot.paused {
    background-color: var(--text-dim);
    box-shadow: none;
    animation: none;
  }
  @keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 12px var(--red); }
    100% { transform: scale(0.95); opacity: 0.8; }
  }
  h1 {
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.2px;
  }
  .timer-badge {
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
    color: var(--text-dim);
  }
  /* Controls */
  .controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  button {
    background: var(--surface-hover);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  button:hover {
    background: #232936;
    border-color: #3b4456;
  }
  button.active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }
  .search-input {
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    width: 180px;
  }
  .search-input:focus {
    outline: none;
    border-color: var(--accent);
  }
  /* Terms Bar */
  .terms-bar {
    background: #111419;
    border-bottom: 1px solid var(--border);
    padding: 6px 18px;
    display: flex;
    align-items: center;
    gap: 8px;
    overflow-x: auto;
    white-space: nowrap;
    flex-shrink: 0;
    scrollbar-width: thin;
  }
  .terms-label {
    font-size: 11px;
    color: var(--text-dim);
    text-transform: uppercase;
    font-weight: 600;
    margin-right: 4px;
  }
  .term-chip {
    background: rgba(56, 139, 253, 0.1);
    color: #79c0ff;
    border: 1px solid rgba(56, 139, 253, 0.3);
    padding: 1px 8px;
    border-radius: 12px;
    font-size: 11px;
    cursor: pointer;
  }
  .term-chip:hover {
    background: rgba(56, 139, 253, 0.25);
  }
  /* Transcript View */
  #transcript-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
  }
  .segment-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    transition: background 0.15s ease, border-color 0.15s ease;
    cursor: pointer;
    position: relative;
  }
  .segment-card:hover {
    background: var(--surface-hover);
    border-color: #3b4456;
  }
  .segment-card.highlight {
    border-left: 3px solid var(--accent);
    background: var(--accent-glow);
  }
  .segment-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }
  .timestamp {
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }
  .copy-hint {
    font-size: 10px;
    color: var(--text-dim);
    opacity: 0;
    transition: opacity 0.15s;
  }
  .segment-card:hover .copy-hint {
    opacity: 1;
  }
  .segment-text {
    font-size: 13.5px;
    color: var(--text);
    line-height: 1.45;
  }
  /* Empty state */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-dim);
    gap: 12px;
  }
  /* Toast */
  #toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #1f242d;
    border: 1px solid var(--accent);
    color: #fff;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 12px;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.2s ease;
    pointer-events: none;
  }
  #toast.show {
    opacity: 1;
    transform: translateY(0);
  }
</style>
</head>
<body>

<header>
  <div class="title-area">
    <div id="live-indicator" class="live-dot paused"></div>
    <h1 id="course-title">Waiting for Lecture...</h1>
    <span id="timer-badge" class="timer-badge">00:00</span>
  </div>
  <div class="controls">
    <input type="text" id="search-box" class="search-input" placeholder="Search transcript..." />
    <button id="btn-scrollback" title="Pause autoscroll so you can read previous statements">⏸️ Scrollback Mode</button>
    <button id="btn-copy-60s" title="Copy last 60 seconds formatted for Obsidian">📋 Copy Last 60s</button>
    <button id="btn-copy-all" title="Copy entire transcript formatted for Obsidian">📑 Copy All</button>
  </div>
</header>

<div id="terms-bar" class="terms-bar" style="display: none;">
  <span class="terms-label">Slide Terms:</span>
  <div id="terms-list" style="display: inline-flex; gap: 6px;"></div>
</div>

<main id="transcript-container">
  <div class="empty-state" id="empty-state">
    <div style="font-size: 32px;">🎙️</div>
    <div>Lecture Audio & Live Transcript HUD ready.</div>
    <div style="font-size: 12px;">Start a lecture using <code>aios-lecture start &lt;course&gt;</code> or click below.</div>
  </div>
</main>

<div id="toast">Copied to clipboard!</div>

<script>
  let isScrollback = false;
  let allSegments = [];
  let elapsedSeconds = 0;
  let timerInterval = null;

  const container = document.getElementById('transcript-container');
  const emptyState = document.getElementById('empty-state');
  const courseTitle = document.getElementById('course-title');
  const timerBadge = document.getElementById('timer-badge');
  const liveIndicator = document.getElementById('live-indicator');
  const btnScrollback = document.getElementById('btn-scrollback');
  const btnCopy60s = document.getElementById('btn-copy-60s');
  const btnCopyAll = document.getElementById('btn-copy-all');
  const searchBox = document.getElementById('search-box');
  const termsBar = document.getElementById('terms-bar');
  const termsList = document.getElementById('terms-list');
  const toast = document.getElementById('toast');

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2000);
  }

  function formatDuration(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = Math.floor(sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  function renderCard(seg) {
    if (emptyState) emptyState.style.display = 'none';

    const card = document.createElement('div');
    card.className = 'segment-card';
    card.dataset.id = seg.id;
    card.dataset.start = seg.start_seconds;
    card.dataset.text = seg.text;

    card.innerHTML = `
      <div class="segment-header">
        <span class="timestamp">${seg.timestamp_str}</span>
        <span class="copy-hint">Click to copy markdown</span>
      </div>
      <div class="segment-text">${escapeHtml(seg.text)}</div>
    `;

    card.addEventListener('click', () => {
      const md = `> **${seg.timestamp_str}** "${seg.text}"`;
      navigator.clipboard.writeText(md);
      showToast(`Copied: ${seg.timestamp_str}`);
    });

    container.appendChild(card);

    if (!isScrollback) {
      container.scrollTop = container.scrollHeight;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Toggle Scrollback Mode
  btnScrollback.addEventListener('click', () => {
    isScrollback = !isScrollback;
    btnScrollback.classList.toggle('active', isScrollback);
    btnScrollback.innerHTML = isScrollback ? '▶️ Resume Autoscroll' : '⏸️ Scrollback Mode';
    if (!isScrollback) {
      container.scrollTop = container.scrollHeight;
      showToast('Autoscroll resumed');
    } else {
      showToast('Scrollback paused at current line');
    }
  });

  // Copy Last 60s
  btnCopy60s.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/recent?seconds=60');
      const data = await res.json();
      if (!data.segments || data.segments.length === 0) {
        showToast('No speech in the last 60 seconds');
        return;
      }
      const lines = data.segments.map(s => `> **${s.timestamp_str}** "${s.text}"`).join('\\n');
      await navigator.clipboard.writeText(lines);
      showToast(`Copied ${data.segments.length} segments from last 60s`);
    } catch (e) {
      showToast('Error copying recent segments');
    }
  });

  // Copy All
  btnCopyAll.addEventListener('click', () => {
    if (allSegments.length === 0) {
      showToast('Transcript is empty');
      return;
    }
    const lines = allSegments.map(s => `> **${s.timestamp_str}** "${s.text}"`).join('\\n');
    navigator.clipboard.writeText(lines);
    showToast(`Copied full transcript (${allSegments.length} segments)`);
  });

  // Search Filter
  searchBox.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    const cards = container.querySelectorAll('.segment-card');
    cards.forEach(card => {
      const text = card.dataset.text.toLowerCase();
      if (!q || text.includes(q)) {
        card.style.display = '';
        card.classList.toggle('highlight', !!q && text.includes(q));
      } else {
        card.style.display = 'none';
        card.classList.remove('highlight');
      }
    });
  });

  // Connect SSE
  function initSSE() {
    const es = new EventSource('/api/events');
    es.addEventListener('segment', (e) => {
      try {
        const seg = JSON.parse(e.data);
        allSegments.push(seg);
        renderCard(seg);
      } catch (err) {
        console.error('Failed to parse segment:', err);
      }
    });
    es.onerror = () => {
      setTimeout(initSSE, 3000);
    };
  }

  // Poll status periodically
  async function checkStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (data.is_running) {
        courseTitle.textContent = data.course || 'Active Lecture';
        liveIndicator.classList.remove('paused');
        elapsedSeconds = data.elapsed_seconds;
        timerBadge.textContent = formatDuration(elapsedSeconds);

        if (data.terms_of_art && data.terms_of_art.length > 0) {
          termsBar.style.display = 'flex';
          termsList.innerHTML = data.terms_of_art.slice(0, 15).map(t => 
            `<span class="term-chip" onclick="searchBox.value='${escapeHtml(t)}'; searchBox.dispatchEvent(new Event('input'))">${escapeHtml(t)}</span>`
          ).join('');
        }
      } else {
        liveIndicator.classList.add('paused');
        if (allSegments.length === 0) {
          courseTitle.textContent = 'Lecture Paused / Ready';
        }
      }
    } catch (e) {
      console.warn('Status poll error:', e);
    }
  }

  // Initial load
  async function init() {
    await checkStatus();
    try {
      const res = await fetch('/api/transcript');
      const data = await res.json();
      if (data.segments && data.segments.length > 0) {
        allSegments = data.segments;
        data.segments.forEach(renderCard);
      }
    } catch (e) {}

    initSSE();
    setInterval(checkStatus, 3000);
    setInterval(() => {
      if (!liveIndicator.classList.contains('paused')) {
        elapsedSeconds += 1;
        timerBadge.textContent = formatDuration(elapsedSeconds);
      }
    }, 1000);
  }

  init();
</script>
</body>
</html>
"""

def run_server(host: str = "127.0.0.1", port: int = 4141, engine: Optional[LectureEngine] = None):
    import uvicorn
    app = create_app(engine=engine)
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_server()
