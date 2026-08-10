# Cache-Aware Thread Handoff & Stale Thread Safety Gate

## Status: Active / High Priority Task

## Overview
Resuming dormant threads after 1 hour (or provider TTL expiry) forces full raw transcript re-ingest. We need a safety gate in `preflight.py` / `check_thread_bloat.py`.

## Requirements
1. **Stale Thread Fail-Gate**: When sending a message to a thread that has been dormant > 1 hour (or TTL), automatically intercept/fail or trigger handoff cleanly to prevent accidental high-cost re-ingests.
2. **Dynamic Safety Margin**: The TTL safety margin scales dynamically with thread size (larger threads = aggressive early handoff).
3. **Fallback**: If auto-handoff cannot be auto-triggered natively, hard-fail with a clear warning prompt to force a fresh thread handoff.
