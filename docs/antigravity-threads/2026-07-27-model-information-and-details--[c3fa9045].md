---
title: "Model Information And Details"
date: "2026-07-27"
conversation_id: "c3fa9045-db84-4083-aba4-b52f824001ed"
source: "antigravity"
---

# Model Information And Details

## User

--model

---

## Assistant

Created At: 2026-07-27T16:59:02-06:00
Completed At: 2026-07-27T16:59:04-06:00

				The command exited with code 0.
				Output:
				[AIOS WebUI Triage] Hook registered — waiting for agent import
=== PRE-FLIGHT CHECK ===
--- Running Quota Check (ag-quota) ---
ag-quota status: WARNING - Low quota detected (darryl.l.murphy@gmail.com | gemini-3.6-flash-tiered: 0.9% remaining; darryl.l.murphy@gmail.com | Gemini 2.5 Pro: 0.9% remaining; darryl.l.murphy@gmail.com | Gemini 3.1 Flash Lite: 0.9% remaining)

--- LiteLLM Model Stack Header ---
# ==============================================================================
# LEAN CODING STACK - CHEAPEST TO SMARTEST (By SWE-Bench Pro Score & Cost)
# ==============================================================================
#
# --- TIER 1: ULTRA-BUDGET & BACKGROUND LOOPS ---
# 1. deepseek-v4-flash   ($0.04/task | 52.6% | ~100 t/s) - Background scripts, linters, log parsing
# 2. gemini-3.5-flash-lite ($0.15/task | 54.2% | 350 t/s)  - Google credit speed demon for instant loops
#
# --- TIER 2: DAILY DRIVERS & PARETO WINNERS ---
# 3. muse-spark-1.1        ($0.26/task | 61.5% | ~120 t/s) - Primary daily driver (*Vercel Proxy Active)
# 4. grok-4.5              ($0.31/task | 64.7% | ~110 t/s) - Cheap step-up when Muse Spark hits a wall
# 5. gemini-3.1-pro        ($0.36/task | 54.2% | ~80 t/s)  - 1M+ context window for huge monorepo dumps
#
# --- TIER 3: DELEGATION & HEAVY REASONING ---
# 6. claude-sonnet-5       ($0.75/task | 63.2% | ~90 t/s)  - Multi-agent manager & task delegation
# 7. gemini-3.6-flash      ($0.80/task | 58.7% | 143 t/s)  - Primary high-speed Google agent driver
# 8. claude-opus-5         ($1.35/task | 71.5% | ~70 t/s)  - Heavy refactoring (50% the price of Fable)
# 9. claude-fable-5        ($2.50/task | 80.3% | ~60 t/s)  - Nuclear option for systemic architecture bugs
# ==============================================================================
#
# SUFFIX ALIASES: Models can be called with -high / -medium / -low suffixes
# (e.g. deepseek-v4-flash-high) to pass reasoning effort hints from callers
# like Hermes. All suffix variants route to the same underlying model.
# ==============================================================================

--- Running Rules Bundler (build_rules.py) ---
rules status: OK (CLAUDE.md & GEMINI.md built)

--- Running Git Pull ---

--- Running Thread Bloat Check (check_thread_bloat.py) ---
thread bloat status: OK [T_sys: 337999, T_hist: 18644/204399.4]

I am currently running on **Gemini 3.5 Flash** (configured with low reasoning effort).

---
