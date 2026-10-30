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
        self.assertEqual(plans[0]["doses"], {"meditation": 1, "breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1})  # Sunday

    def test_weekday_habit_only_on_its_days(self):
        _, plans = simulate(["hit"] * 7)  # Sun Oct 18 .. Sat Oct 24
        self.assertEqual([("study" in p["doses"]) for p in plans], [False, True, True, True, True, True, False])
        step = next(s for s in plans[1]["steps"] if s["habit"] == "study")
        self.assertEqual((step["dose"], step["when"]), (5, "afternoon"))

    def test_weekends_dont_block_weekday_habit_growth(self):
        state, _ = simulate(["hit"] * 31)
        self.assertTrue(any(e["kind"] == "up" and e["habit"] == "study" for e in state["events"]))

    def test_skipped_study_twice_eases_it(self):
        def day(i, study):
            r = {"breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1}
            return dict(r, study=study) if 0 < i % 7 < 6 else r
        state, plans = simulate([day(i, 20) for i in range(15)] + [day(15, 0), day(16, 0), day(17, 20)])
        self.assertLess(plans[17]["doses"]["study"], plans[16]["doses"]["study"])
        self.assertTrue(any("Lunch, then study in SUB eased" in c for c in plans[17]["changes"]))
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
        shared = [e for e in state["events"] if e["habit"] != "study"]  # study grows on its own clock
        ups = [e for e in shared if e["kind"] == "up"]
        unlocks = [e for e in shared if e["kind"] == "unlock"]
        self.assertGreaterEqual(len(ups), 2)
        self.assertGreaterEqual(len(unlocks), 1)
        change_days = sorted({e["date"] for e in shared})
        gaps = [(date.fromisoformat(b) - date.fromisoformat(a)).days for a, b in zip(change_days, change_days[1:])]
        self.assertTrue(all(g >= 7 for g in gaps), gaps)

    def test_one_miss_undoes_the_last_increase(self):
        state, plans = simulate(["hit"] * 8 + [None, "hit"])
        grew = plans[7]
        self.assertEqual(grew["changes"][0], "Gratitude goes up to 2 things.")
        self.assertIn("Guided meditation goes up to 2 minutes.", grew["changes"])
        after = plans[9]
        self.assertEqual(after["status"], "red")
        self.assertEqual(after["doses"]["meditation"], 1)  # the newest growth is undone first
        # growth frozen for a week after the miss
        state, plans = simulate(["hit"] * 8 + [None] + ["hit"] * 7)
        self.assertFalse(any(p["changes"] for p in plans[10:16]))

    def test_two_misses_is_panic_and_drops_to_floor(self):
        _, plans = simulate(["hit"] * 8 + [None, None, "hit"])
        p = plans[10]
        self.assertEqual(p["status"], "panic")
        self.assertEqual({k: v for k, v in p["doses"].items() if k != "study"},
                         {"meditation": 1, "breaths": 1, "gratitude": 1, "cards": 1, "reflection": 1})

    def test_meditation_grows_weekly_and_drops_back(self):
        state, plans = simulate(["hit"] * 22)
        self.assertEqual([plans[i]["doses"]["meditation"] for i in (0, 7, 14, 21)], [1, 2, 3, 5])
        _, plans = simulate(["hit"] * 15 + [None, None, "hit"])  # two missed days: back to one minute
        self.assertEqual(plans[17]["doses"]["meditation"], 1)

    def test_meditation_stopped_early_twice_eases_it(self):
        day = lambda m: {"meditation": m, "breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1}
        _, plans = simulate(["hit"] * 8 + [day(1), day(1), "hit"])
        self.assertEqual(plans[8]["doses"]["meditation"], 2)
        self.assertEqual(plans[10]["doses"]["meditation"], 1)

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
