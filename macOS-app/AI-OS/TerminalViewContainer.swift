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
        // 1. Grab your system's clean environment directly
                var environment = ProcessInfo.processInfo.environment
                
                // 2. Inject styling and local proxy routing rules
                environment["TERM"] = "xterm-256color"
                environment["COLORTERM"] = "truecolor"
                
                // Explicitly pass your LiteLLM configurations down to the shell process
                environment["ANTHROPIC_BASE_URL"] = "http://localhost:8082"
                environment["ANTHROPIC_API_KEY"] = "using-openrouter"
                
                // Convert to the array format SwiftTerm expects
                let envArgumentArray = environment.map { "\($0.key)=\($0.value)" }
        
        // 3. Launch an interactive login shell at ~ without hardcoding any paths
        let homePath = NSHomeDirectory()

        // 2. Start the process with the proper path anchor
        terminalView.startProcess(
            executable: "/bin/zsh",
            args: ["-l", "-c", "claude", "--dangerously-skip-permissions"],
            environment: envArgumentArray,
            currentDirectory: homePath
        )
        
        return terminalView
    }

    func updateNSView(_ nsView: LocalProcessTerminalView, context: Context) {
        // No updates needed — the terminal manages its own rendering and I/O.
    }

    class Coordinator: NSObject {
        // Reserved for future delegate/menu support.
    }
}
