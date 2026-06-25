//
//  ContentView.swift
//  AI-OS
//
//  Created by Matthew Murphy on 2026-06-25.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 0) {
            TerminalViewContainer()
                .frame(maxWidth: .infinity, maxHeight: .infinity)

            // Bottom bezel — dark native look
            HStack {
                Text("AI-OS | DeepSeek V4")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)

                Spacer()

                Text("Session Cost: $0.00")
                    .font(.system(size: 12, weight: .regular, design: .monospaced))
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 16)
            .frame(height: 50)
            .background {
                Color(nsColor: .windowBackgroundColor)
            }
        }
    }
}

#Preview {
    ContentView()
}