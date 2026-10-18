"""Regression tests: auto_commit commit messages match what is committed."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "scripts"))

import auto_commit


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class TestAutoCommitPathsMessage(unittest.TestCase):
    def setUp(self):
        tmp_root = ROOT / "tmp"
        tmp_root.mkdir(exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(dir=tmp_root)
        self.repo = Path(self._tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.test")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "tracked.txt").write_text("v1\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "init")
        self._cwd = os.getcwd()
        os.chdir(self.repo)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_fallback_message_lists_only_committed_paths(self):
        # Unrelated dirt left by "other sessions"
        (self.repo / "tracked.txt").write_text("v2\n")
        for name in ("Discussions.html", "a.txt", "b.txt", "c.txt"):
            (self.repo / name).write_text("noise\n")
        (self.repo / "skills").mkdir()
        (self.repo / "skills" / "SKILL.md").write_text("mine\n")

        # No --message: uses the staged-file fallback
        with patch.object(sys, "argv", ["auto_commit.py", "--paths", "skills/SKILL.md"]):
            auto_commit.main()

        self.assertEqual(git(self.repo, "log", "-1", "--format=%s"), "Update skills/SKILL.md")
        self.assertEqual(git(self.repo, "show", "--name-only", "--format=", "HEAD"), "skills/SKILL.md")
        # Unrelated changes stay uncommitted
        self.assertIn("Discussions.html", git(self.repo, "status", "--porcelain"))

    def test_agent_message_is_used_verbatim(self):
        (self.repo / "tracked.txt").write_text("v2\n")
        msg = "Fix tracked value\n\nBumps tracked.txt to v2 for the release."
        with patch.object(sys, "argv", ["auto_commit.py", "-m", msg, "--paths", "tracked.txt"]):
            auto_commit.main()

        self.assertEqual(git(self.repo, "log", "-1", "--format=%B"), msg)


if __name__ == "__main__":
    unittest.main()
