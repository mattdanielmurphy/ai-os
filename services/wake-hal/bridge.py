#!/usr/bin/env python3
"""
services/wake-hal/bridge.py
TypeWhisper -> aios triage bridge.

Watches TypeWhisper's SQLite transcription database (history.store) for new transcripts,
or receives transcripts via local HTTP webhook, strips wake words, and routes to
aios triage (/Users/matt/projects/ai-os/bin/triage-launcher.sh).
"""

import sys
import os
import time
import sqlite3
import subprocess
import threading
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("wake-hal-bridge")

DB_PATH = Path.home() / "Library/Application Support/TypeWhisper/history.store"
TRIAGE_LAUNCHER = Path("/Users/matt/projects/ai-os/bin/triage-launcher.sh")

# Wake words to strip from transcribed output before forwarding
WAKE_PREFIXES = [
    "hal", "hey hal", "hi hal", "hello hal",
    "hey how", "how", "ai os", "ai-os"
]

def sanitize_transcript(raw_text: str) -> str:
    """Strips leading wake words / punctuation from transcript."""
    text = raw_text.strip()
    if not text:
        return ""
    
    text_lower = text.lower()
    for prefix in WAKE_PREFIXES:
        if text_lower.startswith(prefix):
            # Strip prefix and any immediately following commas/colons/spaces
            stripped = text[len(prefix):].lstrip(" ,:;-\n\t")
            if stripped:
                return stripped
    return text

def dispatch_to_triage(prompt: str):
    """Executes ai-os triage with the sanitized prompt in a detached background subprocess."""
    cleaned = sanitize_transcript(prompt)
    if not cleaned:
        logger.info("Empty prompt after sanitization; skipping dispatch.")
        return

    logger.info(f"🚀 Dispatching to aios triage: '{cleaned}'")
    try:
        subprocess.Popen(
            [str(TRIAGE_LAUNCHER), cleaned],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception as e:
        logger.error(f"Failed to launch triage: {e}")

class TypeWhisperDBWatcher:
    """Monitors TypeWhisper's history.store for new transcription records."""

    def __init__(self, db_path: Path = DB_PATH, poll_interval: float = 0.5):
        self.db_path = db_path
        self.poll_interval = poll_interval
        self.last_pk = self._get_latest_pk()
        self.active_session_expected = False
        self._running = False
        logger.info(f"TypeWhisper DB Watcher initialized. Starting at Z_PK={self.last_pk}")

    def _get_latest_pk(self) -> int:
        if not self.db_path.exists():
            return 0
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True, timeout=2.0)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(Z_PK) FROM ZTRANSCRIPTIONRECORD")
            row = cursor.fetchone()
            conn.close()
            return row[0] if (row and row[0] is not None) else 0
        except Exception as e:
            logger.debug(f"DB read exception: {e}")
            return 0

    def expect_wake_session(self):
        """Called by daemon.py when 'Hal' is detected, flagging the next transcript for triage dispatch."""
        self.active_session_expected = True
        logger.info("Wake word armed: awaiting next TypeWhisper transcription...")

    def run(self):
        self._running = True
        while self._running:
            try:
                latest_pk = self._get_latest_pk()
                if latest_pk > self.last_pk:
                    conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True, timeout=2.0)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT Z_PK, ZFINALTEXT, ZRAWTEXT FROM ZTRANSCRIPTIONRECORD WHERE Z_PK > ? ORDER BY Z_PK ASC",
                        (self.last_pk,)
                    )
                    rows = cursor.fetchall()
                    conn.close()

                    for pk, final_text, raw_text in rows:
                        self.last_pk = max(self.last_pk, pk)
                        transcript = (final_text or raw_text or "").strip()
                        logger.info(f"New transcript detected (PK={pk}): '{transcript}'")
                        
                        # If a wake session was initiated OR if the utterance explicitly starts with 'Hal'/'Hey Hal'
                        starts_with_hal = any(transcript.lower().startswith(p) for p in WAKE_PREFIXES)
                        if self.active_session_expected or starts_with_hal:
                            self.active_session_expected = False
                            dispatch_to_triage(transcript)

                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in DB watch loop: {e}")
                time.sleep(1.0)

def main():
    watcher = TypeWhisperDBWatcher()
    watcher.run()

if __name__ == "__main__":
    main()
