import unittest
import sys
import os
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from watch_transcripts import (
    get_active_convs, render, process_updates, is_turn_completed, get_brain_dir_for_conv
)

class TestWatchTranscripts(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.brain_dir = Path(self.test_dir.name) / 'brain'
        self.brain_dir.mkdir()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_active_convs(self):
        conv_id = "test_conv"
        conv_dir = self.brain_dir / conv_id
        (conv_dir / ".system_generated/logs").mkdir(parents=True)
        transcript = conv_dir / ".system_generated/logs/transcript.jsonl"
        transcript.write_text("{}")
        
        active, _ = get_active_convs(self.brain_dir, force_rescan=True)
        self.assertIn(conv_id, active)

    def test_render(self):
        with patch('watch_transcripts.subprocess.run'):
            # In a real setup render would create this file
            self.output_file = self.brain_dir / "test_conv" / "transcript.md"
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.output_file.write_text("rendered")
            
            self.assertTrue(render("test_conv", self.brain_dir))
            self.assertTrue(self.output_file.exists())

    def test_process_updates(self):
        conv_id = "test_conv"
        conv_dir = self.brain_dir / conv_id
        (conv_dir / ".system_generated/logs").mkdir(parents=True)
        transcript = conv_dir / ".system_generated/logs/transcript.jsonl"
        transcript.write_text("initial content")
        
        last_state = {}
        last_render_time = {}
        
        # Initial run
        with patch('watch_transcripts.render', return_value=True) as mock_render:
            process_updates(last_state, last_render_time, set(), self.brain_dir, {}, self.brain_dir / ".commit_results")
            self.assertIn(conv_id, last_state)
            
            # Simulate change
            transcript.write_text("new content")
            time.sleep(0.1) # Ensure mtime changes
            
            process_updates(last_state, last_render_time, set(), self.brain_dir, {}, self.brain_dir / ".commit_results")
            self.assertTrue(mock_render.called)

    def test_is_turn_completed(self):
        conv_dir = self.brain_dir / "turn_test"
        (conv_dir / ".system_generated/logs").mkdir(parents=True)
        transcript = conv_dir / ".system_generated/logs/transcript.jsonl"
        
        # User input (not completed)
        transcript.write_text(json.dumps({'type': 'USER_INPUT', 'content': 'hello'}) + '\n')
        self.assertFalse(is_turn_completed(transcript))
        
        # Planner response with tool call (not completed)
        with open(transcript, 'a') as f:
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'tool_calls': [{'name': 'view_file'}]}) + '\n')
        self.assertFalse(is_turn_completed(transcript))
        
        # Final planner response with no tool calls (completed)
        with open(transcript, 'a') as f:
            f.write(json.dumps({'type': 'PLANNER_RESPONSE', 'content': 'All done!', 'tool_calls': []}) + '\n')
        self.assertTrue(is_turn_completed(transcript))

    def test_subagent_mapping(self):
        parent_id = "11111111-1111-1111-1111-111111111111"
        sub_id = "22222222-2222-2222-2222-222222222222"
        parent_dir = self.brain_dir / parent_id
        (parent_dir / ".system_generated/logs").mkdir(parents=True)
        transcript = parent_dir / ".system_generated/logs/transcript.jsonl"
        transcript.write_text(json.dumps({'type': 'PLANNER_RESPONSE', 'tool_calls': [{'name': 'invoke_subagent', 'args': {'conversationID': sub_id}}]}) + '\n')
        
        active, sub_map = get_active_convs(self.brain_dir, force_rescan=True)
        self.assertEqual(sub_map.get(sub_id), parent_id)
        self.assertEqual(get_brain_dir_for_conv(sub_id), self.brain_dir)

if __name__ == '__main__':
    unittest.main()
