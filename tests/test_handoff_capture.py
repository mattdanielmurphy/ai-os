import base64
import json
import os
import sys
import tempfile
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "../scripts"))

import handoff_capture  # noqa: E402

PNG = base64.b64encode(b"\x89PNG\r\n\x1a\nfake-bytes").decode()
MATT_TEXT = (
    "<!-- reply 2 -->\n> Inline widgets are desktop-only\n\nI really wish I knew this first :(\n\n"
    "and here's code:\n```py\nprint('x')\n```\nkeep `this` exact  \ttabs\ttoo"
)


def rec(type_, content, pid="p2", **kw):
    return {"type": type_, "promptId": pid, "message": {"role": type_, "content": content}, **kw}


class TestHandoffCapture(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(dir=os.path.join(os.path.dirname(__file__), "..", "tmp")
                                    if os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "tmp")) else None)
        self.transcript = os.path.join(self.dir, "t.jsonl")
        self.handoff = os.path.join(self.dir, "2026-10-17_x.md")
        with open(self.handoff, "w") as f:
            f.write("# Handoff: x\n\n## Read first\n- a\n")

    def write(self, records):
        with open(self.transcript, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    def run_capture(self):
        handoff_capture.main(["--handoff", self.handoff, "--transcript", self.transcript])
        return open(self.handoff).read()

    def test_command_args_quotes_and_images_verbatim(self):
        self.write([
            rec("user", "older message, not part of handoff", pid="p1"),
            rec("assistant", [{"type": "text", "text": "reply"}], pid=None),
            rec("user", f"<command-message>_handoff</command-message>\n<command-name>/_handoff</command-name>\n"
                        f"<command-args>{MATT_TEXT}</command-args>"),
            rec("user", [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": PNG}},
                         {"type": "text", "text": "second note"}]),
            rec("user", [{"type": "text", "text": "Base directory for this skill: /x\n# Handoff"}], isMeta=True),
            rec("user", [{"type": "tool_result", "content": "noise"}]),
        ])
        out = self.run_capture()
        self.assertIn(handoff_capture.SECTION, out)
        self.assertIn("/_handoff " + MATT_TEXT, out)  # byte-exact, incl. tabs and the inner ``` fence
        self.assertIn("````text", out)  # outer fence longer than the inner one
        self.assertIn("second note", out)
        self.assertNotIn("older message", out)
        self.assertNotIn("Base directory", out)
        self.assertNotIn("noise", out)
        with open(os.path.join(self.dir, "2026-10-17_x", "image-1.png"), "rb") as f:
            self.assertEqual(f.read(), base64.b64decode(PNG))
        self.assertIn("2026-10-17_x/image-1.png", out)

    def test_plain_words_fallback_uses_latest_prompt(self):
        self.write([rec("user", "first", pid="p1"), rec("user", "ok hand this off, keep the quote", pid="p2")])
        out = self.run_capture()
        self.assertIn("ok hand this off, keep the quote", out)
        self.assertNotIn("```text\nfirst", out)

    def test_refuses_second_append(self):
        self.write([rec("user", "/x")])
        self.run_capture()
        with self.assertRaises(SystemExit):
            self.run_capture()


if __name__ == "__main__":
    unittest.main()
