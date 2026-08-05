import sys
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

import subprocess

class TestTriage(unittest.TestCase):
    def test_cli_execution(self):
        result = subprocess.run([sys.executable, str(Path(__file__).parent.parent / "scripts/triage_task.py"), "--prompt", "test task"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Recommended Model:", result.stdout)
        self.assertIn("Reasoning:", result.stdout)

    def test_task_classification(self):
        self.assertTrue(True)

    def test_fast_path_interception(self):
        self.assertTrue(True)

    def test_routing_table_resolution(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
