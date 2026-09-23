import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from link_formatter import enrich_file_links

class TestLinkFormatter(unittest.TestCase):
    def test_file_link_is_preserved_without_editor_launchers(self):
        text = '[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)'
        res = enrich_file_links(text)
        self.assertEqual(res, text)

    def test_line_number_file_link_is_preserved(self):
        text = '[postflight.py#L40-L53](file:///Users/matt/projects/ai-os/scripts/postflight.py#L40-L53)'
        res = enrich_file_links(text)
        self.assertEqual(res, text)

    def test_no_link_unchanged(self):
        text = 'Hello world with no links.'
        self.assertEqual(enrich_file_links(text), text)

    def test_no_launcher_links_are_added(self):
        text = '[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)'
        res = enrich_file_links(text)
        self.assertNotIn('open_zed', res)
        self.assertNotIn('open_finder', res)

if __name__ == '__main__':
    unittest.main()
