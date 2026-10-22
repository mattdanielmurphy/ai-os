import json
import os
import shutil
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
            shutil.rmtree(f) if f.is_dir() else f.unlink()

    def history(self):
        return ladder.read_history(TMP)

    def test_holds_matt_prompt_in_afternoon(self):
        ctx = run("fix the mixer")
        self.assertIn("HABIT GATE", ctx)
        self.assertIn("habit_gate.py page", ctx)  # first rungs are a fixed card bank
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


    def test_ladder_starts_with_symbol_bank(self):
        self.assertIn(" page`", run("hi"))
        os.environ["HABIT_GATE_NOW"] = "2026-10-22T15:00"
        cfg = ladder.load_config()
        out = habit_gate.build_page(cfg, ladder.read_state(cfg, TMP), habit_gate.now())
        cards = json.loads((Path(TMP) / "practice" / "2026-10-22.json").read_text())
        self.assertEqual([c["card_id"] for c in cards][:2], ["sym_forall", "sym_exists"])
        self.assertIn("What does ∀ mean?", out.read_text())

    def test_ladder_moves_only_when_solid(self):
        ids = [c["card_id"] for c in habit_gate.load_rungs()["rungs"][0]["cards"]]
        doc = lambda ok, bad=(): {"reviews": [{"card_id": i, "correct": True} for i in ok]
                                  + [{"card_id": i, "correct": False} for i in bad]}
        self.assertEqual(habit_gate.score(doc(ids[:5]), "d1")["rung"], 0)  # perfect, but not every card seen
        self.assertEqual(habit_gate.score(doc(ids[:5]), "d1")["rung"], 0)  # same day counts once
        r = habit_gate.score(doc(ids[5:7], ids[7:]), "d2")
        self.assertEqual((r["rung"], r["missed"]), (0, [ids[7]]))  # 2/3 < 80%
        self.assertEqual(habit_gate.pick_cards(habit_gate.load_rungs()["rungs"][0], r, 2)[0]["card_id"], ids[7])
        self.assertEqual(habit_gate.score(doc(ids[7:]), "d3")["rung"], 1)
        self.assertEqual(habit_gate.score(doc([], ["word_every", "word_some"]), "d4")["rung"], 0)  # rough page: back one


if __name__ == "__main__":
    unittest.main()
