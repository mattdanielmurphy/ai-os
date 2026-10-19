import json
import unittest

import daily

CARD = {"card_id": "c1", "prompt": "Two sentences are equivalent when…", "answer": "Same truth value always.",
        "elaboration": "", "options": json.dumps(["right", "wrong a", "wrong b", "wrong c"]), "correct_index": 0}
PLAN = {"status": "green", "streak": 3, "changes": [], "doses": {"breaths": 3, "gratitude": 1, "cards": 1, "reflection": 1}}


class DailyTest(unittest.TestCase):
    def test_shuffle_keeps_correct_answer_and_is_stable(self):
        c = daily.shuffle_card(CARD, "2026-10-18")
        self.assertEqual(c["options"][c["correct_index"]], "right")
        self.assertEqual(c, daily.shuffle_card(CARD, "2026-10-18"))

    def test_grade_right_is_good_wrong_is_again(self):
        c = daily.shuffle_card(CARD, "2026-10-18")
        right = daily.grade([c], {"c1": c["correct_index"]})[0]
        wrong = daily.grade([c], {"c1": (c["correct_index"] + 1) % 4})[0]
        self.assertEqual((right["correct"], right["rating"]), (True, 3))
        self.assertEqual((wrong["correct"], wrong["rating"]), (False, 1))
        self.assertEqual(daily.grade([c], {}), [])

    def test_seed_shows_comic_image_when_downloaded(self):
        with_img = daily.thread_seed(PLAN, [], [], "https://explosm.net/comics/x", "2026-10-18",
                                     comic_image="/data/comic-2026-10-18.png")
        self.assertIn("SendUserFile", with_img)
        self.assertIn("/data/comic-2026-10-18.png", with_img)
        without = daily.thread_seed(PLAN, [], [], "https://explosm.net/comics/x", "2026-10-18")
        self.assertNotIn("SendUserFile", without)
        self.assertIn("Today's comic: https://explosm.net/comics/x", without)

    def test_one_card_per_question_call(self):
        cards = [daily.shuffle_card({**CARD, "card_id": f"c{i}"}, "d") for i in range(5)]
        batches = daily.card_questions(cards)
        self.assertEqual([len(b["questions"]) for b in batches], [1] * len(cards))
        self.assertTrue(all(len(q["header"]) <= 12 for b in batches for q in b["questions"]))

    def test_seed_has_no_unfilled_fields(self):
        seed = daily.thread_seed(PLAN, [{"when": "9:00 AM", "what": "Class"}],
                                 [daily.shuffle_card(CARD, "2026-10-18")], None, "2026-10-18")
        self.assertNotRegex(seed, r"\{[a-z_]+\}")
        self.assertIn("9:00 AM Class", seed)
        self.assertIn("daily.py finish --date 2026-10-18", seed)


if __name__ == "__main__":
    unittest.main()
