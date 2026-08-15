import re
import os

with open("index.html", "r") as f:
    html = f.read()

html = re.sub(
    r'<!-- TUI Toggle Bar / Divider -->.*?</div>',
    '''<!-- TUI Toggle Bar / Divider -->
                <div
                    id="tui-toggle-bar"
                    class="tui-toggle-bar"
                    data-ui="tui-toggle-bar"
                >
                    <div id="tui-resize-handle" class="tui-resize-handle"></div>
                    <span style="pointer-events: none;">Engine TUI Session</span>
                    
                    <div class="terminal-presets" data-ui="terminal-presets">
                        <button class="preset-btn" data-preset="0" title="Preset 1 (Small)">1</button>
                        <button class="preset-btn" data-preset="1" title="Preset 2 (Medium)">2</button>
                        <button class="preset-btn" data-preset="2" title="Preset 3 (Large)">3</button>
                    </div>
                </div>''',
    html,
    flags=re.DOTALL
)
with open("index.html", "w") as f:
    f.write(html)

with open("src/styles.css", "a") as f:
    f.write('''
/* TUI Resize & Presets */
.tui-resize-handle {
  position: absolute;
  top: -3px;
  left: 0;
  right: 0;
  height: 6px;
  cursor: row-resize;
  z-index: 10;
}
.tui-toggle-bar {
  position: relative;
}
.terminal-presets {
  display: flex;
  gap: 6px;
}
.preset-btn {
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.8rem;
}
.preset-btn:hover {
  color: var(--text-main);
  border-color: var(--text-muted);
}
.preset-btn.active {
  background: var(--btn-primary-bg);
  color: white;
  border-color: var(--btn-primary-bg);
}
''')

# Now for main.ts
with open("src/main.ts", "r") as f:
    main = f.read()

# Add window imports
main = re.sub(
    r"import { invoke } from '@tauri-apps/api/tauri'",
    "import { invoke } from '@tauri-apps/api/tauri'\nimport { appWindow, PhysicalSize, PhysicalPosition } from '@tauri-apps/api/window'",
    main
)

# Add Window restore state at beginning after imports
restore_code = '''
// Restore Window State
async function restoreWindowState() {
    try {
        const sizeStr = localStorage.getItem('windowSize')
        if (sizeStr) {
            const { width, height } = JSON.parse(sizeStr)
            await appWindow.setSize(new PhysicalSize(width, height))
        }
        const posStr = localStorage.getItem('windowPosition')
        if (posStr) {
            const { x, y } = JSON.parse(posStr)
            await appWindow.setPosition(new PhysicalPosition(x, y))
        }
    } catch (e) {
        console.error('Failed to restore window state:', e)
    }

    appWindow.onResized(async ({ payload: size }) => {
        localStorage.setItem('windowSize', JSON.stringify({ width: size.width, height: size.height }))
    })
    appWindow.onMoved(async ({ payload: position }) => {
        localStorage.setItem('windowPosition', JSON.stringify({ x: position.x, y: position.y }))
    })
}
restoreWindowState()
'''
main = main.replace("// ----------------------------------------------------\n// 1. Interfaces & Types", restore_code + "\n// ----------------------------------------------------\n// 1. Interfaces & Types")

# Sidebar restore
sidebar_logic = '''
// 4a. Sidebar Width Resizing
const sidebarSplitter = document.getElementById('sidebar-splitter')
const sidebar = document.getElementById('projects-sidebar')

if (sidebarSplitter && sidebar) {
    const savedSidebarWidth = localStorage.getItem('sidebarWidth')
    if (savedSidebarWidth) {
        sidebar.style.width = `${savedSidebarWidth}px`
    }

    let isDragging = false
    let startX = 0
    let startWidth = 0

    sidebarSplitter.addEventListener('mousedown', (e) => {
        isDragging = true
        startX = e.clientX
        startWidth = sidebar.offsetWidth
        document.body.style.cursor = 'col-resize'
        e.preventDefault()
    })

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return

        const deltaX = e.clientX - startX
        const newWidth = startWidth + deltaX
        const minWidth = 150
        const maxWidth = 600

        if (newWidth >= minWidth && newWidth <= maxWidth) {
            sidebar.style.width = `${newWidth}px`
            localStorage.setItem('sidebarWidth', newWidth.toString())
            debouncedResizePty()
        }
    })
'''
main = re.sub(r"// 4a. Sidebar Width Resizing.*?\n    document\.addEventListener\('mousemove', \(e\) => \{.*?\n    \}\)\n", sidebar_logic, main, flags=re.DOTALL)

# Terminal Presets Logic
terminal_logic = '''
// TUI Presets & Drag Resizing
const tuiContainer = document.getElementById('terminal-container')
const previewWrapper = document.getElementById('preview-wrapper')
const tuiResizeHandle = document.getElementById('tui-resize-handle')
const presetBtns = document.querySelectorAll('.preset-btn')

let terminalPresets = [110, 300, 600]
try {
    const savedPresets = localStorage.getItem('terminalPresets')
    if (savedPresets) terminalPresets = JSON.parse(savedPresets)
} catch (e) {}

let activeTerminalPreset = 0
try {
    const savedActivePreset = localStorage.getItem('activeTerminalPreset')
    if (savedActivePreset !== null) activeTerminalPreset = parseInt(savedActivePreset, 10)
} catch (e) {}

function applyTerminalPreset(index: number) {
    activeTerminalPreset = index
    localStorage.setItem('activeTerminalPreset', index.toString())
    presetBtns.forEach(btn => btn.classList.remove('active'))
    const activeBtn = document.querySelector(`.preset-btn[data-preset="${index}"]`)
    if (activeBtn) activeBtn.classList.add('active')
    
    if (tuiContainer && previewWrapper) {
        tuiContainer.style.height = `${terminalPresets[index]}px`
        // if large enough, maybe hide preview entirely?
        // Let's just adjust flex space. 
    }
    
    setTimeout(() => resizePty(), 50)
    setTimeout(() => resizePty(), 150)
}

if (presetBtns.length > 0) {
    presetBtns.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            const el = e.currentTarget as HTMLElement
            const index = parseInt(el.dataset.preset || '0', 10)
            applyTerminalPreset(index)
        })
    })
}

// Initial application
applyTerminalPreset(activeTerminalPreset)

// Resizing logic for Terminal
if (tuiResizeHandle && tuiContainer && previewWrapper) {
    let isResizingTui = false
    let startY = 0
    let startHeight = 0

    tuiResizeHandle.addEventListener('mousedown', (e) => {
        isResizingTui = true
        startY = e.clientY
        startHeight = tuiContainer.offsetHeight
        document.body.style.cursor = 'row-resize'
        e.preventDefault()
    })

    document.addEventListener('mousemove', (e) => {
        if (!isResizingTui) return
        const deltaY = startY - e.clientY // Dragging UP increases height
        let newHeight = startHeight + deltaY
        const minHeight = 50
        const maxHeight = window.innerHeight - 100 // Leave some space for header

        if (newHeight >= minHeight && newHeight <= maxHeight) {
            tuiContainer.style.height = `${newHeight}px`
            terminalPresets[activeTerminalPreset] = newHeight
            localStorage.setItem('terminalPresets', JSON.stringify(terminalPresets))
            debouncedResizePty()
        }
    })

    document.addEventListener('mouseup', () => {
        if (isResizingTui) {
            isResizingTui = false
            document.body.style.cursor = 'default'
            resizePty()
        }
    })
}

// Remove auto-expand interactive override or point it to preset 1
'''
main = re.sub(
    r"// TUI Toggle Button Event Listener\nconst toggleTuiBtn = document\.getElementById\('toggle-tui-btn'\).*?isTuiExpanded = false\n\n",
    terminal_logic + "\n\n",
    main,
    flags=re.DOTALL
)

# Remove `isTuiExpanded` usage in interactive detection
main = re.sub(
    r"if \(isInteractive && tuiContainer && !isTuiExpanded && !userManuallyCollapsedTui\) {.*?\}",
    r'''if (isInteractive && tuiContainer && activeTerminalPreset === 0) {
                        applyTerminalPreset(1); // Auto-expand to medium on prompt if small
                    }''',
    main,
    flags=re.DOTALL
)

with open("src/main.ts", "w") as f:
    f.write(main)

print("Patch applied successfully.")
