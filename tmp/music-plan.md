# Replace Generative Music System

## Current Problem
The existing `MusicGenerator` uses a single sawtooth oscillator at 40Hz base frequency, wobbling with noise values. This creates a low, unpleasant "growing fart" sound.

## Design: Polyphonic Ambient Music Engine

### Musical Foundation
- **Scale:** C major pentatonic (C4 D4 E4 G4 A4 + octave offsets) — impossible to hit a "wrong" note
- **Chord progressions:** 8 chord sequence slowly cycling every ~16 seconds, chosen from pentatonic modes
- **Waveforms:** Triangle and sine only — warm, gentle, no harsh harmonics

### Voice Architecture (3 layers)
1. **Pad layer (2-3 voices):** Detuned sine/triangle oscillators, slow attack/release, gentle volume LFO. Long reverb tail.
2. **Arpeggio layer:** Single triangle oscillator with pluck envelope. Steps through pentatonic notes at tempo tied to `noiseSpeed` parameter.
3. **Drone/bass:** Very quiet sine at root note for warmth.

### Effects
- **Reverb:** Network of 3 feedback delays with staggered times (0.3s, 0.5s, 0.7s) feeding each other for a rich ambient tail.
- **Low-pass filter:** On pad layer, modulated by cursor energy.

### Visual Synchronization
| Visual Element | Music Response |
|---|---|
| Average noise value | Chord selection (shifts root) & arpeggio note density |
| Cursor energy (smoothEnergy) | Filter cutoff opens → brighter sound with fast movement |
| Noise speed param | Arpeggio tempo (faster = more notes/second) |
| Animation time | Slow chord progression cycling (~16s per chord) |
| Cursor shockwave burst | Accent note triggered (extra pluck) |
| Particle speed | Arpeggio velocity (note loudness) |

### Files to Modify
- `script.js` — Replace entire MusicGenerator class (lines 413-476) with new implementation

### Non-Goals
- No external audio libraries or MIDI files
- No pre-recorded samples
- No UI changes (toggle button stays as-is)
