## 23:55 X-Ray better-shot search (built)
- Asked: build Matt's idea (hunt nearby frames for a clearer face).
- Did: faces.swift adds Apple Vision face capture quality; xray.ts `clearerShots` decodes ±3 s at 4 fps in a separate decoder (player untouched), tracks each unclear/unnamed face by box overlap, stops at cuts (scene score > 0.15), fingerprints the 3 clearest shots, takes the best match. Commit e454b82 (glass-tv).
- Rejected: "must look like the same face" as the cut guard: a heavily blurred face looks like nobody, so it rejected the real person. Kept as knob xray.sameFace, off.
- Tested on synthetic clips made from cast photos: blur→clear (0.71→0.99), heavy blur (unknown→named), cut to another actor (correctly not borrowed). ~+0.4 s.
- Untested: real movies (profiles, motion, streams over http). Overlay doesn't show "refining"; result just arrives ~0.5 s later.
- Undo: git revert e454b82, or set xray.searchSeconds to 0.
