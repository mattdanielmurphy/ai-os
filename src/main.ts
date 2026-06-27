import '@xterm/xterm/css/xterm.css'
import './styles.css'

import { FitAddon } from '@xterm/addon-fit'
import { Terminal } from '@xterm/xterm'
import { invoke } from '@tauri-apps/api/tauri'
import { listen } from '@tauri-apps/api/event'

// 1. Terminal Setup
const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: { background: '#000000', foreground: '#ffffff' },
})

const fitAddon = new FitAddon();
term.loadAddon(fitAddon);

// Handle direct input to terminal
term.onData((data) => {
    invoke('write_to_pty', { data }).catch((err) => {
        console.error('Failed to write direct key input to PTY:', err);
    });
});

// Helper function to fit and sync geometry with Rust
const resizePty = () => {
    fitAddon.fit();
    invoke('resize_pty', { rows: term.rows, cols: term.cols }).catch((err) => {
        console.error('Failed to resize PTY:', err);
    });
};

const container = document.getElementById('terminal-container');
if (container) {
    term.open(container);
    resizePty(); // Sync immediately on boot
}

window.addEventListener('resize', () => {
    resizePty(); // Sync on window resize
});

// 2. Listen to Backend PTY events
listen<{ data: string }>('pty-output', (event) => {
    term.write(event.payload.data)
})

// 3. UI State Management
let currentEngine: 'claude' | 'agy' = 'claude'
const engineRadios = document.querySelectorAll<HTMLInputElement>(
    'input[name="engine"]'
)

engineRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy'
    })
})

// 4. Input Interception & Routing
const textarea = document.getElementById('prompt-input') as HTMLTextAreaElement

// Auto-resize function
const adjustHeight = () => {
    if (textarea) {
        textarea.style.height = 'auto';
        // Enforce boundary logic: height = scrollHeight
        textarea.style.height = textarea.scrollHeight + 'px';
        resizePty();
    }
};

textarea?.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        
        const rawInput = textarea.value.trim();
        if (!rawInput) return;

        let processedInput = rawInput;

        // PHASE 4 HOOK: Obsidian Knowledge Routing
        // If the user mentions notes, inject a strict system override into the prompt
        if (processedInput.toLowerCase().includes('notes')) {
            processedInput += `\n\n[SYSTEM DIRECTIVE: Any read/write operations regarding "notes" MUST exclusively target this absolute path: /Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/]`;
        }

        // Escape quotes and flatten newlines so the bash command doesn't break
        const escapedInput = processedInput.replace(/"/g, '\\"').replace(/\n/g, ' ');
        let commandToExecute = '';

        // FIXED ENGINE ROUTING
        if (currentEngine === 'claude') {
            // Force Claude Code CLI execution
            commandToExecute = `claude -p "${escapedInput}"`;
        } else if (currentEngine === 'agy') {
            // Use the correct interactive Antigravity syntax
            commandToExecute = `agy --add-dir=$PWD -i "${escapedInput}" --dangerously-skip-permissions`;
        }

        // PHASE 4 HOOK: Cost Telemetry Execution
        // Chain the python script to the end of the zsh command using standard bash sequential execution (;)
        const costScript = '/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py';
        commandToExecute += ` ; if [ -f "${costScript}" ]; then python3 "${costScript}"; fi`;

        const isBypass = e.metaKey || e.ctrlKey || e.altKey;

        if (isBypass) {
            // Send the prompt without sending /clear first
            invoke('write_to_pty', { data: commandToExecute + '\r' });
        } else {
            // Send a clear command to the active PTY
            invoke('write_to_pty', { data: '/clear\r' });
            // Asynchronous delay to allow CLI tool to process clear action
            await new Promise((resolve) => setTimeout(resolve, 450));
            // Send actual processed prompt
            invoke('write_to_pty', { data: commandToExecute + '\r' });
        }

        textarea.value = '';
        
        // Reset the textarea height back to the default
        adjustHeight();
    }
});

textarea?.addEventListener('input', adjustHeight);

// Tauri File Drop handling
listen<string[]>('tauri://file-drop', (event) => {
    if (!textarea) return;
    const paths = event.payload;
    if (paths && paths.length > 0) {
        const textToAppend = paths.join(' ');
        if (textarea.value) {
            textarea.value += ' ' + textToAppend;
        } else {
            textarea.value = textToAppend;
        }
        adjustHeight();
    }
});

// 5. Focus Management
textarea?.focus()
document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    const selection = window.getSelection()
    const isTerminalClick = container?.contains(target)

    if (isTerminalClick) {
        term.focus()
    } else if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && (!selection || selection.toString() === '')) {
        textarea?.focus()
    }
})
