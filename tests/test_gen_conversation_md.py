import unittest
import sys
import os
import re
import json
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from gen_conversation_md import (
    fmt_time, strip_html_tags, decode_html_entities,
    extract_user_input, parse_exchanges, load_agent_response,
    next_turn_number, format_prompt, make_exchange_block, generate,
    clean_agent_content, clean_agent_response, balance_code_fences, filter_transient_lines,
    make_exchange_block_with_progress
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
        self.assertNotIn("<details>", format_prompt(long))

    def test_extract_user_input_single(self):
        content = """<ADDITIONAL_METADATA>meta</ADDITIONAL_METADATA>
current local time is: 2026-08-05T14:00:00-06:00
Comments on artifact URI: file:///test.md

Selection:
> &lt;b&gt;foo&lt;/b&gt;

Comment: "bar"

<USER_REQUEST>hello</USER_REQUEST>"""
        prompt, time = extract_user_input(content)
        self.assertEqual(time, "2:00pm")
        self.assertIn("<b>foo</b>", prompt)
        self.assertIn("💬 **Comment**: bar", prompt)
        self.assertIn("hello", prompt)

    def test_extract_user_input_multiple_comments(self):
        content = """current local time is: 2026-08-15T13:45:46-06:00
Comments on artifact URI: file:///Users/matt/thread.md

Selection:
>Emotional Support Animals (ESAs)

Comment: "not necessary"

Selection:
>Campus Transit / Pacing Allowance

Comment: "no need"
<USER_REQUEST>
I don't want to ask for too much.
</USER_REQUEST>"""
        prompt, time = extract_user_input(content)
        self.assertEqual(time, "1:45pm")
        self.assertIn("Emotional Support Animals (ESAs)", prompt)
        self.assertIn("💬 **Comment**: not necessary", prompt)
        self.assertIn("Campus Transit / Pacing Allowance", prompt)
        self.assertIn("💬 **Comment**: no need", prompt)
        self.assertIn("I don't want to ask for too much.", prompt)
        # Verify raw unparsed Selection: was not leaked
        self.assertNotIn('Selection:\n>Campus Transit', prompt)

    def test_parse_exchanges(self):
        transcript = Path(self.test_dir.name) / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>hi</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'hello'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': '[thread.md](...)'}) + '\n')
        
        exchanges = parse_exchanges(transcript)
        ex_items = [i for i in exchanges if i['type'] == 'exchange']
        self.assertEqual(len(ex_items), 1)
        self.assertEqual(ex_items[0]['users'][0]['prompt'], 'hi')
        self.assertEqual(ex_items[0]['agent_content'], 'hello')

    def test_load_agent_response(self):
        turn_file = self.history_dir / 'turn_1.md'
        turn_file.write_text('agent response')
        self.assertEqual(load_agent_response(self.history_dir, 1), 'agent response')
        self.assertEqual(load_agent_response(self.history_dir, 2), '')

    def test_make_exchange_block(self):
        block = make_exchange_block([{'prompt': 'hi', 'time': '2:00pm'}], 'hello', '2:01pm')
        self.assertIn('<div', block)
        self.assertIn('Sent at 2:00pm', block)
        self.assertIn('Responded at 2:01pm', block)
        self.assertIn('hi', block)
        self.assertIn('hello', block)

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
        ex_items = [i for i in exchanges if i['type'] == 'exchange']
        self.assertEqual(len(ex_items), 1)
        self.assertEqual(len(ex_items[0]['users']), 2)
        self.assertEqual(ex_items[0]['users'][1]['prompt'], '2')

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
        content = custom_out.read_text()
        self.assertIn('column-reverse', content)
        self.assertIn('Thread Started', content)
        self.assertIn('Sent at', content)

    def test_parse_exchanges_with_undo(self):
        transcript = Path(self.test_dir.name) / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            # Turn 1
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>1</USER_REQUEST>', 'step_index': 1}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'r1'}) + '\n')
            # Turn 2
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>2</USER_REQUEST>', 'step_index': 2}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'r2'}) + '\n')
            # Undo Turn 2
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>3</USER_REQUEST>', 'step_index': 2}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'r3'}) + '\n')
        
        items = parse_exchanges(transcript, 'test_conv', Path(self.test_dir.name))
        self.assertEqual(len(items), 3)
        self.assertEqual(items[1]['type'], 'fork_notice')
        self.assertEqual(items[2]['type'], 'exchange')
        self.assertTrue(items[1]['fork_path'].exists())
        
        content = items[1]['fork_path'].read_text()
        self.assertIn('r2', content)

    def test_format_prompt_no_details(self):
        long_prompt = "Line 1\nLine 2\nLine 3\n" + ("a" * 900) + "\nLine 5"
        formatted = format_prompt(long_prompt)
        self.assertNotIn("<details>", formatted)
        self.assertNotIn("<summary>", formatted)
        self.assertIn("Line 1\nLine 2\nLine 3", formatted)

    def test_transient_status_filtering(self):
        transcript = Path(self.test_dir.name) / 'transcript.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>Line 1\nLine 2\nLine 3</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Completed task-75. Waiting for timer notification...'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Waiting for subagent to complete...'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Gemini 3.1 Pro (High) model is streaming its reasoning'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Actual final agent response output'}) + '\n')
        
        items = parse_exchanges(transcript)
        ex = [i for i in items if i['type'] == 'exchange'][0]
        self.assertIn("Line 1\nLine 2\nLine 3", ex['users'][0]['prompt'])
        self.assertNotIn("Completed task-75", ex['agent_content'])
        self.assertNotIn("Waiting for subagent", ex['agent_content'])
        self.assertNotIn("Gemini 3.1 Pro", ex['agent_content'])
        self.assertIn("Actual final agent response output", ex['agent_content'])

    def test_balance_code_fences(self):
        unclosed = "Some text\n```python\nprint('hello')"
        balanced = balance_code_fences(unclosed)
        self.assertTrue(balanced.endswith("\n```\n"))

        unclosed_tildes = "Some text\n~~~bash\necho 1"
        balanced_tildes = balance_code_fences(unclosed_tildes)
        self.assertTrue(balanced_tildes.endswith("\n~~~\n"))

        closed = "```python\nprint(1)\n```"
        self.assertEqual(balance_code_fences(closed), closed)

    def test_clean_agent_content(self):
        # Standalone
        self.assertEqual(clean_agent_content("[thread.md](file:///brain/123/thread.md)"), "")
        # Backticked
        self.assertEqual(clean_agent_content("[`thread.md`](file:///brain/123/thread.md#L1-L10)"), "")
        # Bullet point
        self.assertEqual(clean_agent_content("- [thread.md](file://...)"), "")
        # Prefixed
        self.assertEqual(clean_agent_content("Reference link to the thread artifact: [thread.md](file://...)"), "")
        self.assertEqual(clean_agent_content("📄 Reference: [thread.md](file://...)"), "")
        self.assertEqual(clean_agent_content("Current Thread: [thread.md](file://...)"), "")
        # Conversation response
        self.assertEqual(clean_agent_content("[conversation_response.md](file://...)"), "")
        # Normal
        self.assertEqual(clean_agent_content("[app.py](file:///app.py)"), "[app.py](file:///app.py)")
        # Mixed
        self.assertEqual(clean_agent_content("text\n[thread.md](file://...)\nmore"), "text\nmore")
        # Transient wait messages
        self.assertEqual(clean_agent_content("Wait for subagent x to finish.\nHello"), "Hello")

    def test_clean_agent_response(self):
        content = "# H1\n## H2\n### H3\n#### H4\nThread context logged at: link\nThread artifact: link\nThread logged at: link\nReference link: link\nSome text"
        cleaned = clean_agent_response(content)
        self.assertIn("### H1", cleaned)
        self.assertIn("### H2", cleaned)
        self.assertIn("### H3", cleaned)
        self.assertIn("### H4", cleaned)
        self.assertNotIn("Thread context logged at:", cleaned)
        self.assertNotIn("Thread artifact:", cleaned)
        self.assertNotIn("Thread logged at:", cleaned)
        self.assertNotIn("Reference link:", cleaned)
        self.assertIn("Some text", cleaned)

    def test_transient_filtering_with_final_output(self):
        text = "Streaming reasoning...\nFinal answer here."
        self.assertEqual(filter_transient_lines(text), "Final answer here.")

    def test_transient_filtering_streaming_mode(self):
        text = "Gemini 3.1 Pro is streaming its reasoning...\nWaiting for subagent...\nI'm still waiting."
        self.assertEqual(filter_transient_lines(text), "I'm still waiting.")

    def test_paragraph_separation(self):
        transcript = Path(self.test_dir.name) / 'transcript_paragraphs.jsonl'
        with open(transcript, 'w') as f:
            f.write(json.dumps({'type': 'USER_INPUT', 'content': '<USER_REQUEST>hi</USER_REQUEST>'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Para 1'}) + '\n')
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'Para 2'}) + '\n')
        
        items = parse_exchanges(transcript)
        ex = [i for i in items if i['type'] == 'exchange'][0]
        self.assertEqual(ex['agent_content'], 'Para 1\n\nPara 2')

    def test_multiline_user_prompt_preserves_paragraphs(self):
        raw = "Para 1\n\nPara 2\n\n\nPara 3"
        formatted = format_prompt(raw)
        self.assertIn("Para 1\n\nPara 2\n\nPara 3", formatted)

    def test_make_exchange_block_multiline_user_prompt(self):
        raw_user = "Paragraph 1\n\nParagraph 2 with **bold**\n\n```python\nprint(1)\n```"
        block = make_exchange_block([{'prompt': raw_user, 'time': '2:00pm'}], 'agent response', '2:01pm')
        self.assertIn('Paragraph 1', block)
        self.assertIn('Paragraph 2 with **bold**', block)
        # Ensure user container is a closed single div
        user_div_match = re.search(r'<div title="Sent at 2:00pm"[^>]*>(.*?)</div>', block, re.DOTALL)
        self.assertIsNotNone(user_div_match)
        user_content = user_div_match.group(1)
        self.assertIn('Paragraph 1', user_content)
        self.assertIn('Paragraph 2 with **bold**', user_content)

    def test_multi_comment_and_prompt_div_divider(self):
        content = """current local time is: 2026-08-15T13:45:46-06:00
Comments on artifact URI: file:///Users/matt/thread.md

Selection:
>Quote 1

Comment: "cmt 1"

<USER_REQUEST>
User question line 1

User question line 2
</USER_REQUEST>"""
        prompt, time = extract_user_input(content)
        self.assertNotIn('<hr', prompt)
        self.assertIn('border-top: 1px solid', prompt)
        block = make_exchange_block([{'prompt': prompt, 'time': time}], 'reply', '1:46pm')
        self.assertNotIn('<hr', block)
        self.assertIn('<div title="Sent at 1:45pm"', block)

if __name__ == '__main__':
    unittest.main()

