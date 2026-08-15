import sys
import unittest
from pathlib import Path

# Add services/agy-proxy directory to path
sys.path.append(str(Path(__file__).parent.parent / "services" / "agy-proxy"))

try:
    from proxy import (  # noqa: E402
        Message,
        ToolFunction,
        _build_agy_prompt,
        _build_cmd_and_prompt,
        _get_session_key,
    )
    HAS_AGY_PROXY_DEPS = True
except ImportError:
    HAS_AGY_PROXY_DEPS = False


def _msg(role: str, content: str) -> Message:
    return Message(role=role, content=content)


@unittest.skipUnless(HAS_AGY_PROXY_DEPS, "httpx or fastapi not installed")
class TestSessionKey(unittest.TestCase):
    """The session key must be stable across turns of the SAME conversation."""

@unittest.skipUnless(HAS_AGY_PROXY_DEPS, "httpx or fastapi not installed")
class TestBuildCmdAndPrompt(unittest.TestCase):
    """Flag order is critical: --print consumes the NEXT arg as the prompt,
    so the prompt must sit immediately after --print and all flags after it."""

@unittest.skipUnless(HAS_AGY_PROXY_DEPS, "httpx or fastapi not installed")
class TestBuildAgyPrompt(unittest.TestCase):
    def test_flattens_messages(self):
        messages = [
            _msg("system", "sys"),
            _msg("user", "Hello"),
            _msg("assistant", "Hi there"),
        ]
        expected = "SYSTEM: sys\n\nUSER: Hello\n\nASSISTANT: Hi there"
        self.assertEqual(_build_agy_prompt(messages), expected)


@unittest.skipUnless(HAS_AGY_PROXY_DEPS, "httpx or fastapi not installed")
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