#!/usr/bin/env python3
"""CLI wrapper around triage_router.open_gemini_webview_thread.

Dispatches a prompt directly to the ai-os Gemini webview (via the local
Tauri HTTP server, or by launching the app with a pending prompt).

Usage:
    open_webview.py "your prompt text"
    echo "some text" | open_webview.py
    open_webview.py -f notes.txt -f report.pdf "summarize these"
    open_webview.py -t "inline text" -f image.png
    open_webview.py --model "Gemini 3.1 Pro (High)" "prompt"

Options:
    -t, --text TEXT      Inline prompt text (repeatable; joined with newlines).
    -f, --file PATH      File(s) to include. Any file type is read as text when
                         possible; binary files are embedded as a base64 data
                         URI so the model can still receive them.
    -m, --model MODEL    Optional model override passed to the webview.
    -h, --help           Show this help.
"""
import argparse
import base64
import sys
from pathlib import Path

# Make the sibling triage_router importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from triage_router import open_gemini_webview_thread


def read_stdin():
    """Read all of stdin as text."""
    return sys.stdin.read()


def read_file(path):
    """Read a file, returning (label, content).

    Text-ish files are read as UTF-8 text. Binary files are embedded as a
    base64 data URI so the model can still access the raw bytes.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    data = p.read_bytes()

    # Try to decode as text; fall back to base64 data URI for binary content.
    try:
        text = data.decode("utf-8")
        return str(p), text
    except UnicodeDecodeError:
        b64 = base64.b64encode(data).decode("ascii")
        return str(p), f"[binary file: {p.name}]\ndata:{p.suffix or 'application/octet-stream'};base64,{b64}"


def build_query(texts, files):
    """Assemble the final prompt from inline text and file contents."""
    parts = []

    for path in files:
        label, content = read_file(path)
        parts.append(f"===== FILE: {label} =====\n{content}")

    if texts:
        parts.append("\n".join(texts))

    return "\n\n".join(parts).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Dispatch a prompt to the ai-os Gemini webview.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-t", "--text", action="append", default=[],
                        help="Inline prompt text (repeatable).")
    parser.add_argument("-f", "--file", action="append", default=[],
                        help="File to include (repeatable, any type).")
    parser.add_argument("-m", "--model", default=None,
                        help="Optional model override.")
    parser.add_argument("text", nargs="*",
                        help="Free-form prompt text (all bare args are joined).")
    args = parser.parse_args()

    texts = list(args.text)
    if args.text:
        texts.append(" ".join(args.text))

    # If no inline text was given, fall back to piping from stdin when it's
    # not an interactive terminal.
    if not texts and not sys.stdin.isatty():
        piped = read_stdin().strip()
        if piped:
            texts.append(piped)

    query = build_query(texts, args.file)

    if not query:
        parser.error("No prompt provided. Pass text, pipe stdin, or use -f/--file.")

    open_gemini_webview_thread(query, model=args.model)


if __name__ == "__main__":
    main()
