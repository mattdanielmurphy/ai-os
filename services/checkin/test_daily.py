import json
import tempfile
import unittest
from pathlib import Path

import daily

PLAN = {"status": "green", "streak": 3, "changes": [], "doses": {"breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1}}


class DailyTest(unittest.TestCase):
    def test_seed_shows_comic_image_when_downloaded(self):
        with_img = daily.thread_seed(PLAN, [], "https://explosm.net/comics/x", "2026-10-18",
                                     comic_image="/data/comic-2026-10-18.png")
        self.assertIn("SendUserFile", with_img)
        self.assertIn("/data/comic-2026-10-18.png", with_img)
        without = daily.thread_seed(PLAN, [], "https://explosm.net/comics/x", "2026-10-18")
        self.assertNotIn("SendUserFile", without)
        self.assertIn("Today's comic: https://explosm.net/comics/x", without)

    def test_seed_has_no_unfilled_fields_and_no_menus(self):
        seed = daily.thread_seed(PLAN, [{"when": "9:00 AM", "what": "Class"}], None, "2026-10-18")
        self.assertNotRegex(seed, r"\{[a-z_]+\}")
        self.assertIn("9:00 AM Class", seed)
        self.assertIn("ladder.py record --date 2026-10-18 reflection=", seed)
        self.assertIn("Never use the AskUserQuestion tool", seed)

    def test_record_from_page_doc(self):
        doc = {"breaths": 3, "gratitude": "Mia", "reviews": [{"card_id": "c1", "rating": 2}], "extras": {"water": 1}}
        self.assertEqual(daily.record_from_checkin(doc, {}, 5), {"breaths": 3, "meditation": 0, "gratitude": 1, "cards": 1, "water": 1})
        self.assertEqual(daily.record_from_checkin({**doc, "meditation": 2}, {}, 5)["meditation"], 2)
        self.assertEqual(daily.record_from_checkin({**doc, "meditation": True}, {}, 5)["meditation"], 0)
        # Mistapped cards are skipped, never counted or sent to the deck.
        self.assertEqual(daily.record_from_checkin({**doc, "skipped": ["c2"]}, {}, 5)["cards"], 1)
        # No cards due that day counts as hitting the dose.
        self.assertEqual(daily.record_from_checkin({}, {"cards": 2}, 0)["cards"], 2)

    def test_load_checkin_unwraps_artifactdata_file(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "c.json"
            f.write_text(json.dumps({"id": "2026-10-18", "data": {"breaths": 2}, "version": 3}))
            self.assertEqual(daily.load_checkin(f), {"breaths": 2})
            self.assertIsNone(daily.load_checkin(Path(d) / "missing.json"))

    def test_gratitude_logged_once(self):
        with tempfile.TemporaryDirectory() as vault:
            doc = {"gratitude": "Mia and\nthe smart lights"}
            self.assertTrue(daily.log_gratitude(doc, "2026-10-18", vault))
            self.assertFalse(daily.log_gratitude(doc, "2026-10-18", vault))
            text = (Path(vault) / "habits/logs/2026-10-18.md").read_text()
            self.assertEqual(text.count("- Grateful for: Mia and the smart lights"), 1)
            self.assertFalse(daily.log_gratitude({"gratitude": " "}, "2026-10-18", vault))

    def test_mix_subjects_interleaves_and_rotates(self):
        cards = [{"card_id": f"forallx_ch0{i}_q01"} for i in range(5)] + \
                [{"card_id": "music_cello_01"}, {"card_id": "music_cello_02"}, {"card_id": "ai_arch_01"}]
        mixed = daily.mix_subjects(cards, "2026-10-20", weights={})
        first3 = {daily.subject(c["card_id"]) for c in mixed[:3]}
        self.assertEqual(first3, {"forallx", "music", "ai"})
        self.assertEqual(len(mixed), len(cards))
        # within a subject, most overdue first
        logic = [c["card_id"] for c in mixed if c["card_id"].startswith("forallx")]
        self.assertEqual(logic, [c["card_id"] for c in cards[:5]])
        leads = {daily.subject(daily.mix_subjects(cards, f"2026-10-{d}", weights={})[0]["card_id"]) for d in (20, 21, 22)}
        self.assertEqual(len(leads), 3)

    def test_exam_soon_gets_more_slots_and_leads(self):
        cards = [{"card_id": f"forallx_ch0{i}_q01"} for i in range(6)] + [{"card_id": f"music102_t_{i}"} for i in range(6)]
        mixed = daily.mix_subjects(cards, "2026-10-20", weights={"music102": 3, "forallx": 1})
        self.assertEqual([daily.subject(c["card_id"]) for c in mixed[:4]], ["music102"] * 3 + ["forallx"])

    def test_exam_weights_from_dates(self):
        import tempfile, json as j
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            j.dump({"_about": "x", "a": ["2026-10-21"], "b": ["2026-10-25"], "c": ["2026-12-01"], "d": ["2026-10-01"]}, f)
        self.assertEqual(daily.exam_weights("2026-10-20", f.name), {"a": 3, "b": 2, "c": 1, "d": 1})


if __name__ == "__main__":
    unittest.main()
