import { invoke, listen, appWindow } from './tauriWrapper';

interface StagedPayload {
    thread_id: string;
    thread_title: string;
    phase: number;
    payload: string;
    source_url: string;
    security_token: string;
}

interface WorkspaceItem {
    path: string;
    last_used: number;
}

interface WorkspacesConfig {
    recent: WorkspaceItem[];
    pinned: WorkspaceItem[];
}

let activePayload: StagedPayload | null = null;
let selectedWorkspacePath: string = 'scratchpad';
let selectedMode: 'worker' | 'triage' = 'worker';
let selectedEngine: 'agy' | 'claude' | 'hermes' = 'agy';

document.addEventListener('DOMContentLoaded', async () => {
    const threadTitleBadge = document.getElementById('thread-title-badge');
    const previewText = document.getElementById('preview-text');
    const workspaceList = document.getElementById('workspace-list');
    const btnBrowseDir = document.getElementById('btn-browse-dir');
    const btnModeWorker = document.getElementById('btn-mode-worker');
    const btnModeTriage = document.getElementById('btn-mode-triage');
    const btnEngineAgy = document.getElementById('btn-engine-agy');
    const btnEngineClaude = document.getElementById('btn-engine-claude');
    const btnEngineHermes = document.getElementById('btn-engine-hermes');
    const btnCancel = document.getElementById('btn-cancel-execution');
    const btnConfirm = document.getElementById('btn-confirm-execution');

    // Fetch and populate payload
    const loadPayload = (payload: StagedPayload) => {
        if (!payload) return;
        activePayload = payload;
        if (threadTitleBadge) {
            threadTitleBadge.innerText = payload.thread_title || 'Payload';
        }
        if (previewText) {
            previewText.innerText = payload.payload || 'No instructions provided.';
        }
    };

    try {
        const staged = await invoke<StagedPayload | null>('get_staged_payload');
        if (staged) {
            loadPayload(staged);
        }
    } catch (e) {
        console.error("Failed to load initial staged payload", e);
    }

    // Listen for real-time payload updates
    listen<StagedPayload>('load-payload', (event) => {
        loadPayload(event.payload);
    });

    // Populate recent workspaces list
    const populateWorkspaces = async () => {
        if (!workspaceList) return;
        
        try {
            const config = await invoke<WorkspacesConfig>('get_recent_workspaces');
            
            // Build HTML
            let html = '';
            
            // Always have Scratchpad
            html += `
                <div class="workspace-item ${selectedWorkspacePath === 'scratchpad' ? 'selected' : ''}" data-path="scratchpad">
                    <div>
                        <div class="workspace-name">Scratchpad</div>
                        <div class="workspace-path">Temporary sandbox execution</div>
                    </div>
                </div>
            `;

            if (config && config.recent && config.recent.length > 0) {
                config.recent.forEach(ws => {
                    const parts = ws.path.split('/');
                    const name = parts[parts.length - 1] || ws.path;
                    html += `
                        <div class="workspace-item ${selectedWorkspacePath === ws.path ? 'selected' : ''}" data-path="${ws.path}">
                            <div>
                                <div class="workspace-name">${name}</div>
                                <div class="workspace-path">${ws.path}</div>
                            </div>
                        </div>
                    `;
                });
            }

            workspaceList.innerHTML = html;

            // Re-attach click listeners
            const items = workspaceList.querySelectorAll('.workspace-item');
            items.forEach(item => {
                item.addEventListener('click', () => {
                    items.forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');
                    selectedWorkspacePath = item.getAttribute('data-path') || 'scratchpad';
                });
            });

        } catch (e) {
            console.error("Failed to fetch workspaces list", e);
        }
    };

    await populateWorkspaces();

    // Directory Browser
    if (btnBrowseDir) {
        btnBrowseDir.addEventListener('click', async () => {
            try {
                const selectedDir = await invoke<string | null>('select_directory');
                if (selectedDir) {
                    selectedWorkspacePath = selectedDir;
                    // Re-render workspaces list, including the new one
                    await populateWorkspaces();
                    // Auto-select the newly added workspace
                    const items = workspaceList?.querySelectorAll('.workspace-item');
                    items?.forEach(item => {
                        if (item.getAttribute('data-path') === selectedDir) {
                            items.forEach(i => i.classList.remove('selected'));
                            item.classList.add('selected');
                        }
                    });
                }
            } catch (e) {
                console.error("Failed to open directory browser", e);
            }
        });
    }

    // Mode Buttons
    if (btnModeWorker && btnModeTriage) {
        btnModeWorker.addEventListener('click', () => {
            btnModeWorker.classList.add('selected');
            btnModeTriage.classList.remove('selected');
            selectedMode = 'worker';
        });

        btnModeTriage.addEventListener('click', () => {
            btnModeTriage.classList.add('selected');
            btnModeWorker.classList.remove('selected');
            selectedMode = 'triage';
        });
    }

    // Engine Buttons
    const engineBtns = [
        { el: btnEngineAgy, value: 'agy' as const },
        { el: btnEngineClaude, value: 'claude' as const },
        { el: btnEngineHermes, value: 'hermes' as const },
    ];
    engineBtns.forEach(({ el, value }) => {
        if (el) {
            el.addEventListener('click', () => {
                engineBtns.forEach(btn => btn.el?.classList.remove('selected'));
                el.classList.add('selected');
                selectedEngine = value;
            });
        }
    });

    // Actions
    if (btnCancel) {
        btnCancel.addEventListener('click', async () => {
            await appWindow.hide();
        });
    }

    if (btnConfirm) {
        btnConfirm.addEventListener('click', async () => {
            if (!activePayload) {
                alert("No staged execution task payload found.");
                return;
            }

            let targetPath = selectedWorkspacePath;
            if (targetPath === 'scratchpad') {
                // Determine a scratchpad directory (e.g. workspaceRoot/tmp or similar)
                // Let's query targetPath using the active project root or standard tmp.
                // Wait! Let's get the initial project path or use current directory.
                try {
                    const initialProj = await invoke<string>('get_initial_project');
                    targetPath = initialProj ? `${initialProj}/tmp` : './tmp';
                } catch {
                    targetPath = './tmp';
                }
            }

            try {
                btnConfirm.innerText = 'Initializing...';
                btnConfirm.setAttribute('disabled', 'true');
                
                await invoke('confirm_staged_execution', {
                    projectPath: targetPath,
                    engine: selectedEngine,
                    mode: selectedMode,
                    payload: activePayload.payload
                });
                
                // Hide window
                await appWindow.hide();
            } catch (err) {
                console.error("Execution confirm failed:", err);
                alert("Failed to confirm staged execution: " + String(err));
            } finally {
                btnConfirm.innerText = 'Execute Task';
                btnConfirm.removeAttribute('disabled');
            }
        });
    }
});
