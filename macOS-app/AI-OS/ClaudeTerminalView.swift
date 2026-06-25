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
//  NOTE: Uses NSEvent local monitors (not method overrides) because SwiftTerm's
//  MacTerminalView declares keyDown(with:) and scrollWheel(with:) as public
//  override — not open — which would produce compiler warnings when overriding
//  from outside the SwiftTerm module. Local monitors intercept the event before
//  dispatch, avoiding the need to override at all.
//

import AppKit
import SwiftTerm
import Carbon.HIToolbox

final class ClaudeTerminalView: LocalProcessTerminalView {

    // MARK: - Event Monitors

    private var keyDownMonitor: Any?
    private var scrollWheelMonitor: Any?

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        removeMonitors()

        guard let window = self.window else { return }

        // Intercept Shift+Return: send \n (0x0a) instead of the normal \r (0x0d).
        // This lets the user insert a line break in Claude Code without submitting.
        keyDownMonitor = NSEvent.addLocalMonitorForEvents(matching: .keyDown) {
            [weak self] event in
            guard let self else { return event }

            if event.keyCode == UInt16(kVK_Return) {
                let flags = event.modifierFlags
                let hasShift = flags.contains(.shift)
                let hasCtrl  = flags.contains(.control)
                let hasOpt   = flags.contains(.option)
                let hasCmd   = flags.contains(.command)

                if hasShift && !hasCtrl && !hasOpt && !hasCmd {
                    self.send([0x0a])
                    return nil // consumed
                }
            }

            return event // pass through
        }

        // Intercept scroll events to:
        //   a) Use scrollingDeltaY (precise trackpad) instead of deltaY
        //   b) Forward scrolls as Page Up/Down keys in alternate-screen TUI apps
        scrollWheelMonitor = NSEvent.addLocalMonitorForEvents(matching: .scrollWheel) {
            [weak self] event in
            guard let self else { return event }

            // Resolve the effective delta
            let delta: Double
            if event.hasPreciseScrollingDeltas {
                delta = event.scrollingDeltaY
            } else {
                delta = event.deltaY
            }
            guard delta != 0 else { return nil }

            let isUpper = delta > 0 // positive = finger/mouse moves up

            // Alternate screen (TUI) → forward as keyboard sequences
            if terminal.isCurrentBufferAlternate {
                let absDelta = abs(delta)
                if absDelta >= 3 {
                    // Page Up   = ESC [ 5 ~
                    // Page Down = ESC [ 6 ~
                    self.send(isUpper
                        ? EscapeSequences.cmdPageUp
                        : EscapeSequences.cmdPageDown)
                } else {
                    // Cursor Up   = ESC [ A
                    // Cursor Down = ESC [ B
                    let seq: [UInt8] = isUpper
                        ? [0x1b, 0x5b, 0x41]
                        : [0x1b, 0x5b, 0x42]
                    self.send(seq)
                }
                return nil // consumed
            }

            // Primary buffer scroll — use resolved delta instead of event.deltaY
            let velocity = calcVelocity(delta: abs(delta))
            if isUpper {
                scrollUp(lines: velocity)
            } else {
                scrollDown(lines: velocity)
            }
            return nil // consumed — prevent SwiftTerm's deltaY-only handler from firing
        }
    }

    override func viewWillMove(toWindow newWindow: NSWindow?) {
        if newWindow == nil { removeMonitors() }
        super.viewWillMove(toWindow: newWindow)
    }

    private func removeMonitors() {
        if let monitor = keyDownMonitor {
            NSEvent.removeMonitor(monitor)
            keyDownMonitor = nil
        }
        if let monitor = scrollWheelMonitor {
            NSEvent.removeMonitor(monitor)
            scrollWheelMonitor = nil
        }
    }

    // MARK: - Helpers

    /// Convert a scroll delta into a number of lines to scroll.
    /// Tuned for both coarse mouse wheels (delta ≈ ±1 per notch) and
    /// smooth trackpad deltas (scrollingDeltaY ≈ ±2–±20 per gesture).
    private func calcVelocity(delta: Double) -> Int {
        let d = Int(delta.rounded(.toNearestOrAwayFromZero))
        if d >= 10 { return terminal.rows }          // full page
        if d >= 5  { return terminal.rows / 2 }       // half page
        if d >= 2  { return 3 }                       // few lines
        return 1                                       // one line
    }
}