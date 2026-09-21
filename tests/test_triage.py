import sys
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

import subprocess
from triage_router import evaluate_routing, build_thin_handoff, is_lightweight_request, format_routing_visibility
from triage_task import evaluate_triage


class TestTriage(unittest.TestCase):
    def test_cli_execution(self):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "scripts/triage_task.py"), "--prompt", "test task"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Recommended Model:", result.stdout)
        self.assertIn("Reasoning:", result.stdout)

    def test_healthy_quota_substantive_analytical(self):
        """Case 1: Healthy agy quota plus a substantive analytical request routes to agy."""
        prompt = "Review the current architecture and explain the best way to add this feature."
        decision = evaluate_routing(prompt, mock_quota_status="healthy", mock_quota_fraction=1.0)
        
        self.assertEqual(decision["backend"], "agy")
        self.assertEqual(decision["selection_method"], "automatic")
        self.assertEqual(decision["quota_status"], "healthy")
        self.assertFalse(decision["fallback_occurred"])
        self.assertFalse(decision["is_lightweight"])
        self.assertIsNotNone(decision["thin_handoff"])
        self.assertIn(prompt, decision["thin_handoff"])
        self.assertIn("Mode: plan", decision["thin_handoff"])

    def test_healthy_quota_repository_implementation(self):
        """Case 2: Healthy agy quota plus a repository/implementation request routes to agy."""
        prompt = "Look through the project and implement this change to fix the bug."
        decision = evaluate_routing(prompt, mock_quota_status="healthy", mock_quota_fraction=0.85)
        
        self.assertEqual(decision["backend"], "agy")
        self.assertEqual(decision["selection_method"], "automatic")
        self.assertFalse(decision["fallback_occurred"])
        self.assertFalse(decision["is_lightweight"])
        self.assertIsNotNone(decision["thin_handoff"])
        self.assertIn(prompt, decision["thin_handoff"])
        self.assertIn("Mode: build", decision["thin_handoff"])

    def test_healthy_quota_clearly_trivial(self):
        """Case 3: Healthy agy quota plus clearly trivial requests stay direct in ChatGPT."""
        trivial_prompts = [
            ("Hi", "greeting / casual conversation"),
            ("Hello there", "greeting / casual conversation"),
            ("What is 17 * 4?", "trivial calculation"),
            ("Fix the grammar in this: She go to store yesterday.", "short text rewrite or formatting"),
            ("Make this title shorter: The Great Big Guide to Artificial Intelligence Systems", "short text rewrite or formatting"),
            ("Give me three quick name ideas for a coffee shop", "simple context-free brainstorming"),
        ]
        for prompt, expected_reason in trivial_prompts:
            with self.subTest(prompt=prompt):
                decision = evaluate_routing(prompt, mock_quota_status="healthy", mock_quota_fraction=1.0)
                self.assertEqual(decision["backend"], "chatgpt")
                self.assertEqual(decision["selection_method"], "automatic")
                self.assertTrue(decision["is_lightweight"])
                self.assertEqual(decision["lightweight_reason"], expected_reason)
                self.assertFalse(decision["fallback_occurred"])
                self.assertIsNone(decision["thin_handoff"])

    def test_low_or_unavailable_quota_fallback(self):
        """Case 4: Low, exhausted, or unavailable agy quota falls back cleanly to direct ChatGPT."""
        prompt = "Review the current architecture and explain the best way to add this feature."
        
        # 4a. Low quota (< 20%)
        d_low = evaluate_routing(prompt, mock_quota_status="low", mock_quota_fraction=0.12)
        self.assertEqual(d_low["backend"], "chatgpt")
        self.assertTrue(d_low["fallback_occurred"])
        self.assertEqual(d_low["fallback_reason"], "low quota")

        # 4b. Exhausted quota (0%)
        d_ex = evaluate_routing(prompt, mock_quota_status="exhausted", mock_quota_fraction=0.0)
        self.assertEqual(d_ex["backend"], "chatgpt")
        self.assertTrue(d_ex["fallback_occurred"])
        self.assertEqual(d_ex["fallback_reason"], "exhausted quota")

        # 4c. Unavailable quota
        d_unavail = evaluate_routing(prompt, mock_quota_status="unavailable", mock_quota_fraction=None)
        self.assertEqual(d_unavail["backend"], "chatgpt")
        self.assertTrue(d_unavail["fallback_occurred"])
        self.assertEqual(d_unavail["fallback_reason"], "unavailable quota")

        # 4d. Unknown quota
        d_unk = evaluate_routing(prompt, mock_quota_status="unknown", mock_quota_fraction=None)
        self.assertEqual(d_unk["backend"], "chatgpt")
        self.assertTrue(d_unk["fallback_occurred"])
        self.assertEqual(d_unk["fallback_reason"], "unknown quota")

    def test_explicit_user_override_forcing_agy(self):
        """Case 5: Explicit user override forcing agy (via flag or in-prompt)."""
        # 5a. Flag override
        decision_flag = evaluate_routing("What is 17 * 4?", explicit_flags=["--agy"], mock_quota_status="healthy")
        self.assertEqual(decision_flag["backend"], "agy")
        self.assertEqual(decision_flag["selection_method"], "explicit")
        self.assertIn("--agy", decision_flag["override_reason"])

        # 5b. In-prompt override even with low quota
        decision_prompt = evaluate_routing("use agy to review the architecture", mock_quota_status="low")
        self.assertEqual(decision_prompt["backend"], "agy")
        self.assertEqual(decision_prompt["selection_method"], "explicit")
        self.assertFalse(decision_prompt["fallback_occurred"])

    def test_explicit_user_override_forcing_direct_chatgpt(self):
        """Case 6: Explicit user override forcing direct ChatGPT."""
        # 6a. Flag override
        prompt = "Review the current architecture and explain the best way to add this feature."
        decision_flag = evaluate_routing(prompt, explicit_flags=["--chatgpt"], mock_quota_status="healthy")
        self.assertEqual(decision_flag["backend"], "chatgpt")
        self.assertEqual(decision_flag["selection_method"], "explicit")
        self.assertFalse(decision_flag["fallback_occurred"])

        # 6b. In-prompt override ("do not delegate")
        decision_prompt = evaluate_routing("Do not delegate this: Review the current architecture", mock_quota_status="healthy")
        self.assertEqual(decision_prompt["backend"], "chatgpt")
        self.assertEqual(decision_prompt["selection_method"], "explicit")
        self.assertFalse(decision_prompt["fallback_occurred"])

    def test_thin_handoff_policy(self):
        """Validates thin handoff contains only verbatim request, repo/cwd, and mode."""
        prompt = "Compare these database architectures and propose a migration plan."
        handoff = build_thin_handoff(prompt, cwd="/Users/matt/projects/ai-os", safety_boundary="no-drop-db")
        
        self.assertIn(f"Original user request: {prompt}", handoff)
        self.assertIn("Active project/repository and working directory:", handoff)
        self.assertIn("Mode: plan", handoff)
        self.assertIn("Safety boundary: no-drop-db", handoff)
        # Verify no token-wasting prompt expansion / pre-triage bloat
        self.assertNotIn("Here is an exhaustive breakdown", handoff)
        self.assertNotIn("Step 1: Parse AST", handoff)

    def test_routing_visibility_formatting(self):
        """Validates human-readable routing visibility output format."""
        decision = evaluate_routing("Review the architecture", mock_quota_status="healthy", mock_quota_fraction=1.0)
        visibility = format_routing_visibility(decision)
        
        self.assertIn("[ai-os routing]", visibility)
        self.assertIn("Backend: agy", visibility)
        self.assertIn("Selection: automatic (healthy quota available)", visibility)
        self.assertIn("Quota: healthy (100% remaining)", visibility)
        self.assertIn("Fallback: false", visibility)


if __name__ == '__main__':
    unittest.main()
