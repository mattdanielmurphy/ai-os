import unittest
from datetime import date, timedelta

import ladder

START = date(2026, 10, 18)


def simulate(days, cfg=None):
    """days: list of dicts (results for that day) or None (missed). Returns plans per day."""
    cfg = cfg or ladder.load_config()
    state, history, plans = ladder.initial_state(cfg), [], []
    for i, results in enumerate(days):
        today = START + timedelta(days=i)
        state, p = ladder.plan(cfg, state, history, today)
        plans.append(p)
        if results is not None:
            rec = {"date": today.isoformat()}
            rec.update(p["doses"] if results == "hit" else results)
            history.append(rec)
    return state, plans


class LadderTest(unittest.TestCase):
    def test_starts_at_current_doses(self):
        _, plans = simulate(["hit"])
        self.assertEqual(plans[0]["doses"], {"breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1})
        self.assertEqual(plans[0]["status"], "green")

    def test_plan_is_idempotent_per_day(self):
        cfg = ladder.load_config()
        state = ladder.initial_state(cfg)
        state, a = ladder.plan(cfg, state, [], START)
        state, b = ladder.plan(cfg, state, [], START)
        self.assertEqual(a, b)
        self.assertEqual(len(state["events"]), 0)

    def test_grows_once_a_week_and_adds_a_step_within_a_month(self):
        state, plans = simulate(["hit"] * 31)
        ups = [e for e in state["events"] if e["kind"] == "up"]
        unlocks = [e for e in state["events"] if e["kind"] == "unlock"]
        self.assertGreaterEqual(len(ups), 2)
        self.assertGreaterEqual(len(unlocks), 1)
        change_days = [p["date"] for p in plans if p["changes"]]
        gaps = [(date.fromisoformat(b) - date.fromisoformat(a)).days for a, b in zip(change_days, change_days[1:])]
        self.assertTrue(all(g >= 7 for g in gaps), gaps)

    def test_one_miss_undoes_the_last_increase(self):
        state, plans = simulate(["hit"] * 8 + [None, "hit"])
        grew = plans[7]
        self.assertEqual(grew["changes"][0], "Slow breaths goes up to 4 breaths.")
        after = plans[9]
        self.assertEqual(after["status"], "red")
        self.assertEqual(after["doses"]["breaths"], 3)
        # growth frozen for a week after the miss
        state, plans = simulate(["hit"] * 8 + [None] + ["hit"] * 7)
        self.assertFalse(any(p["changes"] for p in plans[10:16]))

    def test_two_misses_is_panic_and_drops_to_floor(self):
        _, plans = simulate(["hit"] * 8 + [None, None, "hit"])
        p = plans[10]
        self.assertEqual(p["status"], "panic")
        self.assertEqual(p["doses"], {"breaths": 1, "gratitude": 1, "cards": 1, "reflection": 1})

    def test_penalty_applies_once_not_every_day(self):
        state, plans = simulate(["hit"] * 8 + [None] + ["hit"] * 3)
        undos = [e for e in state["events"] if e["kind"] == "undo"]
        self.assertEqual(len(undos), 1)
        self.assertEqual(plans[10]["status"], "green")

    def test_two_days_under_dose_eases_that_habit(self):
        under = {"breaths": 1, "gratitude": 1, "cards": 1, "reflection": 1}
        _, plans = simulate(["hit", under, under, "hit"])
        self.assertEqual(plans[3]["doses"]["breaths"], 2)
        self.assertIn("eased", plans[3]["changes"][0])


if __name__ == "__main__":
    unittest.main()
