# Audio & Web Audio API Rules

- **Web Audio Node Lifetime**: Oscillator and filter nodes should be created once at `initAudioContext()` and modulated via parameter automation (`frequency.linearRampToValueAtTime`, `gain.exponentialRampToValueAtTime`).
- **Decay Floor**: Exponential ramps must target a non-zero floor value (e.g. `0.001`) to avoid WebAudio arithmetic errors.
- **Feedback Delay Networks**: Maintain sub-unity feedback across staggered delay lines to produce stable diffuse tails without clipping.
