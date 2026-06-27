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
    engine: 'claude' | 'agy';
    promptDraft?: string;
    isTerminalMode?: boolean;
}

// ----------------------------------------------------
// 2. Global State Management
// ----------------------------------------------------
let activeProject: string = '/Users/matthewmurphy/projects/ai-os';
let isTerminalMode: boolean = false;

// In-memory cache for terminal history of each project, so we can restore screen instantly when switching
const engineBuffers: Record<string, string> = {};
const miniTermBuffers: Record<string, string> = {};

let pauseStatus: 'Running' | 'Pending' | 'Paused' = 'Running';
const pauseBtnEl = document.getElementById('pause-btn');

const updatePauseUI = (status: 'Running' | 'Pending' | 'Paused') => {
    pauseStatus = status;
    if (pauseBtnEl) {
        if (status === 'Pending') {
            pauseBtnEl.textContent = 'Pending...';
            pauseBtnEl.className = 'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-orange-600/20 hover:bg-orange-600/40 text-orange-400 border border-orange-500/30 animate-pulse transition-all select-none cursor-pointer';
        } else if (status === 'Paused') {
            pauseBtnEl.textContent = 'Resume';
            pauseBtnEl.className = 'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-400 border border-yellow-500/30 transition-all select-none cursor-pointer';
        } else {
            pauseBtnEl.textContent = 'Pause';
            pauseBtnEl.className = 'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 transition-all select-none cursor-pointer';
        }
    }
};

pauseBtnEl?.addEventListener('click', async () => {
    const requestPause = (pauseStatus === 'Running');
    try {
        await invoke('toggle_process_pause', { projectPath: activeProject, pause: requestPause });
    } catch (e) {
        console.error('Failed to toggle pause:', e);
    }
});

listen<{ project_path: string, status: 'Running' | 'Pending' | 'Paused' }>('pause-status', (event) => {
    const { project_path, status } = event.payload;
    if (project_path === activeProject) {
        updatePauseUI(status);
    }
});

// Hardcoded initial projects list mapped with unique random colors and default engines
const initialProjects: Project[] = [
    { path: '/Users/matthewmurphy/projects/ai-os', name: 'ai-os', color: '#3b82f6', lastActive: Date.now(), engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/structural-constraint-art', name: 'structural-constraint-art', color: '#ec4899', lastActive: Date.now() - 1000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/now-music', name: 'now-music', color: '#10b981', lastActive: Date.now() - 2000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/antigravity-optimization', name: 'antigravity-optimization', color: '#f59e0b', lastActive: Date.now() - 3000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/webpage-compressor', name: 'webpage-compressor', color: '#8b5cf6', lastActive: Date.now() - 4000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/tic-tac-toe', name: 'tic-tac-toe', color: '#ef4444', lastActive: Date.now() - 5000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/agy-animation', name: 'agy-animation', color: '#06b6d4', lastActive: Date.now() - 6000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/atlas-calculator', name: 'atlas-calculator', color: '#10b981', lastActive: Date.now() - 7000, engine: 'claude', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/animation_project', name: 'animation_project', color: '#6366f1', lastActive: Date.now() - 8000, engine: 'claude', isTerminalMode: false }
];

// Load projects from localStorage or use initial list
let projects: Project[] = (() => {
    const saved = localStorage.getItem('ai-os-projects');
    if (saved) {
        try {
            const list = JSON.parse(saved);
            // Ensure all loaded projects have the engine and isTerminalMode properties
            return list.map((p: any) => ({
                engine: 'claude',
                isTerminalMode: false,
                ...p
            }));
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
// 3. Terminals Setup & Integration
// ----------------------------------------------------

// Engine TUI Terminal
const term = new Terminal({
    cursorBlink: true,
    fontSize: 13,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: { background: '#000000', foreground: '#ffffff' },
});
const fitAddon = new FitAddon();
term.loadAddon(fitAddon);

term.onData((data) => {
    invoke('write_to_pty', { data, projectPath: activeProject, terminalType: 'engine' }).catch((err) => {
        console.error('Failed to write key to Engine PTY:', err);
    });
});

// Mini Terminal
const miniTerm = new Terminal({
    cursorBlink: true,
    fontSize: 12,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: { background: '#000000', foreground: '#10b981' }, // pastel green font for distinct look
});
const miniFitAddon = new FitAddon();
miniTerm.loadAddon(miniFitAddon);

let miniInputBuffer = '';

miniTerm.onData((data) => {
    // Intercept Escape key
    if (data === '\x1b') {
        exitTerminalMode();
        return;
    }
    
    // Write directly to PTY
    invoke('write_to_pty', { data, projectPath: activeProject, terminalType: 'mini' }).catch((err) => {
        console.error('Failed to write key to Mini PTY:', err);
    });

    // Check buffer for command exits
    for (let i = 0; i < data.length; i++) {
        const char = data[i];
        if (char === '\r' || char === '\n') {
            const cmd = miniInputBuffer.trim();
            if (cmd === 'exit' || cmd === 'exit()') {
                exitTerminalMode();
            }
            miniInputBuffer = '';
        } else if (char === '\x7f' || char === '\x08') {
            miniInputBuffer = miniInputBuffer.slice(0, -1);
        } else {
            miniInputBuffer += char;
        }
    }
});

const exitTerminalMode = () => {
    isTerminalMode = false;
    const currentProj = projects.find(p => p.path === activeProject);
    if (currentProj) {
        currentProj.isTerminalMode = false;
        saveProjects();
    }
    applyTerminalModeUI();
};

const resizePty = () => {
    fitAddon.fit();
    miniFitAddon.fit();
    invoke('resize_pty', { rows: term.rows, cols: term.cols, projectPath: activeProject, terminalType: 'engine' }).catch((err) => {
        console.error('Failed to resize Engine PTY:', err);
    });
    invoke('resize_pty', { rows: miniTerm.rows, cols: miniTerm.cols, projectPath: activeProject, terminalType: 'mini' }).catch((err) => {
        console.error('Failed to resize Mini PTY:', err);
    });
};

const container = document.getElementById('terminal-container');
if (container) {
    term.open(container);
}

const miniContainer = document.getElementById('mini-terminal-container');
if (miniContainer) {
    miniTerm.open(miniContainer);
}

window.addEventListener('resize', () => {
    resizePty();
});

// Listen to Backend PTY events
listen<{ data: string, project_path: string, terminal_type: string }>('pty-output', (event) => {
    const { data, project_path, terminal_type } = event.payload;
    
    // Choose correct buffer
    const buffers = terminal_type === 'mini' ? miniTermBuffers : engineBuffers;
    
    // Append to cache buffer
    if (!buffers[project_path]) {
        buffers[project_path] = '';
    }
    buffers[project_path] += data;
    // Limit cache size to prevent massive leaks
    if (buffers[project_path].length > 100000) {
        buffers[project_path] = buffers[project_path].substring(buffers[project_path].length - 50000);
    }

    // Only write output on screen if it belongs to the currently active project
    if (project_path === activeProject) {
        if (terminal_type === 'mini') {
            miniTerm.write(data);
        } else {
            term.write(data);
        }
    }
});

// ----------------------------------------------------
// 4. Splitter Drag Resizing Panel
// ----------------------------------------------------
const splitter = document.getElementById('pane-splitter');
const panesContainer = document.getElementById('panes-container');

if (splitter && miniContainer && panesContainer) {
    let isDragging = false;
    
    splitter.addEventListener('mousedown', (e) => {
        isDragging = true;
        document.body.style.cursor = 'row-resize';
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const containerRect = panesContainer.getBoundingClientRect();
        const newMiniHeight = containerRect.bottom - e.clientY - (splitter.offsetHeight / 2);
        
        const minHeight = 50;
        const maxHeight = containerRect.height * 0.8;
        
        if (newMiniHeight >= minHeight && newMiniHeight <= maxHeight) {
            miniContainer.style.height = `${newMiniHeight}px`;
            resizePty();
        }
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = '';
        }
    });
}

// ----------------------------------------------------
// 5. Dynamic Mode UI Application
// ----------------------------------------------------
const applyTerminalModeUI = () => {
    const bottomArea = document.getElementById('bottom-input-area');
    
    if (isTerminalMode) {
        if (splitter) splitter.style.display = 'block';
        if (miniContainer) miniContainer.style.display = 'block';
        if (bottomArea) bottomArea.style.display = 'none';
        setTimeout(() => {
            miniTerm.focus();
            resizePty();
        }, 50);
    } else {
        if (splitter) splitter.style.display = 'none';
        if (miniContainer) miniContainer.style.display = 'none';
        if (bottomArea) bottomArea.style.display = 'flex';
        setTimeout(() => {
            textarea?.focus();
            resizePty();
        }, 50);
    }
};

// ----------------------------------------------------
// 6. UI Rendering: Sidebar & Project Swapper
// ----------------------------------------------------
const projectsListEl = document.getElementById('projects-list');
const currentDirPathEl = document.getElementById('current-dir-path');
const textarea = document.getElementById('prompt-input') as HTMLTextAreaElement;

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
    // Save draft and engine setting of the current project before switching
    const currentProj = projects.find(p => p.path === activeProject);
    if (currentProj) {
        currentProj.promptDraft = textarea ? textarea.value : '';
        currentProj.engine = currentEngine;
        currentProj.isTerminalMode = isTerminalMode;
    }

    activeProject = path;
    
    // Update lastActive timestamp & restore state
    const nextProj = projects.find(p => p.path === path);
    if (nextProj) {
        nextProj.lastActive = Date.now();
        if (textarea) {
            textarea.value = nextProj.promptDraft || '';
        }
        if (nextProj.engine) {
            currentEngine = nextProj.engine;
            const radio = document.querySelector(`input[name="engine"][value="${nextProj.engine}"]`) as HTMLInputElement;
            if (radio) {
                radio.checked = true;
            }
        }
        isTerminalMode = !!nextProj.isTerminalMode;
        applyTerminalModeUI();
        saveProjects();
    }
    
    // Clear terminal screens and dump cached history
    term.reset();
    if (engineBuffers[path]) {
        term.write(engineBuffers[path]);
    } else {
        term.write(`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${path}...\x1b[0m\r\n`);
    }

    miniTerm.reset();
    if (miniTermBuffers[path]) {
        miniTerm.write(miniTermBuffers[path]);
    } else {
        miniTerm.write(`\r\n\x1b[1;32m[ai-os] Connecting to Shell session at: ${path}...\x1b[0m\r\n`);
    }

    if (currentDirPathEl) {
        currentDirPathEl.textContent = path;
    }
    
    // Reset pause state for the active project
    updatePauseUI('Running');
    
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
                    invoke('write_to_pty', { data: startupCmd, projectPath: path, terminalType: 'engine' });
                }, 500);
            }
        }
    } catch (e) {
        console.error('Failed to switch session in Rust:', e);
    }
    
    // Restore or initialize PTY geometry sync
    resizePty();
    renderProjects();
    adjustHeight();
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
        lastActive: Date.now(),
        engine: 'claude',
        isTerminalMode: false
    };
    
    projects.push(newProj);
    saveProjects();
    switchToProject(cleanPath);
});

// ----------------------------------------------------
// 7. Engine Toggle & Routing
// ----------------------------------------------------
let currentEngine: 'claude' | 'agy' = 'claude'
const engineRadios = document.querySelectorAll<HTMLInputElement>('input[name="engine"]')

engineRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy';
        // Persist setting on the active project
        const currentProj = projects.find(p => p.path === activeProject);
        if (currentProj) {
            currentProj.engine = currentEngine;
            saveProjects();
        }
    });
});

// ----------------------------------------------------
// 8. Input Interception & Routing
// ----------------------------------------------------
const adjustHeight = () => {
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
        resizePty();
    }
};

textarea?.addEventListener('input', () => {
    // Instantly toggle to terminal mode when user types exactly "!" in empty field
    if (textarea.value === '!') {
        isTerminalMode = true;
        const currentProj = projects.find(p => p.path === activeProject);
        if (currentProj) {
            currentProj.isTerminalMode = true;
            saveProjects();
        }
        applyTerminalModeUI();
        textarea.value = '';
        adjustHeight();
    } else {
        adjustHeight();
    }
});

textarea?.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        
        let rawInput = textarea.value;
        const trimmedInput = rawInput.trim();
        if (!trimmedInput) return;

        // Prompt Mode Engine Routing Logic
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
            invoke('write_to_pty', { data: dataToSend, projectPath: activeProject, terminalType: 'engine' });
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
                invoke('write_to_pty', { data: commandToExecute + '\r', projectPath: activeProject, terminalType: 'engine' });
            } else {
                // Send clear context command
                invoke('write_to_pty', { data: '/clear\r', projectPath: activeProject, terminalType: 'engine' });
                await new Promise((resolve) => setTimeout(resolve, 450));
                // Send command
                invoke('write_to_pty', { data: commandToExecute + '\r', projectPath: activeProject, terminalType: 'engine' });
            }
        }

        textarea.value = '';
        adjustHeight();
    }
});

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
// 9. Focus Management & Initialization
// ----------------------------------------------------
textarea?.focus();

document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const selection = window.getSelection();
    
    // Focus appropriate terminal or textarea
    const isEngineTermClick = container?.contains(target);
    const isMiniTermClick = miniContainer?.contains(target);
    const isSidebarClick = document.getElementById('projects-sidebar')?.contains(target);

    if (isEngineTermClick) {
        term.focus();
    } else if (isMiniTermClick) {
        miniTerm.focus();
    } else if (!isSidebarClick && target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && (!selection || selection.toString() === '')) {
        if (isTerminalMode) {
            miniTerm.focus();
        } else {
            textarea?.focus();
        }
    }
});

// Initialize workspace session
(async () => {
    await switchToProject(activeProject);
    renderProjects();
})();
