import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from gen_conversation_md import (
    fmt_time, strip_html_tags, decode_html_entities,
    extract_user_input, parse_exchanges, load_agent_response,
    next_turn_number, format_prompt, make_exchange_block, generate
)

class TestGenConversationMd(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.history_dir = Path(self.test_dir.name) / 'history'
        self.history_dir.mkdir()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_fmt_time(self):
        self.assertEqual(fmt_time("2026-08-05T14:05:00-06:00"), "2:05pm")
        self.assertEqual(fmt_time("2026-08-05T00:00:00"), "12:00am")
        self.assertEqual(fmt_time("2026-08-05T12:00:00"), "12:00pm")
        self.assertEqual(fmt_time("invalid"), "")

    def test_strip_html_tags(self):
        self.assertEqual(strip_html_tags("<b>test</b>"), "test")
        self.assertEqual(strip_html_tags("<div><span>hello</span></div>"), "hello")

    def test_decode_html_entities(self):
        self.assertEqual(decode_html_entities("&lt;div&gt;&amp;&#x27;&quot;"), "<div>&'\"")

    def test_next_turn_number(self):
        self.assertEqual(next_turn_number(self.history_dir), 1)
        (self.history_dir / 'turn_1.md').write_text('content')
        self.assertEqual(next_turn_number(self.history_dir), 2)
        (self.history_dir / 'turn_3.md').write_text('content')
        self.assertEqual(next_turn_number(self.history_dir), 4)

    def test_format_prompt(self):
        short = "short"
        self.assertEqual(format_prompt(short), short)
        long = "a" * 900
        self.assertIn("<details>", format_prompt(long))

    def test_extract_user_input(self):
        content = """<ADDITIONAL_METADATA>meta</ADDITIONAL_METADATA>
current local time is: 2026-08-05T14:00:00-06:00
Comments on artifact URI: file:///test.md

Selection:
> &lt;b&gt;foo&lt;/b&gt;

Comment: "bar"

<USER_REQUEST>hello</USER_REQUEST>"""
        prompt, time = extract_user_input(content)
        self.assertEqual(time, "2:00pm")
        self.assertIn("> <b>foo</b>", prompt)
        self.assertIn("💬 **Comment**: bar", prompt)
        self.assertIn("hello", prompt)

    def test_parse_exchanges(self):
        transcript = Path(self.test_dir.name) / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>hi</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'hello'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': '[thread.md](...)'}) + '\n') # Should skip
        
        exchanges = parse_exchanges(transcript)
        self.assertEqual(len(exchanges), 1)
        self.assertEqual(exchanges[0]['users'][0]['prompt'], 'hi')
        self.assertEqual(exchanges[0]['agent_text'], 'hello')

    def test_load_agent_response(self):
        turn_file = self.history_dir / 'turn_1.md'
        turn_file.write_text('agent response')
        self.assertEqual(load_agent_response(self.history_dir, 1), 'agent response')
        self.assertEqual(load_agent_response(self.history_dir, 2, 'fallback'), 'fallback')

    def test_make_exchange_block(self):
        block = make_exchange_block([{'prompt': 'hi', 'time': '2:00pm'}], 'hello', '2:01pm')
        self.assertIn('#### 🧔 You — *2:00pm*', block)
        self.assertIn('hi', block)
        self.assertIn('#### 🤖 Agent — *2:01pm*', block)
        self.assertIn('hello', block)

    def test_generate(self):
        conv_id = 'test_conv'
        base = Path(self.test_dir.name) / 'brain' / conv_id
        base.mkdir(parents=True)
        sys_logs = base / '.system_generated/logs'
        sys_logs.mkdir(parents=True)
        
        transcript = sys_logs / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>hi</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'hello'}) + '\n')
        
        (base / 'history').mkdir()
        (base / 'history' / 'turn_1.md').write_text('manual response')
        
        generate(conv_id, 'Title', Path(self.test_dir.name))
        
        output = base / 'thread.md'
        self.assertTrue(output.exists())
        self.assertIn('manual response', output.read_text())

    def test_strip_system_tags(self):
        content = "<system>hidden</system><user_rules>rule</user_rules><USER_REQUEST>hi</USER_REQUEST>"
        prompt, _ = extract_user_input(content)
        self.assertEqual(prompt, "hi")

    def test_multi_user_input(self):
        transcript = Path(self.test_dir.name) / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>1</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>2</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'reply'}) + '\n')
        
        exchanges = parse_exchanges(transcript)
        self.assertEqual(len(exchanges), 1)
        self.assertEqual(len(exchanges[0]['users']), 2)
        self.assertEqual(exchanges[0]['users'][1]['prompt'], '2')

    def test_format_prompt_fenced_code(self):
        prompt = "test ```python\ndef f():\n  pass\n```"
        formatted = format_prompt(prompt)
        lines = formatted.split('\n')
        self.assertIn("```python", lines)
        self.assertIn("```", lines)
        self.assertTrue(lines.index("```python") > 0)
        self.assertTrue(lines.index("```") > lines.index("```python"))

    def test_generate_output_path(self):
        conv_id = 'test_conv_out'
        base = Path(self.test_dir.name) / 'brain' / conv_id
        base.mkdir(parents=True)
        sys_logs = base / '.system_generated/logs'
        sys_logs.mkdir(parents=True)
        (base / 'history').mkdir()
        
        transcript = sys_logs / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>hi</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'hello'}) + '\n')
            
        custom_out = Path(self.test_dir.name) / 'custom.md'
        generate(conv_id, 'Title', Path(self.test_dir.name), output_path_override=custom_out)
        self.assertTrue(custom_out.exists())

if __name__ == '__main__':
    unittest.main()
