## Goal
User reported the generative music sounded like "a long growing fart" and asked for melodic, beautiful, ever-changing music synced with the visuals.

## Changes Made
- **`projects/generative-animation/script.js`** — Completely rewrote `MusicGenerator` class (lines 413–653):
  - Replaced single sawtooth oscillator with 3-layer polyphonic architecture
  - Added C major pentatonic frequency map (20 notes across 4 octaves)
  - 8-chord progression cycling every ~14s (Cmaj → Am → G5 → C/E → Dsus2 → Asus2 → C/G → Em)
  - Pad layer: 2 detuned triangle oscillators → low-pass filter → feedback reverb
  - Arpeggio layer: triangle oscillator with pluck envelope, tempo tied to noiseSpeed slider
  - Bass drone: quiet sine at C2 for root anchor
  - Feedback-delay reverb network (3 staggered delays: 0.23/0.37/0.53s at 38%/32%/26% feedback)
  - Cross-fading chord transitions via scheduled gain/frequency ramps
  - Low-pass filter cutoff modulated by cursor smoothEnergy (brighter with motion)
  - Shockwave events trigger bright accent plucks at doubled root frequency
  - Drone volume breathes with average noise value

## What Worked
- Chord cross-fading with `cancelScheduledValues` + `setValueAtTime` + `linearRampToValueAtTime` avoids audible clicks
- Pentatonic scale guarantees no wrong notes regardless of how parameters shift
- `cursonField.smoothEnergy` was already available as a signal — no changes needed to CursorField
- Low-pass on pad layer creates the "brighter with motion" effect naturally

## What Didn't Work / Known Issues
- Firefox's AudioContext autoplay policy may require user gesture — the existing toggle-button + M key pattern handles this via `toggle()`
- The `shockwave` boolean threshold (`shockwaveEnergy > 3`) could be tuned — may fire too frequently at high mouse speeds

## Architecture Notes
- Web Audio API node lifetime: oscillator nodes created once at `initAudioContext()`, never stopped/restarted — frequencies changed via `frequency.linearRampToValueAtTime`
- Feedback delay reverb is a well-known trick: 3 delays with staggered times and sub-unity feedback feeding into each other creates a rich diffuse tail
- `exponentialRampToValueAtTime` must target a non-zero value (used 0.001 as the decay floor)
