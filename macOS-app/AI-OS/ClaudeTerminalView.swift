//
//  ClaudeTerminalView.swift
//  AI-OS
//
//  Created by Matthew Murphy on 2026-06-25.
//
//  Subclass of SwiftTerm's LocalProcessTerminalView that intercepts
//  Shift+Enter to send \n (line feed) instead of \r (carriage return).
//  Claude Code interprets \r as "submit the prompt" and \n as "insert newline."
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
                // Send a bare line feed — Claude Code treats this as "newline in prompt"
                send([0x0a])
                return
            }
        }

        super.keyDown(with: event)
    }
}