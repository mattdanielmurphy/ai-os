import { invoke } from "@tauri-apps/api/tauri";
import { listen } from "@tauri-apps/api/event";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";

// Import styles
import "./styles.css";

interface PtyPayload {
  data: string;
}

window.addEventListener("DOMContentLoaded", () => {
  const terminalContainer = document.getElementById("terminal-container");
  const promptInput = document.getElementById("prompt-input") as HTMLTextAreaElement;

  if (!terminalContainer || !promptInput) {
    console.error("Required DOM elements not found!");
    return;
  }

  // Initialize xterm
  const term = new Terminal({
    cursorBlink: true,
    fontSize: 13,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: {
      background: '#0d0e15',
      foreground: '#f1f1f4',
      cursor: '#f1f1f4',
      selectionBackground: '#2a2b3d',
    },
    disableStdin: true, // Lock the terminal from receiving direct keystrokes
  });

  const fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  term.open(terminalContainer);
  fitAddon.fit();

  // Listen for window resize
  window.addEventListener("resize", () => {
    fitAddon.fit();
  });

  // Listen to PTY outputs from Rust
  listen<PtyPayload>("pty-output", (event) => {
    term.write(event.payload.data);
  });

  // Listen to keyboard entry on the textarea
  promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Stop carriage return in textarea
      const val = promptInput.value;
      if (val !== null) {
        // Send command to the PTY
        invoke("write_to_pty", { data: val + "\n" })
          .catch((err) => {
            console.error("Failed to write to PTY:", err);
            term.write(`\r\n\x1b[31mError writing to shell: ${err}\x1b[0m\r\n`);
          });
        promptInput.value = "";
      }
    }
  });

  // Focus prompt input by default
  promptInput.focus();
  document.addEventListener("click", () => {
    // Focus textarea if user clicks somewhere, for convenience,
    // but allow selecting text in terminal if needed.
    const selection = window.getSelection();
    if (!selection || selection.toString() === "") {
      promptInput.focus();
    }
  });
});
