"""Daily Personalized Briefing: High-signal AI, Applied Tech, Drumming, Cello & Music Theory.

Curated and bounded. Zero disguised ads. Zero AI stock images.
Cached daily in SQLite to prevent duplicate computation and cognitive fatigue.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("assistant.briefing.news")

# -----------------------------------------------------------------------------
# Curated Knowledge Rotators for Drumming, Cello & Music Theory
# (Ensures high-yield, actionable practice nuggets that rotate daily)
# -----------------------------------------------------------------------------

DRUMMING_TIPS = [
    {
        "title": "Inverted Paradiddle Ghost Note Groove",
        "tip": "Practice the inverted paradiddle (`R L L R - L R R L`). Put the accents on the outer single notes (`R` and `L`) on the hi-hat/ride, and let the inner doubles (`L L` and `R R`) fall as delicate ghost notes on the snare. It immediately unlocks linear funk textures.",
    },
    {
        "title": "Moeller Arm Whip on the Hi-Hat",
        "tip": "Initiate downstrokes from the elbow and forearm, letting the wrist stay loose and whip down. On the rebound upstroke, let the stick tip graze the edge of the hi-hat. You get effortless accents on downbeats and quiet eighth-note pulses without fatiguing your wrist.",
    },
    {
        "title": "3:2 Polyrhythm Internalization",
        "tip": "Tap quarter-note triplets with your right hand while your left foot keeps straight quarter notes on the hi-hat. Use the mnemonic *'Not dif-fi-cult'* (1, 2-and, 3) to lock in the micro-pulse until both tempos feel independent.",
    },
    {
        "title": "Purdie Shuffle Ghost Note Pocket",
        "tip": "In half-time shuffles (Purdie / Porcaro), ensure your snare ghost notes sit strictly on the middle partial of the eighth-note triplet. If they rush toward the third partial, the groove loses its lazy, buoyant pocket.",
    },
    {
        "title": "Bass Drum Feathering & Beater Control",
        "tip": "Practice leaving the beater off the bass drum head between strokes (heel-down or relaxed heel-up). Burying the beater chokes low-end resonance and creates involuntary micro-doubles.",
    },
    {
        "title": "Linear 16th-Note Coordination",
        "tip": "Take a 4-note linear grouping: `K - R - L - K` (Kick - Right Hand - Left Hand - Kick). Run it continuously through 16th notes. Because no two limbs hit together, dynamics and note spacing must be laser-even.",
    },
]

CELLO_TIPS = [
    {
        "title": "Contact Point & Bow Speed Dynamics",
        "tip": "For warm, singing tone, find the sweet spot midway between bridge and fingerboard (*mezzo*). When drawing the bow slowly, increase downward arm weight; when drawing the bow fast, lighten arm weight to avoid choking string vibration.",
    },
    {
        "title": "Thumb Position Intonation Anchor",
        "tip": "When shifting above the neck block into thumb position, anchor the side of the thumb across both the D and A strings like a movable nut. Use the harmonic at the halfway point (octave) as your sonic calibration check.",
    },
    {
        "title": "Spiccato Sweet Spot",
        "tip": "Spiccato originates slightly below the balance point of the bow (closer to the frog). Keep the right wrist supple and let the natural resilience of the pernambuco/carbon fiber wood do the bouncing, not your whole arm.",
    },
    {
        "title": "Left Hand Finger Weight vs Squeezing",
        "tip": "Avoid clamping the cello neck between your thumb and fingers. Hang the natural weight of your left arm from the string; the thumb should merely rest lightly behind the neck as a guide, never as a vise.",
    },
    {
        "title": "Sul Tasto vs Sul Ponticello Coloration",
        "tip": "Use *Sul Tasto* (bowing over the fingerboard) with rapid bow speed for ethereal, airy accompaniment. Use *Sul Ponticello* (millimeters from the wooden bridge) for tense, glassy, overtone-rich accents.",
    },
]

MUSIC_THEORY_PIANO_TIPS = [
    {
        "title": "Tritone Substitution Voice Leading",
        "tip": "Substitute a `V7` dominant chord with the dominant 7th chord a tritone away (e.g. `D♭7` in place of `G7` resolving to `Cmaj7`). The 3rd and 7th (F and B/C♭) remain identical, while the bass steps down chromatically (`D♭ → C`).",
    },
    {
        "title": "Rootless Bill Evans 'A' & 'B' Voicings",
        "tip": "In a `ii-V-I` (Dm7 - G7 - Cmaj7): voice `Dm7` as `3-5-7-9` (F-A-C-E), `G7` as `7-9-3-13` (F-A-B-E), and `Cmaj7` as `3-5-7-9` (E-G-B-D). Notice the top voice stays anchored on E while inner voices shift smoothly by half/whole steps.",
    },
    {
        "title": "Minor iv Borrowed Chord (Modal Interchange)",
        "tip": "In a major key, borrow the minor `iv` chord from the parallel natural minor (e.g. `Fm` in C major, voice leading `A♭ → G`). It infuses melancholic weight before landing on the tonic major.",
    },
    {
        "title": "Neo-Riemannian Parallel & Leading-Tone Shifts",
        "tip": "Move from `C major` (C-E-G) to `C minor` (C-E♭-G) via Parallel (P) shift, then to `A♭ major` (C-E♭-A♭) via Leittonwechsel (L) shift. This chromatic triad sliding creates cinematic harmonic motion without standard circle-of-fifths cadences.",
    },
    {
        "title": "Upper Structure Triads over Dominant 7ths",
        "tip": "Play a `C7` shell (C-E-B♭) in the left hand and an `A major` triad (A-C♯-E) in the right hand. You instantly produce a rich `C7(♭9, 13)` altered sound with clear melodic shape.",
    },
]

AI_INSIGHTS = [
    {
        "title": "KV Cache Linear Scaling & Paged Attention",
        "takeaway": "While self-attention matrix computation is O(N²), stored KV cache tensors scale linearly: 2 × 2 × n_layers × n_kv_heads × d_head × seq_len bytes. PagedAttention eliminates memory fragmentation by allocating virtual pages on GPU VRAM like OS virtual memory.",
    },
    {
        "title": "Grouped-Query Attention (GQA) Efficiency",
        "takeaway": "GQA partitions query heads into groups sharing single Key/Value heads. Llama 3 and Mistral use GQA to maintain 98%+ of Multi-Head Attention modeling capacity while cutting KV cache memory bandwidth by 4x to 8x during token generation.",
    },
    {
        "title": "FlashAttention IO-Aware Tiling",
        "takeaway": "FlashAttention avoids slow GPU High-Bandwidth Memory (HBM) round-trips by tiling queries, keys, and values into on-chip SRAM, computing softmax normalization incrementally via online softmax algorithms.",
    },
    {
        "title": "LoRA Alpha Scaling Invariant",
        "takeaway": "When fine-tuning via LoRA (`W_new = W_0 + (alpha / r) * B @ A`), keeping `alpha = 2 * r` stabilizes learning dynamics when experimenting across different rank sizes (r=8, 16, 32).",
    },
    {
        "title": "Speculative Decoding Latency Drops",
        "takeaway": "Because autoregressive decoding is strictly memory-bandwidth bound, a tiny draft model generating 4–5 speculative candidate tokens verified in a single parallel forward pass by the large model yields a 2x–3x speedup with zero loss in output distribution.",
    },
    {
        "title": "RoPE Rotational Invariance",
        "takeaway": "Rotary Position Embeddings rotate 2D sub-vectors of Query and Key vectors in the complex plane. The dot product `Q_m^T K_n` depends solely on relative distance `(m - n)`, allowing natural length extrapolation with RoPE scaling factors.",
    },
]


class DailyNewsService:
    """Generates and caches personalized, bounded daily briefings."""

    def __init__(self, db: Any = None):
        self.db = db

    def _get_day_rotation_index(self, date: datetime, list_len: int) -> int:
        day_of_year = date.timetuple().tm_yday
        return (day_of_year + date.year) % list_len

    def compose_briefing(self, date: Optional[datetime] = None) -> str:
        """Composes a high-yield, ad-free briefing tailored to Matt's domains."""
        current_date = date or datetime.now()
        date_str = current_date.strftime("%A, %B %-d, %Y")

        # Pick rotating domain insights based on stable day-of-year rotation
        drum_idx = self._get_day_rotation_index(current_date, len(DRUMMING_TIPS))
        cello_idx = (self._get_day_rotation_index(current_date, len(CELLO_TIPS)) + 2) % len(CELLO_TIPS)
        theory_idx = (self._get_day_rotation_index(current_date, len(MUSIC_THEORY_PIANO_TIPS)) + 1) % len(MUSIC_THEORY_PIANO_TIPS)
        ai_idx = self._get_day_rotation_index(current_date, len(AI_INSIGHTS))
        ai_idx_2 = (ai_idx + 3) % len(AI_INSIGHTS)

        drum_tip = DRUMMING_TIPS[drum_idx]
        cello_tip = CELLO_TIPS[cello_idx]
        theory_tip = MUSIC_THEORY_PIANO_TIPS[theory_idx]
        ai_1 = AI_INSIGHTS[ai_idx]
        ai_2 = AI_INSIGHTS[ai_idx_2]

        lines = [
            f"📰 *Daily Signal* — {date_str}",
            "Ad-free · Curated · Bounded intake\n",
            "🤖 *AI & Applied Engineering*",
            f"• *{ai_1['title']}*: {ai_1['takeaway']}",
            f"• *{ai_2['title']}*: {ai_2['takeaway']}\n",
            "🥁 *Drumming & Rhythm Focus*",
            f"• *{drum_tip['title']}*",
            f"  _{drum_tip['tip']}_\n",
            "🎻 *Cello & Strings*",
            f"• *{cello_tip['title']}*",
            f"  _{cello_tip['tip']}_\n",
            "🎹 *Piano & Music Theory*",
            f"• *{theory_tip['title']}*",
            f"  _{theory_tip['tip']}\n",
            "✨ *End of briefing.* No algorithmic feed, no disguised ads. Have a focused day!",
        ]

        return "\n".join(lines).strip()

    async def get_or_create_daily_brief(
        self, date: Optional[datetime] = None, force_refresh: bool = False
    ) -> str:
        """Retrieves cached briefing for today or generates and caches it in SQLite."""
        current_date = date or datetime.now()
        today_key = f"daily_brief:{current_date.strftime('%Y-%m-%d')}"

        if self.db and not force_refresh:
            try:
                cached = await self.db.get_dynamic(today_key)
                if cached:
                    logger.info("Serving cached daily briefing for %s", today_key)
                    return cached
            except Exception as e:
                logger.warning("Error reading cached daily brief: %s", e)

        brief = self.compose_briefing(current_date)

        if self.db:
            try:
                await self.db.set_dynamic(today_key, brief)
                logger.info("Cached fresh daily briefing for %s", today_key)
            except Exception as e:
                logger.warning("Error saving daily brief to db: %s", e)

        return brief
