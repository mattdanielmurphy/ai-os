//
//  TerminalViewContainer.swift
//  AI-OS
//
//  Created by Matthew Murphy on 2026-06-25.
//

import SwiftUI
import SwiftTerm

/// An NSViewRepresentable that wraps SwiftTerm's LocalProcessTerminalView
/// and spawns `zsh -l -c claude` with a local liteLLM proxy configuration.
struct TerminalViewContainer: NSViewRepresentable {

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeNSView(context: Context) -> LocalProcessTerminalView {
        let terminal = LocalProcessTerminalView(frame: .zero)

        // Build the environment — start with inherited vars, then override
        // so the spawned `claude` CLI talks to our local liteLLM proxy.
        var env = ProcessInfo.processInfo.environment
        env["ANTHROPIC_BASE_URL"] = "http://localhost:8000"
        env["ANTHROPIC_API_KEY"] = "liteLLM-local"
        env["CLAUDE_CODE_ENABLE_TELEMETRY"] = "1"

        // SwiftTerm's startProcess expects environment as ["KEY=VALUE"] array
        let envArray: [String] = env.map { "\($0.key)=\($0.value)" }

        terminal.startProcess(
            executable: "/bin/zsh",
            args: ["-l", "-c", "claude"],
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
