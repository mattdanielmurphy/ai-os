"""Regression tests for the concise live agy quota summary."""

from __future__ import annotations

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from preflight import summarize_planner_ping, summarize_quota_payload


def test_quota_summary_uses_each_accounts_default_model_not_preview_capacity():
    payload = [
        {
            "email": "first@example.test",
            "quota_summary": {
                "DefaultModelID": "gemini-default",
                "Models": [
                    {
                        "ModelID": "tab_flash_lite_preview",
                        "RemainingFraction": 1.0,
                        "IsExhausted": False,
                    },
                    {
                        "ModelID": "gemini-default",
                        "RemainingFraction": 0.34,
                        "IsExhausted": False,
                    },
                ],
            },
        },
        {
            "email": "second@example.test",
            "quota_summary": {
                "DefaultModelID": "gemini-default",
                "Models": [
                    {
                        "ModelID": "gemini-default",
                        "RemainingFraction": 0.88,
                        "IsExhausted": False,
                    },
                ],
            },
        },
    ]

    summary = summarize_quota_payload(payload)

    assert summary["account_count"] == 2
    assert summary["primary_remaining_fraction"] == 0.34
    assert summary["warning_count"] == 0


def test_planner_ping_surfaces_missing_perplexity_sign_in():
    assert summarize_planner_ping("PPLX=true | AUTH=false") == (
        "AI-OS Planner (:3031): ONLINE (Perplexity sign-in required)"
    )
    assert summarize_planner_ping("PPLX=true | AUTH=true") == (
        "AI-OS Planner (:3031): OK (Perplexity Connected)"
    )
