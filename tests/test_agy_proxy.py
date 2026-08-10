import sys
import unittest
from pathlib import Path

# Add services/agy-proxy directory to path
sys.path.append(str(Path(__file__).parent.parent / "services" / "agy-proxy"))

from proxy import (  # noqa: E402
    Message,
    ToolFunction,
    _build_agy_prompt,
    _build_cmd_and_prompt,
    _get_session_key,
)


def _msg(role: str, content: str) -> Message:
    return Message(role=role, content=content)


class TestSessionKey(unittest.TestCase):
    """The session key must be stable across turns of the SAME conversation."""

    def test_key_stable_as_history_grows(self):
        # Turn 1: only the anchor message
        turn1 = [_msg("user", "Remember this secret code: Zulu7Xray")]
        # Turn 2: full history, same anchor first
        turn2 = [
            _msg("user", "Remember this secret code: Zulu7Xray"),
            _msg("assistant", "Noted."),
            _msg("user", "What was the code?"),
        ]
        self.assertEqual(_get_session_key(turn1), _get_session_key(turn2))

    def test_key_differs_between_conversations(self):
        a = [_msg("user", "Conversation A")]
        b = [_msg("user", "Conversation B")]
        self.assertNotEqual(_get_session_key(a), _get_session_key(b))

    def test_key_uses_system_anchor_when_present(self):
        with_system = [
            _msg("system", "You are Hermes."),
            _msg("user", "hi"),
        ]
        without_system = [_msg("user", "hi")]
        self.assertNotEqual(_get_session_key(with_system), _get_session_key(without_system))

    def test_user_tag_takes_priority(self):
        a = [_msg("user", "Conversation A")]
        b = [_msg("user", "Conversation B")]
        self.assertEqual(_get_session_key(a, user_tag="sess-1"),
                         _get_session_key(b, user_tag="sess-1"))
        self.assertNotEqual(_get_session_key(a, user_tag="sess-1"),
                            _get_session_key(a, user_tag="sess-2"))

    def test_empty_messages(self):
        self.assertEqual(_get_session_key([]), "default")


class TestBuildCmdAndPrompt(unittest.TestCase):
    """Flag order is critical: --print consumes the NEXT arg as the prompt,
    so the prompt must sit immediately after --print and all flags after it."""

    def test_fresh_session_prompt_is_full_history(self):
        messages = [
            _msg("system", "sys"),
            _msg("user", "Hello"),
        ]
        cmd, key = _build_cmd_and_prompt(messages, "agy")
        # prompt right after --print
        self.assertEqual(cmd[1], "--print")
        self.assertEqual(cmd[2], "SYSTEM: sys\n\nUSER: Hello")
        # no --conversation
        self.assertNotIn("--conversation", cmd)

    def test_resume_prompt_is_only_last_user_message(self):
        # Pre-seed the session store with a conversation id for this key
        import proxy
        messages = [_msg("user", "Anchor")]
        key = _get_session_key(messages)
        proxy._save_session(key, "abc-123")

        messages2 = [
            _msg("user", "Anchor"),
            _msg("assistant", "reply"),
            _msg("user", "Follow up question"),
        ]
        cmd, key2 = _build_cmd_and_prompt(messages2, "agy")
        self.assertEqual(key, key2)
        self.assertIn("--conversation", cmd)
        # prompt is ONLY the last user message, not the flattened history
        self.assertEqual(cmd[2], "Follow up question")

        # cleanup test artifact so the real store stays clean
        sessions = proxy._load_sessions()
        sessions.pop(key, None)
        with open(proxy.SESSION_FILE, "w") as f:
            import json
            json.dump(sessions, f, indent=2)

    def test_no_resume_when_last_message_is_assistant(self):
        import proxy
        messages = [_msg("user", "Anchor")]
        key = _get_session_key(messages)
        proxy._save_session(key, "abc-123")

        messages2 = [
            _msg("user", "Anchor"),
            _msg("assistant", "reply"),
        ]
        cmd, _ = _build_cmd_and_prompt(messages2, "agy")
        self.assertNotIn("--conversation", cmd)

        sessions = proxy._load_sessions()
        sessions.pop(key, None)
        with open(proxy.SESSION_FILE, "w") as f:
            import json
            json.dump(sessions, f, indent=2)

    def test_model_flag_comes_after_prompt(self):
        messages = [_msg("user", "Hi")]
        cmd, _ = _build_cmd_and_prompt(messages, "gemini-3.6-flash-low")
        # prompt at index 2, --model must follow it
        self.assertEqual(cmd[1], "--print")
        self.assertEqual(cmd[2], "USER: Hi")
        self.assertIn("--model", cmd)
        self.assertGreater(cmd.index("--model"), 2)

    def test_output_format_appended(self):
        messages = [_msg("user", "Hi")]
        cmd, _ = _build_cmd_and_prompt(messages, "agy", output_format="json")
        self.assertIn("--output-format", cmd)
        self.assertEqual(cmd[cmd.index("--output-format") + 1], "json")


class TestBuildAgyPrompt(unittest.TestCase):
    def test_flattens_messages(self):
        messages = [
            _msg("system", "sys"),
            _msg("user", "Hello"),
            _msg("assistant", "Hi there"),
        ]
        expected = "SYSTEM: sys\n\nUSER: Hello\n\nASSISTANT: Hi there"
        self.assertEqual(_build_agy_prompt(messages), expected)


class TestToolSchemas(unittest.TestCase):
    def test_tool_parameter_extraction(self):
        tool = ToolFunction(
            type="function",
            function={
                "name": "run_command",
                "description": "run a shell command",
                "parameters": {"type": "object", "properties": {}},
            },
        )
        self.assertEqual(tool.function.name, "run_command")
        self.assertEqual(tool.type, "function")

    def test_json_transformation(self):
        import json
        m = _msg("user", "hello")
        d = json.loads(json.dumps({"role": m.role, "content": m.content}))
        self.assertEqual(d, {"role": "user", "content": "hello"})


if __name__ == '__main__':
    unittest.main()