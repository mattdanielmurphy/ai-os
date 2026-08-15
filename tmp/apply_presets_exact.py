import os

with open("index.html", "r") as f:
    html = f.read()

toggle_bar_html = '''                <!-- TUI Toggle Bar / Divider -->
                <div
                    id="tui-toggle-bar"
                    class="tui-toggle-bar"
                    data-ui="tui-toggle-bar"
                >
                    <span>Engine TUI Session</span>
                    <button
                        id="toggle-tui-btn"
                        class="toggle-tui-btn"
                        data-ui="toggle-tui-btn"
                    >
                        <span>Expand Terminal</span>
                        <svg
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2.5"
                                d="M19 9l-7 7-7-7"
                            ></path>
                        </svg>
                    </button>
                </div>'''

new_toggle_bar_html = '''                <!-- TUI Toggle Bar / Divider -->
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
                </div>'''

if toggle_bar_html in html:
    html = html.replace(toggle_bar_html, new_toggle_bar_html)
with open("index.html", "w") as f:
    f.write(html)

with open("src/main.ts", "r") as f:
    main = f.read()

main = main.replace(
    "import { invoke } from '@tauri-apps/api/tauri'",
    "import { invoke } from '@tauri-apps/api/tauri'\nimport { appWindow, PhysicalSize, PhysicalPosition } from '@tauri-apps/api/window'"
)

restore_code = '''// ----------------------------------------------------
// 1. Interfaces & Types
// ----------------------------------------------------
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
main = main.replace("// ----------------------------------------------------\n// 1. Interfaces & Types\n// ----------------------------------------------------", restore_code)


interactive_override = '''                    if (isInteractive && tuiContainer && !isTuiExpanded && !userManuallyCollapsedTui) {
                        const toggleBtn = document.getElementById('toggle-tui-btn');
                        if (toggleBtn) {
                            toggleBtn.click(); // Auto-expand
                        }
                    }'''
new_interactive = '''                    if (isInteractive && tuiContainer && activeTerminalPreset === 0) {
                        applyTerminalPreset(1); // Auto-expand to medium on prompt if small
                    }'''
main = main.replace(interactive_override, new_interactive)


tui_btn_logic = '''// TUI Toggle Button Event Listener
const toggleTuiBtn = document.getElementById('toggle-tui-btn')
const tuiContainer = document.getElementById('terminal-container')
const previewWrapper = document.getElementById('preview-wrapper')

if (toggleTuiBtn && tuiContainer && previewWrapper) {
    toggleTuiBtn.addEventListener('click', () => {
        isTuiExpanded = !isTuiExpanded
        if (isTuiExpanded) {
            userManuallyCollapsedTui = false
            // Expand
            tuiContainer.style.height = 'calc(100% - 28px)'
            previewWrapper.style.display = 'none'
            toggleTuiBtn.innerHTML = `
                <span>Collapse Terminal</span>
                <svg class="ts-html-element-33" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
            `
        } else {
            userManuallyCollapsedTui = true
            // Collapse
            tuiContainer.style.height = '110px'
            previewWrapper.style.display = 'flex'
            toggleTuiBtn.innerHTML = `
                <span>Expand Terminal</span>
                <svg class="ts-html-element-34" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
            `
        }
        setTimeout(() => {
            resizePty()
        }, 50)
        setTimeout(() => {
            resizePty()
        }, 150)
        setTimeout(() => {
            resizePty()
        }, 320)
    })
}'''

new_tui_btn_logic = '''// TUI Presets & Drag Resizing
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
    }
    
    setTimeout(() => {
        try { resizePty(); } catch (e) {}
    }, 50)
    setTimeout(() => {
        try { resizePty(); } catch (e) {}
    }, 150)
}
(window as any).applyTerminalPreset = applyTerminalPreset;

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
        const maxHeight = window.innerHeight - 100

        if (newHeight >= minHeight && newHeight <= maxHeight) {
            tuiContainer.style.height = `${newHeight}px`
            terminalPresets[activeTerminalPreset] = newHeight
            localStorage.setItem('terminalPresets', JSON.stringify(terminalPresets))
            try { debouncedResizePty() } catch (e) {}
        }
    })

    document.addEventListener('mouseup', () => {
        if (isResizingTui) {
            isResizingTui = false
            document.body.style.cursor = 'default'
            try { resizePty() } catch (e) {}
        }
    })
}'''
main = main.replace(tui_btn_logic, new_tui_btn_logic)


sidebar_base = '''// 4a. Sidebar Width Resizing
const sidebarSplitter = document.getElementById('sidebar-splitter')
const sidebar = document.getElementById('projects-sidebar')

if (sidebarSplitter && sidebar) {
    let isDragging = false
    let startX = 0
    let startWidth = 0'''

new_sidebar_base = '''// 4a. Sidebar Width Resizing
const sidebarSplitter = document.getElementById('sidebar-splitter')
const sidebar = document.getElementById('projects-sidebar')

if (sidebarSplitter && sidebar) {
    const savedSidebarWidth = localStorage.getItem('sidebarWidth')
    if (savedSidebarWidth) {
        sidebar.style.width = `${savedSidebarWidth}px`
    }

    let isDragging = false
    let startX = 0
    let startWidth = 0'''

main = main.replace(sidebar_base, new_sidebar_base)

# Inject saving to sidebar resize
sidebar_resize_target = '''        if (newWidth >= minWidth && newWidth <= maxWidth) {
            sidebar.style.width = `${newWidth}px`
            debouncedResizePty()
        }'''
new_sidebar_resize_target = '''        if (newWidth >= minWidth && newWidth <= maxWidth) {
            sidebar.style.width = `${newWidth}px`
            localStorage.setItem('sidebarWidth', newWidth.toString())
            debouncedResizePty()
        }'''
main = main.replace(sidebar_resize_target, new_sidebar_resize_target)


with open("src/main.ts", "w") as f:
    f.write(main)

print("Exact match patched.")
