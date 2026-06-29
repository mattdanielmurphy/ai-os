import '@xterm/xterm/css/xterm.css'
import './styles.css'

import { FitAddon } from '@xterm/addon-fit'
import { Terminal } from '@xterm/xterm'
import { invoke } from '@tauri-apps/api/tauri'
import { listen } from '@tauri-apps/api/event'
import { open } from '@tauri-apps/api/shell'
import { WebLinksAddon } from '@xterm/addon-web-links'

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
const claudeBuffers: Record<string, string> = {};
const agyBuffers: Record<string, string> = {};
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
    { path: '/Users/matthewmurphy/projects/ai-os', name: 'ai-os', color: '#3b82f6', lastActive: Date.now(), engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/structural-constraint-art', name: 'structural-constraint-art', color: '#ec4899', lastActive: Date.now() - 1000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/now-music', name: 'now-music', color: '#10b981', lastActive: Date.now() - 2000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/antigravity-optimization', name: 'antigravity-optimization', color: '#f59e0b', lastActive: Date.now() - 3000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/webpage-compressor', name: 'webpage-compressor', color: '#8b5cf6', lastActive: Date.now() - 4000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/tic-tac-toe', name: 'tic-tac-toe', color: '#ef4444', lastActive: Date.now() - 5000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/agy-animation', name: 'agy-animation', color: '#06b6d4', lastActive: Date.now() - 6000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/atlas-calculator', name: 'atlas-calculator', color: '#10b981', lastActive: Date.now() - 7000, engine: 'agy', isTerminalMode: false },
    { path: '/Users/matthewmurphy/projects/animation_project', name: 'animation_project', color: '#6366f1', lastActive: Date.now() - 8000, engine: 'agy', isTerminalMode: false }
];

// Load projects from localStorage or use initial list
let projects: Project[] = (() => {
    const saved = localStorage.getItem('ai-os-projects');
    if (saved) {
        try {
            const list = JSON.parse(saved);
            // Ensure all loaded projects have the engine and isTerminalMode properties
            return list.map((p: any) => ({
                engine: 'agy',
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

const handleLink = (e: MouseEvent, uri: string) => {
    if (e.metaKey || e.ctrlKey) {
        open(uri).catch(err => console.error("Failed to open link:", err));
    }
};

term.loadAddon(new WebLinksAddon(handleLink));

term.onData((data) => {
    invoke('write_to_pty', { data, projectPath: activeProject, terminalType: currentEngine }).catch((err) => {
        console.error('Failed to write key to Engine PTY:', err);
    });
});

term.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {
        e.preventDefault();
        invoke('write_to_pty', { data: '\x1b\x0d', projectPath: activeProject, terminalType: currentEngine }).catch(console.error);
        return false;
    }
    return true;
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
miniTerm.loadAddon(new WebLinksAddon(handleLink));

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

miniTerm.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {
        e.preventDefault();
        invoke('write_to_pty', { data: '\x1b\x0d', projectPath: activeProject, terminalType: 'mini' }).catch(console.error);
        return false;
    }
    return true;
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

let resizePtyTimeout: any = null;
const debouncedResizePty = () => {
    if (resizePtyTimeout) clearTimeout(resizePtyTimeout);
    resizePtyTimeout = setTimeout(() => {
        resizePty();
    }, 50);
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
    debouncedResizePty();
});

// Listen to Backend PTY events
listen<{ data: string, project_path: string, terminal_type: string }>('pty-output', (event) => {
    const { data, project_path, terminal_type } = event.payload;
    
    // Choose correct buffer
    let buffers = miniTermBuffers;
    if (terminal_type === 'claude') {
        buffers = claudeBuffers;
    } else if (terminal_type === 'agy') {
        buffers = agyBuffers;
    }
    
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
        } else if (terminal_type === currentEngine) {
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
            debouncedResizePty();
        }
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = '';
            resizePty();
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
            updatePlaceholder();
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
                invoke('close_project_session', { projectPath: project.path }).catch((err) => {
                    console.error('Failed to close project session in Rust:', err);
                });
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
    const activeBuffers = currentEngine === 'claude' ? claudeBuffers : agyBuffers;
    if (activeBuffers[path]) {
        term.write(activeBuffers[path]);
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
    
    commandHistory = loadCommandHistory(path);
    historyIndex = -1;
    currentDraft = '';
    
    // Reset pause state for the active project
    updatePauseUI('Running');
    
    // Request Rust backend to load/switch the project shell session
    try {
        await invoke<{ shell_pid: number, is_new_session: boolean }>('switch_active_project', { projectPath: path, engine: currentEngine });
        
        // PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
    } catch (e) {
        console.error('Failed to switch session in Rust:', e);
    }
    
    // Restore or initialize PTY geometry sync
    resizePty();
    renderProjects();
    adjustHeight();
};

// Add project modal and logic
const addProjectModal = document.getElementById('add-project-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const btnChoiceExisting = document.getElementById('btn-choice-existing');
const btnChoiceNew = document.getElementById('btn-choice-new');
const newProjectForm = document.getElementById('new-project-form');
const newProjNameInput = document.getElementById('new-proj-name') as HTMLInputElement;
const newProjGitInput = document.getElementById('new-proj-git') as HTMLInputElement;
const btnSubmitNewProject = document.getElementById('btn-submit-new-project') as HTMLButtonElement;

const openModal = () => {
    if (!addProjectModal) return;
    addProjectModal.classList.remove('hidden');
    // Force browser reflow to trigger CSS transitions
    addProjectModal.offsetHeight;
    addProjectModal.classList.remove('opacity-0');
    addProjectModal.classList.add('opacity-100');
    
    const modalContent = addProjectModal.querySelector('.transform');
    if (modalContent) {
        modalContent.classList.remove('scale-95');
        modalContent.classList.add('scale-100');
    }
    
    // Reset modal state
    if (newProjectForm) newProjectForm.classList.add('hidden');
    if (newProjNameInput) newProjNameInput.value = '';
    if (newProjGitInput) newProjGitInput.value = '';
};

const closeModal = () => {
    if (!addProjectModal) return;
    addProjectModal.classList.remove('opacity-100');
    addProjectModal.classList.add('opacity-0');
    
    const modalContent = addProjectModal.querySelector('.transform');
    if (modalContent) {
        modalContent.classList.remove('scale-100');
        modalContent.classList.add('scale-95');
    }
    
    // Hide modal element after transition completes
    setTimeout(() => {
        addProjectModal.classList.add('hidden');
    }, 300);
};

// Toggle modal visibility
const addProjectBtn = document.getElementById('add-project-btn');
addProjectBtn?.addEventListener('click', openModal);
closeModalBtn?.addEventListener('click', closeModal);

// Close modal when clicking on the backdrop (outside modal content)
addProjectModal?.addEventListener('click', (e) => {
    if (e.target === addProjectModal) {
        closeModal();
    }
});

// Helper to choose random color for project card
const getRandomProjectColor = () => {
    const colors = ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#6366f1', '#14b8a6', '#a855f7'];
    return colors[Math.floor(Math.random() * colors.length)];
};

// Open Existing Project via File Picker
btnChoiceExisting?.addEventListener('click', async () => {
    try {
        const selectedDir = await invoke<string | null>('select_directory');
        if (!selectedDir) return; // User canceled the dialog
        
        const cleanPath = selectedDir.trim();
        const name = cleanPath.split('/').pop() || 'unknown-project';
        
        const existing = projects.find(p => p.path === cleanPath);
        if (existing) {
            switchToProject(cleanPath);
            closeModal();
            return;
        }
        
        const newProj: Project = {
            path: cleanPath,
            name,
            color: getRandomProjectColor(),
            lastActive: Date.now(),
            engine: 'agy',
            isTerminalMode: false
        };
        
        projects.push(newProj);
        saveProjects();
        switchToProject(cleanPath);
        closeModal();
    } catch (err) {
        alert('Failed to select directory: ' + err);
    }
});

// Show New Project Form
btnChoiceNew?.addEventListener('click', () => {
    if (newProjectForm) {
        newProjectForm.classList.remove('hidden');
        newProjNameInput?.focus();
    }
});

// Auto-generate git repository name from project name
newProjNameInput?.addEventListener('input', () => {
    if (newProjGitInput) {
        // Convert to kebab-case
        const kebab = newProjNameInput.value
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');
        newProjGitInput.value = kebab;
    }
});

// Create & Initialize New Project
btnSubmitNewProject?.addEventListener('click', async () => {
    const name = newProjNameInput.value.trim();
    const gitRepoName = newProjGitInput.value.trim();
    
    if (!name) {
        alert('Please enter a project name.');
        return;
    }
    if (!gitRepoName) {
        alert('Please enter a git repository name.');
        return;
    }
    
    // Disable submit button and show loading state
    const originalText = btnSubmitNewProject.innerHTML;
    btnSubmitNewProject.disabled = true;
    btnSubmitNewProject.innerHTML = `<span class="inline-block animate-spin mr-2">🔄</span> Creating...`;
    
    try {
        const projectPath = await invoke<string>('create_new_project', { name, gitRepoName });
        
        const newProj: Project = {
            path: projectPath,
            name,
            color: getRandomProjectColor(),
            lastActive: Date.now(),
            engine: 'agy',
            isTerminalMode: false
        };
        
        projects.push(newProj);
        saveProjects();
        switchToProject(projectPath);
        closeModal();
    } catch (err) {
        alert('Failed to create project: ' + err);
    } finally {
        btnSubmitNewProject.disabled = false;
        btnSubmitNewProject.innerHTML = originalText;
    }
});

// ----------------------------------------------------
// 7. Engine Toggle & Routing
// ----------------------------------------------------
let currentEngine: 'claude' | 'agy' = 'agy'
const engineRadios = document.querySelectorAll<HTMLInputElement>('input[name="engine"]')

engineRadios.forEach((radio) => {
    radio.addEventListener('change', async (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy';
        // Persist setting on the active project
        const currentProj = projects.find(p => p.path === activeProject);
        if (currentProj) {
            currentProj.engine = currentEngine;
            saveProjects();
        }
        
        // Reset terminal screen and show matching engine buffer
        term.reset();
        const activeBuffers = currentEngine === 'claude' ? claudeBuffers : agyBuffers;
        if (activeBuffers[activeProject]) {
            term.write(activeBuffers[activeProject]);
        } else {
            term.write(`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${activeProject}...\x1b[0m\r\n`);
        }

        try {
            // Lazy spawn or switch to the engine on backend
            await invoke<{ shell_pid: number, is_new_session: boolean }>('switch_active_project', { 
                projectPath: activeProject, 
                engine: currentEngine 
            });

            // PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
        } catch (err) {
            console.error('Failed to toggle engine session on backend:', err);
        }
        
        resizePty();
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
const loadCommandHistory = (projectPath: string): string[] => {
    try {
        const historyJson = localStorage.getItem(`ai-os-history-${projectPath}`);
        if (historyJson) {
            return JSON.parse(historyJson);
        }
    } catch (e) {
        console.error('Failed to load command history', e);
    }
    return [];
};

const saveCommandHistory = (projectPath: string, history: string[]) => {
    try {
        localStorage.setItem(`ai-os-history-${projectPath}`, JSON.stringify(history));
    } catch (e) {
        console.error('Failed to save command history', e);
    }
};

let commandHistory: string[] = loadCommandHistory(activeProject);
let historyIndex = -1;
let currentDraft = '';

let arrowUpPressedOnce = false;
let arrowUpTimeout: any = null;
let arrowUpOverlay: HTMLDivElement | null = null;

const showArrowUpOverlay = () => {
    if (!arrowUpOverlay) {
        arrowUpOverlay = document.createElement('div');
        arrowUpOverlay.className = 'absolute top-0 left-0 right-0 bg-blue-600/90 text-white text-xs font-bold px-3 py-1.5 flex items-center justify-center rounded-t pointer-events-none z-10 animate-pulse transition-opacity';
        arrowUpOverlay.textContent = 'Press ArrowUp again to recall history';
        const bottomArea = document.getElementById('bottom-input-area');
        if (bottomArea) {
            bottomArea.appendChild(arrowUpOverlay);
        }
    }
    arrowUpOverlay.style.opacity = '1';
};

const hideArrowUpOverlay = () => {
    if (arrowUpOverlay) {
        arrowUpOverlay.style.opacity = '0';
        setTimeout(() => {
            if (arrowUpOverlay && arrowUpOverlay.style.opacity === '0') {
                arrowUpOverlay.remove();
                arrowUpOverlay = null;
            }
        }, 300);
    }
};


textarea?.addEventListener('keydown', async (e) => {
    if (e.key === 'ArrowUp') {
        if (textarea.selectionStart === 0 || historyIndex !== -1) {
            // If the textarea is empty, we don't need the double tap
            const isEmpty = textarea.value.trim() === '';
            
            if (!isEmpty && historyIndex === -1 && !arrowUpPressedOnce && commandHistory.length > 0) {
                arrowUpPressedOnce = true;
                showArrowUpOverlay();
                
                if (arrowUpTimeout) clearTimeout(arrowUpTimeout);
                arrowUpTimeout = setTimeout(() => {
                    arrowUpPressedOnce = false;
                    hideArrowUpOverlay();
                }, 2000);
                
                const resetArrowUpState = () => {
                    arrowUpPressedOnce = false;
                    hideArrowUpOverlay();
                    textarea.removeEventListener('input', resetArrowUpState);
                    textarea.removeEventListener('blur', resetArrowUpState);
                };
                textarea.addEventListener('input', resetArrowUpState);
                textarea.addEventListener('blur', resetArrowUpState);
                return;
            }
            
            e.preventDefault();
            
            if (arrowUpTimeout) clearTimeout(arrowUpTimeout);
            arrowUpPressedOnce = false;
            hideArrowUpOverlay();
            
            if (historyIndex === -1) {
                currentDraft = textarea.value;
            }
            if (historyIndex < commandHistory.length - 1) {
                historyIndex++;
                textarea.value = commandHistory[commandHistory.length - 1 - historyIndex];
                adjustHeight();
            }
        }
    } else if (e.key === 'ArrowDown') {
        if (arrowUpTimeout) clearTimeout(arrowUpTimeout);
        arrowUpPressedOnce = false;
        hideArrowUpOverlay();
        
        if (historyIndex !== -1) {
            e.preventDefault();
            if (historyIndex > 0) {
                historyIndex--;
                textarea.value = commandHistory[commandHistory.length - 1 - historyIndex];
                adjustHeight();
            } else if (historyIndex === 0) {
                historyIndex = -1;
                textarea.value = currentDraft;
                adjustHeight();
            }
        }
    } else if (e.key === 'Enter') {
        if (e.shiftKey) {
            // Shift+Enter: insert a newline at the cursor position explicitly
            e.preventDefault();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const value = textarea.value;
            textarea.value = value.substring(0, start) + '\n' + value.substring(end);
            textarea.selectionStart = textarea.selectionEnd = start + 1;
            adjustHeight();
            return;
        }

        e.preventDefault();
        
        let rawInput = textarea.value;
        const trimmedInput = rawInput.trim();
        if (!trimmedInput) return;

        commandHistory.push(trimmedInput);
        saveCommandHistory(activeProject, commandHistory);
        historyIndex = -1;

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

        const clearCheckbox = document.getElementById('clear-context-checkbox') as HTMLInputElement;
        const shouldClear = clearCheckbox ? clearCheckbox.checked : true;
        const isBypass = e.metaKey || e.ctrlKey || e.altKey || !shouldClear;

        if (isRunning) {
            // Use bracketed paste mode (\x1b[200~ ... \x1b[201~) so the PTY receives the block instantly and preserves literal newlines
            const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`;
            if (isBypass) {
                invoke('write_to_pty', { data: dataToSend, projectPath: activeProject, terminalType: currentEngine });
            } else {
                // Clear context first
                invoke('write_to_pty', { data: '/clear\r', projectPath: activeProject, terminalType: currentEngine });
                await new Promise((resolve) => setTimeout(resolve, 450));
                // Send prompt
                invoke('write_to_pty', { data: dataToSend, projectPath: activeProject, terminalType: currentEngine });
            }
        } else {
            if (currentEngine === 'agy') {
                try {
                    await invoke('spawn_fresh_engine', { projectPath: activeProject, engine: 'agy' });
                    // Wait a bit for the new instance to boot
                    await new Promise((resolve) => setTimeout(resolve, 1000));
                } catch (err) {
                    console.error('Failed to spawn fresh agy engine:', err);
                }
                const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`;
                
                // When TUI is fresh/exited, we NEVER need to clear context. It's a fresh instance.
                invoke('write_to_pty', { data: dataToSend, projectPath: activeProject, terminalType: 'agy' });
            } else {
                // Escape quotes but preserve literal newlines so the bash/tmux command inputs them properly
                const escapedInput = processedInput.replace(/"/g, '\\"');
                let commandToExecute = '';

                // FIXED ENGINE ROUTING
                if (currentEngine === 'claude') {
                    commandToExecute = `claude -p "${escapedInput}"`;
                }

                // Send command to active project PTY directly
                invoke('write_to_pty', { data: commandToExecute + '\r', projectPath: activeProject, terminalType: currentEngine });
            }
        }

        textarea.value = '';
        adjustHeight();

        // Auto-clear context toggle turns itself back on after each message is sent
        if (clearCheckbox) {
            clearCheckbox.checked = true;
            autoClearContext = true;
            localStorage.setItem('ai-os-auto-clear', 'true');
            // We poll is_engine_running in the background, but we can optimistically call updatePlaceholder(true) since we just spawned/used it
            updatePlaceholder(true);
        }
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
// 8. Clipboard Copy & Paste for TUI (xterm.js)
// ----------------------------------------------------
document.addEventListener('keydown', (e) => {
    // Intercept Cmd+C (Mac) or Ctrl+C to copy selected text from xterm.js or window
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'c') {
        let textToCopy = '';
        const activeEl = document.activeElement;
        
        // Only prioritize xterm.js selections if the terminal elements are focused
        if (activeEl && (container?.contains(activeEl) || term.element?.contains(activeEl))) {
            if (term.hasSelection()) {
                textToCopy = term.getSelection();
            } else {
                invoke('copy_tmux_selection', { projectPath: activeProject, terminalType: currentEngine }).catch((err) => {
                    console.error('Failed to copy tmux selection:', err);
                });
            }
        } else if (activeEl && (miniContainer?.contains(activeEl) || miniTerm.element?.contains(activeEl))) {
            if (miniTerm.hasSelection()) {
                textToCopy = miniTerm.getSelection();
            } else {
                invoke('copy_tmux_selection', { projectPath: activeProject, terminalType: 'mini' }).catch((err) => {
                    console.error('Failed to copy tmux selection:', err);
                });
            }
        } else {
            textToCopy = window.getSelection()?.toString() || '';
        }
        
        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy).catch((err) => {
                console.error('Failed to copy text:', err);
            });
        }
    }
});

document.addEventListener('paste', async (e) => {
    // If user is focused on the prompt input, let default paste happen
    if (document.activeElement === textarea) {
        return;
    }
    let pastedText = e.clipboardData?.getData('text');
    if (pastedText) {
        const activeEl = document.activeElement;
        const isEngineFocus = activeEl && (container?.contains(activeEl) || term.element?.contains(activeEl));
        
        if (isEngineFocus) {
            let isRunning = false;
            try {
                isRunning = await invoke<boolean>('is_engine_running', { engine: currentEngine, projectPath: activeProject });
            } catch (err) {
                console.error('Failed to check if engine is running:', err);
            }
            if (isRunning) {
                // When pasting directly into an active interactive session, map newlines to Esc+LF (\x1b\n)
                // so the interactive shell buffers the entire pasted block without submitting line-by-line
                pastedText = pastedText.replace(/\r\n/g, '\n').replace(/\n/g, '\x1b\n');
            }
            invoke('write_to_pty', { data: pastedText, projectPath: activeProject, terminalType: currentEngine });
        } else if (activeEl && (miniContainer?.contains(activeEl) || miniTerm.element?.contains(activeEl))) {
            // For raw terminals/shells, use bracketed paste sequences if multiline to prevent premature executes
            if (pastedText.includes('\n')) {
                invoke('write_to_pty', { data: '\x1b[200~' + pastedText + '\x1b[201~', projectPath: activeProject, terminalType: 'mini' });
            } else {
                invoke('write_to_pty', { data: pastedText, projectPath: activeProject, terminalType: 'mini' });
            }
        }
    }
});

// ----------------------------------------------------
// 9. Focus Management & Initialization
// ----------------------------------------------------
textarea?.focus();

// Auto-clear context checkbox handling
const clearCheckbox = document.getElementById('clear-context-checkbox') as HTMLInputElement;
let autoClearContext = true;
const savedAutoClear = localStorage.getItem('ai-os-auto-clear');
if (savedAutoClear !== null) {
    autoClearContext = savedAutoClear === 'true';
}

const updatePlaceholder = (isRunning = true) => {
    const contextContainer = document.getElementById('clear-context-container');
    const labelText = document.getElementById('clear-context-label-text');
    if (textarea) {
        if (!isRunning) {
            textarea.placeholder = `Type a prompt... [Will launch ${currentEngine} and send] (Enter to send, Shift+Enter for newline)`;
            if (contextContainer) {
                contextContainer.style.display = 'none';
            }
        } else {
            if (contextContainer) {
                contextContainer.style.display = 'flex';
            }
            if (clearCheckbox && clearCheckbox.checked) {
                textarea.placeholder = "Type a prompt... [Runs /clear first] (Enter to send, Shift+Enter for newline)";
                if (contextContainer) {
                    contextContainer.className = "flex items-center cursor-pointer select-none text-xs font-bold px-2 py-0.5 rounded border transition-all bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
                }
                if (labelText) labelText.textContent = "Auto-Clear: ACTIVE";
            } else {
                textarea.placeholder = "Type a prompt... [Continuing thread] (Enter to send, Shift+Enter for newline)";
                if (contextContainer) {
                    contextContainer.className = "flex items-center cursor-pointer select-none text-xs font-medium px-2 py-0.5 rounded border transition-all bg-gray-900/40 border-gray-800 text-gray-500 hover:text-gray-400";
                }
                if (labelText) labelText.textContent = "Auto-Clear: OFF";
            }
        }
    }
};

if (clearCheckbox) {
    clearCheckbox.checked = autoClearContext;
    clearCheckbox.addEventListener('change', () => {
        autoClearContext = clearCheckbox.checked;
        localStorage.setItem('ai-os-auto-clear', String(autoClearContext));
        updatePlaceholder();
    });
    // Call initially
    setTimeout(updatePlaceholder, 100);
}

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
            updatePlaceholder();
        }
    }
});

// Initialize workspace session
(async () => {
    try {
        const initialProject = await invoke<string | null>('get_initial_project');
        if (initialProject) {
            const cleanPath = initialProject.trim();
            const existing = projects.find(p => p.path === cleanPath);
            if (existing) {
                activeProject = cleanPath;
            } else {
                const name = cleanPath.split('/').pop() || 'unknown-project';
                const newProj: Project = {
                    path: cleanPath,
                    name,
                    color: getRandomProjectColor(),
                    lastActive: Date.now(),
                    engine: 'agy',
                    isTerminalMode: false
                };
                projects.push(newProj);
                saveProjects();
                activeProject = cleanPath;
            }
        }
    } catch (e) {
        console.error('Failed to get initial project:', e);
    }
    await switchToProject(activeProject);
    renderProjects();
})();

// Poll engine running state
setInterval(async () => {
    if (!activeProject || isTerminalMode) return;
    try {
        const isRunning = await invoke<boolean>('is_engine_running', { engine: currentEngine, projectPath: activeProject });
        // Only update if we aren't showing the arrow up overlay (so we don't mess up placeholder)
        if (!arrowUpPressedOnce) {
            updatePlaceholder(isRunning);
        }
    } catch (e) {
        console.error(e);
    }
}, 1000);
