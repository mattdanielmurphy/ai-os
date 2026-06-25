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

    func makeNSView(context: Context) -> ClaudeTerminalView {
        let terminalView = ClaudeTerminalView(frame: .zero)

        // Inject environment: system defaults + our proxy config
        var environment = ProcessInfo.processInfo.environment
        environment["TERM"] = "xterm-256color"
        environment["COLORTERM"] = "truecolor"
        environment["ANTHROPIC_BASE_URL"] = "http://localhost:8082"
        environment["ANTHROPIC_API_KEY"] = "using-openrouter"
        let envArray = environment.map { "\($0.key)=\($0.value)" }

        // Launch interactive Claude Code shell
        let homePath = NSHomeDirectory()
        terminalView.startProcess(
            executable: "/bin/zsh",
            args: ["-l", "-c", "claude", "--dangerously-skip-permissions"],
            environment: envArray,
            currentDirectory: homePath
        )

        return terminalView
    }

    func updateNSView(_ nsView: ClaudeTerminalView, context: Context) {
        // No updates needed — the terminal manages its own rendering and I/O.
    }

    class Coordinator: NSObject {
        // Reserved for future delegate/menu support.
    }
}
