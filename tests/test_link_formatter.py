import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from link_formatter import enrich_file_links

class TestLinkFormatter(unittest.TestCase):
    def test_markdown_file_enrichment(self):
        text = '[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)'
        res = enrich_file_links(text)
        self.assertIn('file:///Users/matt/projects/ai-os/AG_CONTEXT.md', res)
        self.assertIn('zed://file/Users/matt/projects/ai-os/AG_CONTEXT.md', res)
        self.assertIn('ai-os://reveal?path=/Users/matt/projects/ai-os/AG_CONTEXT.md', res)

    def test_code_file_enrichment(self):
        text = '[postflight.py](file:///Users/matt/projects/ai-os/scripts/postflight.py)'
        res = enrich_file_links(text)
        self.assertIn('zed://file/Users/matt/projects/ai-os/scripts/postflight.py', res)
        self.assertIn('ai-os://reveal?path=/Users/matt/projects/ai-os/scripts/postflight.py', res)
        self.assertIn('file:///Users/matt/projects/ai-os/scripts/postflight.py', res)

    def test_code_file_with_line_numbers(self):
        text = '[postflight.py#L10-L20](file:///Users/matt/projects/ai-os/scripts/postflight.py#L10-L20)'
        res = enrich_file_links(text)
        self.assertIn('zed://file/Users/matt/projects/ai-os/scripts/postflight.py:10:20', res)

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
