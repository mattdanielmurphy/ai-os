import json
import os
import tempfile
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp(dir=Path(__file__).resolve().parent / "tmp")
os.environ["HABIT_GATE_DATA"] = TMP

import habit_gate  # noqa: E402
import ladder  # noqa: E402

WAKE = ('<wake reason="mention"><project><message trigger="true" from="{who}" id="x">{text}</message>'
        '</project></wake>')


def run(prompt, when="2026-10-22T15:00"):  # a Thursday
    os.environ["HABIT_GATE_NOW"] = when
    return habit_gate.hook({"prompt": prompt})


class GateTest(unittest.TestCase):
    def setUp(self):
        for f in Path(TMP).glob("*"):
            f.unlink()

    def history(self):
        return ladder.read_history(TMP)

    def test_holds_matt_prompt_in_afternoon(self):
        ctx = run("fix the mixer")
        self.assertIn("HABIT GATE", ctx)
        self.assertIn("5 minutes", ctx)
        self.assertIn("Reply 👍 when done", ctx)

    def test_morning_weekend_and_agents_pass(self):
        self.assertIsNone(run("hi", when="2026-10-22T11:00"))
        self.assertIsNone(run("hi", when="2026-10-24T15:00"))  # Saturday
        self.assertIsNone(run(WAKE.format(who="agent", text="hi")))
        self.assertIsNone(run('<relay from="coordinator">do x</relay>'))
        self.assertIsNone(run("<side-sessions-event>done</side-sessions-event>"))

    def test_project_thread_message_is_held(self):
        self.assertIn("HABIT GATE", run(WAKE.format(who="human", text="build it")))

    def test_thumbs_up_reaction_records_dose_and_unlocks(self):
        run("hi")
        ctx = run('<wake reason="reactions"><reaction emoji="👍" /></wake>')
        self.assertIn("Unlocked", ctx)
        self.assertEqual(self.history()[-1]["study"], 5)
        self.assertIsNone(run("now help me"))

    def test_done_text_in_thread(self):
        self.assertIn("Unlocked", run(WAKE.format(who="human", text="Done!")))
        self.assertIsNone(run("next"))

    def test_skip_records_zero(self):
        self.assertIn("Unlocked", run("skip"))
        self.assertEqual(self.history()[-1]["study"], 0)
        self.assertIsNone(run("next"))

    def test_other_reactions_dont_unlock(self):
        self.assertIsNone(run('<wake reason="reactions"><reaction emoji="❓" /></wake>'))
        self.assertIn("HABIT GATE", run("hi"))

    def test_saved_url_is_reused(self):
        os.environ["HABIT_GATE_NOW"] = "2026-10-22T15:00"
        habit_gate.main(["x", "url", "https://claude.ai/artifact/abc"])
        self.assertIn("https://claude.ai/artifact/abc", run("hi"))
        self.assertIn("HABIT GATE", run("hi", when="2026-10-23T15:00"))
        self.assertNotIn("artifact/abc", run("hi", when="2026-10-23T15:00"))

    def test_already_recorded_by_checkin_passes(self):
        ladder.append_record({"date": "2026-10-22", "study": 10}, TMP)
        self.assertIsNone(run("hi"))


if __name__ == "__main__":
    unittest.main()
