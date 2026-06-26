import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

// 1. Terminal Setup
const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: { background: '#000000', foreground: '#ffffff' },
    disableStdin: true // Locks xterm from receiving raw keyboard inputs
});

const fitAddon = new FitAddon();
term.loadAddon(fitAddon);

const container = document.getElementById('terminal-container');
if (container) {
    term.open(container);
    fitAddon.fit();
}

window.addEventListener('resize', () => fitAddon.fit());

// 2. Listen to Backend PTY events
listen<{ data: string }>('pty-output', (event) => {
    term.write(event.payload.data);
});

// 3. UI State Management
let currentEngine: 'claude' | 'agy' = 'claude';
const engineRadios = document.querySelectorAll<HTMLInputElement>('input[name="engine"]');

engineRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy';
    });
});

// 4. Input Interception & Routing
const textarea = document.getElementById('prompt-input') as HTMLTextAreaElement;

textarea?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Stop a visual line break
        
        const rawInput = textarea.value.trim();
        if (!rawInput) return;

        let commandToExecute = '';

        if (currentEngine === 'claude') {
            // Claude acts as a REPL environment. If the user is in Claude, 
            // send text verbatim. (If they aren't, this sends raw shell commands).
            commandToExecute = rawInput;
        } else if (currentEngine === 'agy') {
            // Agy is an orchestrator. We wrap the payload in quotes 
            // and pass it as an argument to the agy binary.
            const escapedInput = rawInput.replace(/"/g, '\\"');
            commandToExecute = `agy "${escapedInput}"`;
        }

        // Send formatted string to Rust, appended with newline to execute
        invoke('write_to_pty', { data: commandToExecute + '\r\n' })
            .catch((err) => {
                console.error("Failed to write to PTY:", err);
                term.write(`\r\n\x1b[31mError writing to shell: ${err}\x1b[0m\r\n`);
            });
        textarea.value = '';
    }
});

// 5. Focus Management
textarea?.focus();
document.addEventListener("click", () => {
    const selection = window.getSelection();
    if (!selection || selection.toString() === "") {
        textarea?.focus();
    }
});
