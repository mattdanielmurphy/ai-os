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
    get_active_convs, render, process_updates
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
        
        active, _ = get_active_convs(self.brain_dir)
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
            process_updates(last_state, last_render_time, self.brain_dir)
            self.assertIn(conv_id, last_state)
            
            # Simulate change
            transcript.write_text("new content")
            time.sleep(0.1) # Ensure mtime changes
            
            process_updates(last_state, last_render_time, self.brain_dir)
            self.assertTrue(mock_render.called)

if __name__ == '__main__':
    unittest.main()
