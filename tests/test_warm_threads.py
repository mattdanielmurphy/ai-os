"""python3 -m pytest tests/test_warm_threads.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import warm_threads as W  # noqa: E402

WAKE = ('@"/Users/matt/.claude/uploads/x/img.png" <wake reason="mention">'
        '<project id="chan_01CUPXyY9oUwKVDFREVDpYDr" type="project"><thread ts="cmsg_01CUPXyY9oUwKVDFREVDpYDrROOT">'
        '<message trigger="true" from="human">Why isn&#39;t this flashing?</message></thread></project></wake>')


def test_clean_title_drops_path_and_envelope():
    assert W.clean_title(WAKE) == "Why isn't this flashing?"


def test_scan_finds_thread_link(tmp_path):
    f = tmp_path / "s.jsonl"
    rows = [
        {"type": "user", "message": {"content": WAKE}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "t1", "name": "mcp__hearthbot__reply", "input": {"text": "Fixed. Try it?"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1",
                                                 "content": '{"thread_id":"cmsg_01CUPXyY9oUwKVDFREVDpYDrOTHER"}'}]}},
    ]
    f.write_text("\n".join(json.dumps(r) for r in rows))
    title, asked, url = W.scan(f)
    assert title == "Why isn't this flashing?"
    assert asked is True
    assert url == "claude://claude.ai/epitaxy/project/chan_01CUPXyY9oUwKVDFREVDpYDr?thread=cmsg_01CUPXyY9oUwKVDFREVDpYDrROOT"
