//
//  ClaudeTerminalView.swift
//  AI-OS
//
//  Created by Matthew Murphy on 2026-06-25.
//
//  Subclass of SwiftTerm's LocalProcessTerminalView that:
//   - Intercepts Shift+Enter to send \n instead of \r (multiline prompts)
//   - Fixes trackpad/mouse scroll wheel to handle precise scrolling deltas
//   - Forwards scroll events as Page Up/Down when in alternate-screen TUI mode
//

import AppKit
import SwiftTerm
import Carbon.HIToolbox

final class ClaudeTerminalView: LocalProcessTerminalView {

    override func keyDown(with event: NSEvent) {
        // Intercept Shift+Return: send \n (0x0a) instead of the normal \r (0x0d).
        // This lets the user insert a line break in Claude Code without submitting.
        if event.keyCode == UInt16(kVK_Return) {
            let flags = event.modifierFlags
            let hasShift = flags.contains(.shift)
            let hasCtrl  = flags.contains(.control)
            let hasOpt   = flags.contains(.option)
            let hasCmd   = flags.contains(.command)

            if hasShift && !hasCtrl && !hasOpt && !hasCmd {
                send([0x0a])
                return
            }
        }

        super.keyDown(with: event)
    }

    // MARK: - Scroll Wheel (trackpad / mouse)

    /// SwiftTerm's stock `scrollWheel` only inspects `event.deltaY`, which can
    /// be zero for modern trackpad events that carry their delta in
    /// `scrollingDeltaY`.  We also need to handle alternate-screen TUI apps
    /// (like claude) which have no scrollback — we send Page Up/Down instead.
    override func scrollWheel(with event: NSEvent) {
        // 1. Resolve the effective delta
        let delta: Double
        if event.hasPreciseScrollingDeltas {
            delta = event.scrollingDeltaY
        } else {
            delta = event.deltaY
        }
        guard delta != 0 else { return }

        let isUpper = delta > 0  // scroll up = positive delta (finger moves up)

        // 2. If the terminal is showing an alternate screen (TUI), forward
        //    scroll events as keyboard sequences the app understands.
        if terminal.isDisplayBufferAlternate {
            // Use the magnitude to decide: small scroll → ↑/↓, big → Page Up/Down
            let absDelta = abs(delta)
            if absDelta >= 3 {
                // Page Up   = ESC [ 5 ~
                // Page Down = ESC [ 6 ~
                send(isUpper ? EscapeSequences.cmdPageUp : EscapeSequences.cmdPageDown)
            } else {
                // Cursor Up   = ESC [ A
                // Cursor Down = ESC [ B
                let seq: [UInt8] = isUpper ? [0x1b, 0x5b, 0x41] : [0x1b, 0x5b, 0x42]
                send(seq)
            }
            return
        }

        // 3. Normal (primary buffer) scroll — use SwiftTerm's built-in but
        //    with the resolved delta instead of event.deltaY.
        let velocity = calcVelocity(delta: abs(delta))
        if isUpper {
            scrollUp(lines: velocity)
        } else {
            scrollDown(lines: velocity)
        }
    }

    /// Convert a scroll delta into a number of lines to scroll.
    /// Tuned for both coarse mouse wheels (delta ≈ ±1 per notch) and
    /// smooth trackpad deltas (scrollingDeltaY ≈ ±2–±20 per gesture).
    private func calcVelocity(delta: Double) -> Int {
        let d = Int(delta.rounded(.toNearestOrAwayFromZero))
        if d >= 10 { return terminal.rows }           // full page
        if d >= 5  { return terminal.rows / 2 }       // half page
        if d >= 2  { return 3 }                       // few lines
        return 1                                       // one line
    }
}