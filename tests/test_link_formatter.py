import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from link_formatter import enrich_file_links

class TestLinkFormatter(unittest.TestCase):
    def test_file_enrichment(self):
        text = '[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)'
        res = enrich_file_links(text)
        self.assertIn('[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)', res)
        self.assertIn('[](http://127.0.0.1:8643/open_zed?path=', res)
        self.assertIn('[](http://127.0.0.1:8643/open_finder?path=', res)

    def test_line_numbers_enrichment(self):
        text = '[postflight.py#L40-L53](file:///Users/matt/projects/ai-os/scripts/postflight.py#L40-L53)'
        res = enrich_file_links(text)
        self.assertIn('postflight.py%3A40%3A53', res)

    def test_no_link_unchanged(self):
        text = 'Hello world with no links.'
        self.assertEqual(enrich_file_links(text), text)

    def test_idempotency(self):
        text = '[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)'
        first = enrich_file_links(text)
        second = enrich_file_links(first)
        self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main()
