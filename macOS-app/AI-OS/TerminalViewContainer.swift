//
//  TerminalViewContainer.swift
//  AI-OS
//
//  Created by Matthew Murphy on 2026-06-25.
//

import SwiftUI
import SwiftTerm

/// An NSViewRepresentable that wraps SwiftTerm's LocalProcessTerminalView
/// and spawns an interactive `zsh -l` shell configured to talk to a local
/// liteLLM proxy (ANTHROPIC_BASE_URL → http://127.0.0.1:8000).
struct TerminalViewContainer: NSViewRepresentable {

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeNSView(context: Context) -> LocalProcessTerminalView {
        let terminal = LocalProcessTerminalView(frame: .zero)

        // Build the environment — start with inherited vars, then override
        // so the spawned `claude` CLI talks to our local liteLLM proxy.
        var env = ProcessInfo.processInfo.environment
        env["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:8000"
        env["ANTHROPIC_API_KEY"] = "liteLLM-local"
        env["CLAUDE_CODE_ENABLE_TELEMETRY"] = "1"

        // Force color support inside the raw PTY canvas
        env["TERM"] = "xterm-256color"
        env["COLORTERM"] = "truecolor"

        // Clear out any real Anthropic keys that might confuse routing
        env.removeValue(forKey: "USER_ANTHROPIC_API_KEY")

        // SwiftTerm's startProcess expects environment as ["KEY=VALUE"] array
        let envArray: [String] = env.map { "\($0.key)=\($0.value)" }

        terminal.startProcess(
            executable: "/bin/zsh",
            args: ["-l"],
            environment: envArray
        )

        return terminal
    }

    func updateNSView(_ nsView: LocalProcessTerminalView, context: Context) {
        // No updates needed — the terminal manages its own rendering and I/O.
    }

    class Coordinator: NSObject {
        // Reserved for future delegate/menu support.
    }
}
