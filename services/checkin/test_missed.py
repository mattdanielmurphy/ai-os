import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

(Path(__file__).resolve().parent / "tmp").mkdir(exist_ok=True)
TMP = tempfile.mkdtemp(dir=Path(__file__).resolve().parent / "tmp")
os.environ["CHECKIN_DATA"] = TMP
os.environ["HABIT_GATE_DATA"] = TMP

import missed  # noqa: E402


def days(d):
    Path(TMP, "days.json").write_text(json.dumps(d))


def history(*recs):
    Path(TMP, "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))


class MissedTest(unittest.TestCase):
    def setUp(self):
        for f in Path(TMP).glob("*"):
            shutil.rmtree(f) if f.is_dir() else f.unlink()
        self.sent = []
        days({"2026-10-23": {"sent_at": "2026-10-23T07:52:34"}, "2026-10-24": {"sent_at": "2026-10-24T07:52:42"},
              "2026-10-25": {"sent_at": "2026-10-25T07:53:10"}})
        history({"date": "2026-10-22", "breaths": 3}, {"date": "2026-10-23", "study": 5})

    def tick(self, when):
        return missed.tick(datetime.fromisoformat(when), send=self.sent.append)

    def test_streak_ignores_study_only_days(self):
        self.assertEqual(missed.streak("2026-10-25"), 2)
        history({"date": "2026-10-24", "cards": 3})
        self.assertEqual(missed.streak("2026-10-25"), 0)

    def test_resends_once_after_crossword(self):
        self.assertFalse(self.tick("2026-10-25T09:02")["resent"])  # crossword just went out
        r = self.tick("2026-10-25T09:10")
        self.assertTrue(r["resent"])
        self.assertTrue(self.sent[0].rstrip().endswith(missed.daily.ARTIFACT_URL))  # links stay last
        self.assertIn("missed 2 days", self.sent[0])
        self.assertFalse(self.tick("2026-10-25T09:20")["resent"])
        self.assertEqual(len(self.sent), 1)

    def test_no_resend_late_in_day(self):
        self.assertFalse(self.tick("2026-10-25T21:30")["resent"])

    def test_no_resend_once_started_or_sent_late(self):
        missed.daily._save_day(TMP, "2026-10-25", started_at="2026-10-25T08:30:00")
        self.assertFalse(self.tick("2026-10-25T09:10")["resent"])
        days({"2026-10-25": {"sent_at": "2026-10-25T09:30:00"}})  # job ran after the crossword
        self.assertFalse(self.tick("2026-10-25T09:40")["resent"])

    def test_nudge_once_until_cutoff(self):
        os.environ["CHECKIN_NOW"] = "2026-10-25T18:00"
        self.assertIsNone(missed.nudge())
        os.environ["CHECKIN_NOW"] = "2026-10-25T10:00"
        ctx = missed.nudge()
        self.assertIn("CHECK-IN NUDGE", ctx)
        self.assertIn("missed 2 days", ctx)
        self.assertIsNone(missed.nudge())

    def test_started_cli_stops_nudge(self):
        os.environ["CHECKIN_NOW"] = "2026-10-25T10:00"
        missed.main(["missed.py", "started"])
        self.assertIsNone(missed.nudge())


if __name__ == "__main__":
    unittest.main()
