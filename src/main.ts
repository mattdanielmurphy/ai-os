import '@xterm/xterm/css/xterm.css'
import './styles.css'

import { FitAddon } from '@xterm/addon-fit'
import { Terminal } from '@xterm/xterm'
import { invoke } from '@tauri-apps/api/tauri'
import { listen } from '@tauri-apps/api/event'

// ----------------------------------------------------
// 1. Interfaces & Types
// ----------------------------------------------------
interface Project {
    path: string;
    name: string;
    color: string;
    lastActive: number; // timestamp
}

// ----------------------------------------------------
// 2. Global State Management
// ----------------------------------------------------
let activeProject: string = '/Users/matthewmurphy/projects/ai-os';
let isTerminalMode: boolean = false; // '!' mode

// In-memory cache for terminal history of each project, so we can restore screen instantly when switching
const terminalBuffers: Record<string, string> = {};

let isPaused: boolean = false;
const pauseBtnEl = document.getElementById('pause-btn');

const updatePauseUI = (paused: boolean) => {
    isPaused = paused;
    if (pauseBtnEl) {
        if (paused) {
            pauseBtnEl.textContent = 'Resume';
            pauseBtnEl.className = 'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-400 border border-yellow-500/30 transition-all select-none cursor-pointer';
        } else {
            pauseBtnEl.textContent = 'Pause';
            pauseBtnEl.className = 'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 transition-all select-none cursor-pointer';
        }
    }
};

pauseBtnEl?.addEventListener('click', async () => {
    const nextPauseState = !isPaused;
    try {
        await invoke('toggle_process_pause', { projectPath: activeProject, pause: nextPauseState });
        updatePauseUI(nextPauseState);
    } catch (e) {
        console.error('Failed to toggle pause:', e);
    }
});

// Hardcoded initial projects list mapped with unique random colors
const initialProjects: Project[] = [
    { path: '/Users/matthewmurphy/projects/ai-os', name: 'ai-os', color: '#3b82f6', lastActive: Date.now() },
    { path: '/Users/matthewmurphy/projects/structural-constraint-art', name: 'structural-constraint-art', color: '#ec4899', lastActive: Date.now() - 1000 },
    { path: '/Users/matthewmurphy/projects/now-music', name: 'now-music', color: '#10b981', lastActive: Date.now() - 2000 },
    { path: '/Users/matthewmurphy/projects/antigravity-optimization', name: 'antigravity-optimization', color: '#f59e0b', lastActive: Date.now() - 3000 },
    { path: '/Users/matthewmurphy/projects/webpage-compressor', name: 'webpage-compressor', color: '#8b5cf6', lastActive: Date.now() - 4000 },
    { path: '/Users/matthewmurphy/projects/tic-tac-toe', name: 'tic-tac-toe', color: '#ef4444', lastActive: Date.now() - 5000 },
    { path: '/Users/matthewmurphy/projects/agy-animation', name: 'agy-animation', color: '#06b6d4', lastActive: Date.now() - 6000 },
    { path: '/Users/matthewmurphy/projects/atlas-calculator', name: 'atlas-calculator', color: '#10b981', lastActive: Date.now() - 7000 },
    { path: '/Users/matthewmurphy/projects/animation_project', name: 'animation_project', color: '#6366f1', lastActive: Date.now() - 8000 }
];

// Load projects from localStorage or use initial list
let projects: Project[] = (() => {
    const saved = localStorage.getItem('ai-os-projects');
    if (saved) {
        try {
            return JSON.parse(saved);
        } catch (e) {
            console.error('Failed to parse saved projects:', e);
        }
    }
    return initialProjects;
})();

const saveProjects = () => {
    localStorage.setItem('ai-os-projects', JSON.stringify(projects));
};

// ----------------------------------------------------
// 3. Terminal Setup & Integration
// ----------------------------------------------------
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
    // Write direct key input to the PTY for the active project
    invoke('write_to_pty', { data, projectPath: activeProject }).catch((err) => {
        console.error('Failed to write direct key input to PTY:', err);
    });
});

// Helper function to fit and sync geometry with Rust
const resizePty = () => {
    fitAddon.fit();
    invoke('resize_pty', { rows: term.rows, cols: term.cols, projectPath: activeProject }).catch((err) => {
        console.error('Failed to resize PTY:', err);
    });
};

const container = document.getElementById('terminal-container');
if (container) {
    term.open(container);
    // Add custom cursor styling logic or layout adjustments
}

window.addEventListener('resize', () => {
    resizePty();
});

// Listen to Backend PTY events
listen<{ data: string, project_path: string }>('pty-output', (event) => {
    const { data, project_path } = event.payload;
    
    // Append to cache buffer
    if (!terminalBuffers[project_path]) {
        terminalBuffers[project_path] = '';
    }
    terminalBuffers[project_path] += data;
    // Limit cache size to prevent massive leaks (~100k characters)
    if (terminalBuffers[project_path].length > 100000) {
        terminalBuffers[project_path] = terminalBuffers[project_path].substring(terminalBuffers[project_path].length - 50000);
    }

    // Only write output on screen if it belongs to the currently active project
    if (project_path === activeProject) {
        term.write(data);
    }
});

// ----------------------------------------------------
// 4. UI Rendering: Sidebar & Project Swapper
// ----------------------------------------------------
const projectsListEl = document.getElementById('projects-list');
const currentDirPathEl = document.getElementById('current-dir-path');

const renderProjects = () => {
    if (!projectsListEl) return;
    projectsListEl.innerHTML = '';
    
    // Sort by recency
    const sorted = [...projects].sort((a, b) => b.lastActive - a.lastActive);
    
    sorted.forEach((project) => {
        const item = document.createElement('div');
        const isActive = project.path === activeProject;
        
        item.className = `flex items-center justify-between p-2 rounded cursor-pointer transition-all border ${
            isActive 
                ? 'bg-gray-800 border-gray-700 text-white font-medium shadow-sm' 
                : 'bg-transparent border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'
        }`;
        
        // Tab content
        item.innerHTML = `
            <div class="flex items-center gap-2.5 truncate">
                <span class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${project.color}"></span>
                <span class="truncate text-xs">${project.name}</span>
            </div>
            <button class="delete-btn text-[10px] text-gray-600 hover:text-red-400 px-1 py-0.5 rounded opacity-0 hover:opacity-100 hover:bg-gray-700 transition-all select-none">✕</button>
        `;
        
        // Swap project click
        item.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            if (target.classList.contains('delete-btn')) {
                e.stopPropagation();
                // Delete project
                projects = projects.filter(p => p.path !== project.path);
                saveProjects();
                // If deleted active, switch to first available
                if (activeProject === project.path && projects.length > 0) {
                    switchToProject(projects[0].path);
                } else {
                    renderProjects();
                }
                return;
            }
            switchToProject(project.path);
        });
        
        // Show delete button on hover
        item.addEventListener('mouseenter', () => {
            const btn = item.querySelector('.delete-btn') as HTMLElement;
            if (btn && project.path !== '/Users/matthewmurphy/projects/ai-os') {
                btn.style.opacity = '1';
            }
        });
        item.addEventListener('mouseleave', () => {
            const btn = item.querySelector('.delete-btn') as HTMLElement;
            if (btn) btn.style.opacity = '0';
        });

        projectsListEl.appendChild(item);
    });
};

// Switch active project workspace
const switchToProject = async (path: string) => {
    activeProject = path;
    
    // Update lastActive timestamp
    const proj = projects.find(p => p.path === path);
    if (proj) {
        proj.lastActive = Date.now();
        saveProjects();
    }
    
    // Clear terminal screen and dump cached history
    term.reset();
    if (terminalBuffers[path]) {
        term.write(terminalBuffers[path]);
    } else {
        // First boot of shell, or empty cache.
        term.write(`\r\n\x1b[1;34m[ai-os] Connecting to project session at: ${path}...\x1b[0m\r\n`);
    }

    if (currentDirPathEl) {
        currentDirPathEl.textContent = path;
    }
    
    // Reset pause state for the active project
    updatePauseUI(false);
    
    // Request Rust backend to load/switch the project shell session
    try {
        const result = await invoke<{ shell_pid: number, is_new_session: boolean }>('switch_active_project', { projectPath: path });
        
        // Auto-spawn active engine if this session is brand new (e.g. fresh tmux session)
        if (result.is_new_session) {
            let startupCmd = '';
            if (currentEngine === 'claude') {
                startupCmd = 'claude\r';
            } else if (currentEngine === 'agy') {
                startupCmd = 'agy --add-dir=$PWD --dangerously-skip-permissions\r';
            }
            if (startupCmd) {
                setTimeout(() => {
                    invoke('write_to_pty', { data: startupCmd, projectPath: path });
                }, 500);
            }
        }
    } catch (e) {
        console.error('Failed to switch session in Rust:', e);
    }
    
    // Restore or initialize PTY geometry sync
    resizePty();
    renderProjects();
};

// Add project button
const addProjectBtn = document.getElementById('add-project-btn');
addProjectBtn?.addEventListener('click', async () => {
    const pathInput = prompt('Enter absolute path to the project directory:');
    if (!pathInput) return;
    
    const cleanPath = pathInput.trim();
    if (!cleanPath) return;
    
    // Extract project name from path
    const name = cleanPath.split('/').pop() || 'unknown-project';
    
    // Check if already exists
    const existing = projects.find(p => p.path === cleanPath);
    if (existing) {
        switchToProject(cleanPath);
        return;
    }
    
    // Assign a unique random pastel color
    const colors = ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#6366f1', '#14b8a6', '#a855f7'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    
    const newProj: Project = {
        path: cleanPath,
        name,
        color: randomColor,
        lastActive: Date.now()
    };
    
    projects.push(newProj);
    saveProjects();
    switchToProject(cleanPath);
});

// ----------------------------------------------------
// 5. Engine Toggle & Routing
// ----------------------------------------------------
let currentEngine: 'claude' | 'agy' = 'claude'
const engineRadios = document.querySelectorAll<HTMLInputElement>('input[name="engine"]')

engineRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy'
    })
})

// ----------------------------------------------------
// 6. Mode Switch: Terminal Mode VS Prompt Mode
// ----------------------------------------------------
const modeBadgeEl = document.getElementById('mode-badge');
const textarea = document.getElementById('prompt-input') as HTMLTextAreaElement;
const terminalExitHintEl = document.getElementById('terminal-exit-hint');

const setMode = (terminalMode: boolean) => {
    isTerminalMode = terminalMode;
    if (modeBadgeEl) {
        if (terminalMode) {
            modeBadgeEl.textContent = 'Terminal Mode';
            modeBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-widest bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
            textarea.placeholder = "Terminal command mode active. Type command (e.g. 'ls', 'git status', 'exit') and Enter...";
            terminalExitHintEl?.classList.remove('hidden');
        } else {
            modeBadgeEl.textContent = 'Prompt Mode';
            modeBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-widest bg-blue-500/20 text-blue-400 border border-blue-500/30';
            textarea.placeholder = "Type a command or prompt... (Type '!' at start for Terminal Mode, Enter to send)";
            terminalExitHintEl?.classList.add('hidden');
        }
    }
};

// ----------------------------------------------------
// 7. Input Interception & Routing
// ----------------------------------------------------
const adjustHeight = () => {
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
        resizePty();
    }
};

textarea?.addEventListener('keydown', async (e) => {
    // If escape key is pressed, exit terminal mode
    if (e.key === 'Escape' && isTerminalMode) {
        setMode(false);
        textarea.value = '';
        adjustHeight();
        return;
    }

    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        
        let rawInput = textarea.value;
        
        // Check for '!' trigger at the beginning to change modes
        if (rawInput.trim().startsWith('!')) {
            // strip out ! and change mode to terminal mode
            const cmd = rawInput.trim().substring(1).trim();
            setMode(true);
            textarea.value = cmd;
            adjustHeight();
            return;
        }

        const trimmedInput = rawInput.trim();
        if (!trimmedInput) return;

        // If in terminal mode and user types 'exit', exit terminal mode
        if (isTerminalMode && (trimmedInput === 'exit' || trimmedInput === 'exit()')) {
            setMode(false);
            textarea.value = '';
            adjustHeight();
            return;
        }

        if (isTerminalMode) {
            // Write command directly to active project shell PTY
            const dataToSend = trimmedInput + '\r';
            invoke('write_to_pty', { data: dataToSend, projectPath: activeProject });
            textarea.value = '';
            adjustHeight();
            return;
        }

        // --- Prompt Mode Engine Routing Logic ---
        let processedInput = trimmedInput;

        // Obsidian Knowledge Routing
        if (processedInput.toLowerCase().includes('notes')) {
            processedInput += `\n\n[SYSTEM DIRECTIVE: Any read/write operations regarding "notes" MUST exclusively target this absolute path: /Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/]`;
        }

        let isRunning = false;
        try {
            isRunning = await invoke<boolean>('is_engine_running', { engine: currentEngine, projectPath: activeProject });
        } catch (err) {
            console.error('Failed to check if engine is running:', err);
        }

        if (isRunning) {
            // Send prompt raw directly to the running interactive interface (stdin)
            const dataToSend = processedInput.replace(/\n/g, '\r') + '\r';
            invoke('write_to_pty', { data: dataToSend, projectPath: activeProject });
        } else {
            // Escape quotes and flatten newlines so the bash command doesn't break
            const escapedInput = processedInput.replace(/"/g, '\\"').replace(/\n/g, ' ');
            let commandToExecute = '';

            // FIXED ENGINE ROUTING
            if (currentEngine === 'claude') {
                commandToExecute = `claude -p "${escapedInput}"`;
            } else if (currentEngine === 'agy') {
                commandToExecute = `agy --add-dir=$PWD -i "${escapedInput}" --dangerously-skip-permissions`;
            }

            // Cost Telemetry execution hook
            const costScript = '/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py';
            commandToExecute += ` ; if [ -f "${costScript}" ]; then python3 "${costScript}"; fi`;

            const isBypass = e.metaKey || e.ctrlKey || e.altKey;

            if (isBypass) {
                // Send command to active project PTY without clearing
                invoke('write_to_pty', { data: commandToExecute + '\r', projectPath: activeProject });
            } else {
                // Send clear context command
                invoke('write_to_pty', { data: '/clear\r', projectPath: activeProject });
                await new Promise((resolve) => setTimeout(resolve, 450));
                // Send command
                invoke('write_to_pty', { data: commandToExecute + '\r', projectPath: activeProject });
            }
        }

        textarea.value = '';
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

// ----------------------------------------------------
// 8. Focus Management & Initialization
// ----------------------------------------------------
textarea?.focus();

document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const selection = window.getSelection();
    const isTerminalClick = container?.contains(target);
    const isSidebarClick = document.getElementById('projects-sidebar')?.contains(target);

    if (isTerminalClick) {
        term.focus();
    } else if (!isSidebarClick && target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && (!selection || selection.toString() === '')) {
        textarea?.focus();
    }
});

// Initialize workspace session
(async () => {
    await switchToProject(activeProject);
    renderProjects();
})();

