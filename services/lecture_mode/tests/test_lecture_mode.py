# services/lecture_mode/tests/test_lecture_mode.py
from datetime import datetime
from pathlib import Path
import tempfile
import pytest
from starlette.testclient import TestClient

from services.lecture_mode.config import LectureConfig
from services.lecture_mode.engine import LectureEngine
from services.lecture_mode.note_syncer import LectureNoteSyncer
from services.lecture_mode.server import create_app
from services.lecture_mode.slide_parser import (
    build_whisper_initial_prompt,
    extract_terms_of_art,
)
from services.lecture_mode.transcript_store import TranscriptStore


def test_slide_terms_of_art_extraction():
    sample_slide_text = """
    Department of Computing Science, University of Alberta
    CMPUT 204: Algorithms I
    Chapter 4: Graph Algorithms & Dijkstra's Algorithm

    Overview:
    Today we will analyze Single-Source Shortest Paths on directed graphs with non-negative edge weights.
    We will review Dijkstra's Algorithm, Priority Queues, Binary Heaps, and Fibonacci Heaps.
    Key properties:
    - Greedy strategy: repeatedly extract minimum distance vertex from V - S.
    - Time complexity: O((V + E) log V) using a standard Binary Min-Heap.
    - Relaxation step: if d[u] + w(u, v) < d[v] then d[v] = d[u] + w(u, v).
    Comparison with Bellman-Ford: Bellman-Ford handles negative edge weights in O(V * E) time.
    """

    terms = extract_terms_of_art(sample_slide_text)
    assert len(terms) > 5

    # Check that high-level technical terms are extracted
    terms_str = " ".join(terms)
    assert any("Dijkstra" in t for t in terms)
    assert any("Algorithm" in t for t in terms)
    assert any("Binary" in t for t in terms)
    assert any("Heap" in t or "Heaps" in t for t in terms)

    # Check prompt builder
    prompt = build_whisper_initial_prompt(terms, max_chars=120)
    assert len(prompt) <= 120
    assert "," in prompt


def test_transcript_store():
    store = TranscriptStore(course_name="CMPUT 204")

    # Add segments
    seg1 = store.add_segment(0.0, 5.2, "Good afternoon everyone, welcome to class.")
    seg2 = store.add_segment(5.5, 12.0, "Today we will study Dijkstra's algorithm for shortest paths.")
    seg3 = store.add_segment(65.0, 72.0, "Notice how the relaxation step updates the vertex distance.")

    assert seg1.timestamp_str == "[00:00]"
    assert seg2.timestamp_str == "[00:05]"
    assert seg3.timestamp_str == "[01:05]"
    assert len(store.get_all()) == 3

    # Test scrollback filtering (last 60s from latest segment at 72s -> cutoff 12s)
    recent = store.get_recent(seconds_back=60.0)
    assert len(recent) == 2  # seg2 (ends 12.0) and seg3 (ends 72.0)
    assert recent[-1].id == seg3.id

    # Test search
    search_res = store.search("Dijkstra")
    assert len(search_res) == 1
    assert search_res[0].id == seg2.id

    # Test markdown formatting
    md = store.to_markdown()
    assert "- **[00:00]** Good afternoon" in md
    assert "- **[00:05]** Today we will study" in md

    # Test JSON export
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "transcript.json"
        store.save_json(json_path)
        assert json_path.exists()
        assert "CMPUT 204" in json_path.read_text()


def test_note_syncer():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        syncer = LectureNoteSyncer(vault_path=vault, lectures_subpath="Lectures")

        terms = ["Dijkstra's Algorithm", "Binary Heap", "Relaxation Step"]
        test_date = datetime(2026, 9, 18, 14, 0)
        note_path = syncer.init_lecture_note("CMPUT 204", terms, date=test_date)

        assert note_path.exists()
        content = note_path.read_text(encoding="utf-8")
        assert "# CMPUT 204 — 2026-09-18" in content
        assert "`Dijkstra's Algorithm`" in content
        assert "## 📝 Live Notes" in content

        # Simulate user writing notes
        content_with_notes = content.replace(
            "## 📝 Live Notes\n- ",
            "## 📝 Live Notes\n- Proof of correctness uses induction on visited set size S.",
        )
        note_path.write_text(content_with_notes, encoding="utf-8")

        # Finalize note with transcript
        sample_transcript = (
            "- **[00:00]** Welcome to class\n- **[01:15]** The queue invariant is maintained"
        )
        syncer.finalize_lecture_note(
            course_name="CMPUT 204",
            transcript_markdown=sample_transcript,
            audio_path=vault / "audio.wav",
            date=test_date,
        )

        final_content = note_path.read_text(encoding="utf-8")
        # Verify user's notes were PRESERVED!
        assert "Proof of correctness uses induction" in final_content
        # Verify transcript was added in callout
        assert "> [!quote]- Full Audio-Synced Transcript" in final_content
        assert "> - **[00:00]** Welcome to class" in final_content
        assert "> - **[01:15]** The queue invariant is maintained" in final_content
        assert "audio.wav" in final_content


@pytest.mark.asyncio
async def test_lecture_engine_lifecycle_mock():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cfg = LectureConfig(
            obsidian_vault_path=tmp_path / "vault",
            temp_dir=tmp_path / "staging",
            chunk_duration_seconds=5,
        )
        engine = LectureEngine(config=cfg, mock=True)
        engine.set_terms_of_art(["Dijkstra", "Min-Heap"])

        # Start lecture
        start_res = await engine.start_lecture(
            course_name="CMPUT 204",
            engage_hammerspoon_lock=False,
        )
        assert start_res["status"] == "started"
        assert engine.is_running is True
        assert engine.active_course == "CMPUT 204"

        # Manually inject a segment into the store
        engine.store.add_segment(0.0, 4.5, "Testing mock audio segment")
        assert len(engine.store.get_all()) == 1

        # Stop lecture
        stop_res = await engine.stop_lecture(disengage_hammerspoon_lock=False)
        assert stop_res["status"] == "stopped"
        assert engine.is_running is False
        assert stop_res["segments_count"] == 1


def test_server_hud_endpoints():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cfg = LectureConfig(
            obsidian_vault_path=tmp_path / "vault",
            temp_dir=tmp_path / "staging",
        )
        engine = LectureEngine(config=cfg, mock=True)
        app = create_app(engine=engine)
        client = TestClient(app)

        # 1. Test HUD HTML page
        resp = client.get("/")
        assert resp.status_code == 200
        assert "AI-OS Lecture HUD" in resp.text
        assert "btn-scrollback" in resp.text
        assert "btn-copy-60s" in resp.text

        # 2. Test status endpoint when idle
        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_running"] is False

        # 3. Start lecture via API
        resp = client.post(
            "/api/start",
            json={"course": "MUSIC 102", "engage_lock": False},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "started"

        # 4. Status endpoint when active
        resp = client.get("/api/status")
        data = resp.json()
        assert data["is_running"] is True
        assert data["course"] == "MUSIC 102"

        # 5. Stop lecture via API
        resp = client.post("/api/stop?disengage_lock=false")
        assert resp.status_code == 200
        assert resp.json()["status"] == "stopped"
