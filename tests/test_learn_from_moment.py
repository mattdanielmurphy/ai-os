import unittest
import os
from pathlib import Path
from scripts.learn_from_moment import resolve_repo_root, guard_skill_path, classify_destination

class TestLearnFromMoment(unittest.TestCase):
    def test_resolve_repo_root(self):
        # Assuming current dir is /Users/matt/projects/ai-os
        root = resolve_repo_root(os.getcwd())
        self.assertTrue(root.exists())
        self.assertTrue((root / ".git").exists() or (root / "AG_CONTEXT.md").exists())

    def test_guard_skill_path(self):
        # Should raise for builtin
        with self.assertRaises(PermissionError):
            guard_skill_path(Path("/Users/matt/.gemini/antigravity/builtin/some-skill"))
        # Should pass for custom
        guard_skill_path(Path("/Users/matt/projects/ai-os/skills/custom-skills/my-skill"))

    def test_classify_destination(self):
        self.assertEqual(classify_destination("this is a rule"), "DOMAIN_RULE")
        self.assertEqual(classify_destination("a new decision"), "NARRATIVE_DECISION")
        self.assertEqual(classify_destination("conceptual entity"), "CONCEPTUAL_ENTITY")
        self.assertEqual(classify_destination("something else"), "REUSABLE_PROCEDURE")

if __name__ == "__main__":
    import os
    unittest.main()
