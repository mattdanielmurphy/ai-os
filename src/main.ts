import '@xterm/xterm/css/xterm.css'
import './styles.css'

import type { ILink, ILinkProvider } from '@xterm/xterm'

import { FitAddon } from '@xterm/addon-fit'
import { Terminal } from '@xterm/xterm'
import { WebLinksAddon } from '@xterm/addon-web-links'
import { invoke } from '@tauri-apps/api/tauri'
import { listen } from '@tauri-apps/api/event'
import { marked } from 'marked'
import { open } from '@tauri-apps/api/shell'

window.addEventListener('keydown', (e) => {
    if (e.metaKey && e.altKey && e.key.toLowerCase() === 'i') {
        invoke('open_devtools').catch(console.error)
    }
    if (e.metaKey && e.key.toLowerCase() === 'n') {
        e.preventDefault()
        const newThreadBtn = document.querySelector(
            '.new-thread-btn'
        ) as HTMLButtonElement | null
        if (newThreadBtn) {
            newThreadBtn.click()
        }
    }
})

// ----------------------------------------------------
// 1. Interfaces & Types
// ----------------------------------------------------
interface Project {
    path: string
    name: string
    color: string
    lastActive: number // timestamp
    engine: 'claude' | 'agy'
    promptDraft?: string
    isTerminalMode?: boolean
}

// ----------------------------------------------------
// 2. Global State Management
// ----------------------------------------------------
let activeProject: string = '/Users/matthewmurphy/projects/ai-os'

const formatPathForUser = (
    path: string,
    projectPath: string = activeProject
): string => {
    if (!path) return ''
    const projectPrefix = projectPath.endsWith('/')
        ? projectPath
        : projectPath + '/'
    if (path.startsWith(projectPrefix)) {
        return path.substring(projectPrefix.length)
    }
    return path.replace('/Users/matthewmurphy', '~')
}

let isTerminalMode: boolean = false
let isTuiExpanded: boolean = false
let activeThreadId: string | null = null
let activeThreadContext: string | null = null
const threadFilepaths = new Map<string, string>()
const threadLatestLeafIds = new Map<string, string>()
let lastThreadsJson = ''
let isWaitingForNewThread = false
let waitingExistingThreadIds: Set<string> = new Set()
let saveDraftTimeout: any = null
let saveProjectsTimeout: any = null
const saveProjectsDebounced = () => {
    if (saveProjectsTimeout) clearTimeout(saveProjectsTimeout)
    saveProjectsTimeout = setTimeout(() => {
        saveProjects()
    }, 500)
}

const savePromptDraft = (content: string) => {
    if (!activeProject) return
    localStorage.setItem(`ai-os-prompt-draft-${activeProject}`, content)

    const currentProj = projects.find((p) => p.path === activeProject)
    if (currentProj) {
        currentProj.promptDraft = content
        saveProjectsDebounced()
    }

    const isWordCompleted =
        content.endsWith(' ') ||
        content.endsWith('\n') ||
        content.endsWith('\t')

    if (saveDraftTimeout) {
        clearTimeout(saveDraftTimeout)
    }

    const writeToDisk = () => {
        invoke('save_prompt_draft', {
            projectPath: activeProject,
            content,
        }).catch((err) =>
            console.error('Failed to save prompt draft to disk:', err)
        )
    }

    if (isWordCompleted) {
        writeToDisk()
    } else {
        saveDraftTimeout = setTimeout(writeToDisk, 150)
    }
}

// In-memory cache for terminal history of each project, so we can restore screen instantly when switching
const claudeBuffers: Record<string, string> = {}
const agyBuffers: Record<string, string> = {}
const miniTermBuffers: Record<string, string> = {}

let pauseStatus: 'Running' | 'Pending' | 'Paused' = 'Running'
const pauseBtnEl = document.getElementById('pause-btn')

const updatePauseUI = (status: 'Running' | 'Pending' | 'Paused') => {
    pauseStatus = status
    if (pauseBtnEl) {
        if (status === 'Pending') {
            pauseBtnEl.textContent = 'Pending...'
            pauseBtnEl.className =
                'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-orange-600/20 hover:bg-orange-600/40 text-orange-400 border border-orange-500/30 animate-pulse transition-all select-none cursor-pointer'
        } else if (status === 'Paused') {
            pauseBtnEl.textContent = 'Resume'
            pauseBtnEl.className =
                'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-400 border border-yellow-500/30 transition-all select-none cursor-pointer'
        } else {
            pauseBtnEl.textContent = 'Pause'
            pauseBtnEl.className =
                'px-2.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-red-600/20 hover:bg-red-600/40 text-red-400 border border-red-500/30 transition-all select-none cursor-pointer'
        }
    }
}

pauseBtnEl?.addEventListener('click', async () => {
    const requestPause = pauseStatus === 'Running'
    try {
        await invoke('toggle_process_pause', {
            projectPath: activeProject,
            pause: requestPause,
        })
    } catch (e) {
        console.error('Failed to toggle pause:', e)
    }
})

listen<{ project_path: string; status: 'Running' | 'Pending' | 'Paused' }>(
    'pause-status',
    (event) => {
        const { project_path, status } = event.payload
        if (project_path === activeProject) {
            updatePauseUI(status)
            if (activeThreadId && typeof lastRenderedThreadLog === 'string' && typeof renderCustomTuiLog === 'function') {
                renderCustomTuiLog(lastRenderedThreadLog)
            }
        }
    }
)

// Hardcoded initial projects list mapped with unique random colors and default engines
const initialProjects: Project[] = [
    {
        path: '/Users/matthewmurphy/projects/ai-os',
        name: 'ai-os',
        color: '#3b82f6',
        lastActive: Date.now(),
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/structural-constraint-art',
        name: 'structural-constraint-art',
        color: '#ec4899',
        lastActive: Date.now() - 1000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/now-music',
        name: 'now-music',
        color: '#10b981',
        lastActive: Date.now() - 2000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/antigravity-optimization',
        name: 'antigravity-optimization',
        color: '#f59e0b',
        lastActive: Date.now() - 3000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/webpage-compressor',
        name: 'webpage-compressor',
        color: '#8b5cf6',
        lastActive: Date.now() - 4000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/tic-tac-toe',
        name: 'tic-tac-toe',
        color: '#ef4444',
        lastActive: Date.now() - 5000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/agy-animation',
        name: 'agy-animation',
        color: '#06b6d4',
        lastActive: Date.now() - 6000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/atlas-calculator',
        name: 'atlas-calculator',
        color: '#10b981',
        lastActive: Date.now() - 7000,
        engine: 'agy',
        isTerminalMode: false,
    },
    {
        path: '/Users/matthewmurphy/projects/animation_project',
        name: 'animation_project',
        color: '#6366f1',
        lastActive: Date.now() - 8000,
        engine: 'agy',
        isTerminalMode: false,
    },
]

// Load projects from localStorage or use initial list
let projects: Project[] = (() => {
    const saved = localStorage.getItem('ai-os-projects')
    let loadedList: any[] = []
    if (saved) {
        try {
            loadedList = JSON.parse(saved)
        } catch (e) {
            console.error('Failed to parse saved projects:', e)
            loadedList = initialProjects
        }
    } else {
        loadedList = initialProjects
    }

    const uniqueProjectsMap = new Map<string, Project>()
    for (const p of loadedList) {
        let cleanPath = p.path || ''
        if (cleanPath.includes('/projects/thread-')) {
            continue // Filter out legacy mock thread projects
        }
        while (cleanPath.length > 0 && /[`*.,:;)}"\]]$/.test(cleanPath)) {
            cleanPath = cleanPath.slice(0, -1)
        }
        let cleanName = p.name || ''
        while (cleanName.length > 0 && /[`*.,:;)}"\]]$/.test(cleanName)) {
            cleanName = cleanName.slice(0, -1)
        }

        if (!cleanPath) continue

        const mapped: Project = {
            path: cleanPath,
            name: cleanName,
            color: p.color || '#3b82f6',
            lastActive: p.lastActive || Date.now(),
            engine: p.engine || 'agy',
            isTerminalMode: p.isTerminalMode || false,
        }

        const existing = uniqueProjectsMap.get(cleanPath)
        if (!existing || mapped.lastActive > existing.lastActive) {
            uniqueProjectsMap.set(cleanPath, mapped)
        }
    }

    const cleaned = Array.from(uniqueProjectsMap.values())
    cleaned.sort((a, b) => b.lastActive - a.lastActive)

    // Save back the cleaned version immediately if we changed anything
    if (saved && cleaned.length !== loadedList.length) {
        try {
            localStorage.setItem('ai-os-projects', JSON.stringify(cleaned))
        } catch (e) {
            console.error('Failed to save cleaned projects:', e)
        }
    }
    return cleaned
})()

const saveProjects = () => {
    localStorage.setItem('ai-os-projects', JSON.stringify(projects))
}

// ----------------------------------------------------
// 3. Terminals Setup & Integration
// ----------------------------------------------------

const isDarkMode = () =>
    window.matchMedia('(prefers-color-scheme: dark)').matches

const applyTheme = () => {
    if (isDarkMode()) {
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.classList.remove('dark')
    }
}

// Initialize dark mode class on load
applyTheme()

const getTermTheme = () => {
    return isDarkMode()
        ? { background: '#000000', foreground: '#ffffff' }
        : { background: '#ffffff', foreground: '#000000' }
}

const getMiniTermTheme = () => {
    return isDarkMode()
        ? { background: '#000000', foreground: '#10b981' }
        : { background: '#ffffff', foreground: '#059669' }
}

// Engine TUI Terminal
const term = new Terminal({
    cursorBlink: true,
    fontSize: 13,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: getTermTheme(),
})
const fitAddon = new FitAddon()
term.loadAddon(fitAddon)

const handleLink = (_e: MouseEvent, uri: string) => {
    if (true) {
        let finalUri = uri

        // Handle web URLs
        if (finalUri.startsWith('http://') || finalUri.startsWith('https://')) {
            open(finalUri).catch((err) =>
                console.error('Failed to open web link:', err)
            )
            return
        }

        // Clean up file:// prefix if present
        if (finalUri.startsWith('file://')) {
            finalUri = finalUri.replace('file://', '')
        }

        // Resolve relative paths against the active project
        if (!finalUri.startsWith('/') && !finalUri.startsWith('~/')) {
            if (finalUri.startsWith('./')) {
                finalUri = finalUri.slice(2)
            }
            finalUri = `${activeProject}/${finalUri}`
        }

        // Use custom rust command to circumvent Tauri `open` URL restrictions
        invoke('open_path', { path: finalUri }).catch((err) =>
            console.error('Failed to open path:', err)
        )
    }
}

;(window as any).openPath = (path: string) => {
    invoke('open_path', { path }).catch((err) =>
        console.error('Failed to open path:', err)
    )
}

class LocalPathLinkProvider implements ILinkProvider {
    constructor(
        private term: Terminal,
        private handler: (e: MouseEvent, uri: string) => void
    ) {}
    provideLinks(
        bufferLineNumber: number,
        callback: (links: ILink[] | undefined) => void
    ): void {
        const line = this.term.buffer.active.getLine(bufferLineNumber - 1)
        if (!line) {
            callback(undefined)
            return
        }
        const text = line.translateToString(true)
        // Include URLs as well in this regex if needed? No, WebLinksAddon does URLs.
        const regex = /(?:file:\/\/)?[a-zA-Z0-9_.~-]*(?:\/[a-zA-Z0-9_.-]+)+/g
        const links: ILink[] = []
        let match
        while ((match = regex.exec(text)) !== null) {
            links.push({
                range: {
                    start: { x: match.index + 1, y: bufferLineNumber },
                    end: {
                        x: match.index + match[0].length,
                        y: bufferLineNumber,
                    },
                },
                text: match[0],
                activate: (e: MouseEvent, text: string) =>
                    this.handler(e, text),
            })
        }
        callback(links)
    }
}

term.loadAddon(new WebLinksAddon(handleLink))
term.registerLinkProvider(new LocalPathLinkProvider(term, handleLink))

term.onData((data) => {
    invoke('write_to_pty', {
        data,
        projectPath: activeProject,
        terminalType: currentEngine,
    }).catch((err) => {
        console.error('Failed to write key to Engine PTY:', err)
    })

    // Auto-adjust terminal height when user starts typing a slash command
    setTimeout(() => {
        const cursorLine = term.buffer.active.getLine(
            term.buffer.active.cursorY + term.buffer.active.baseY
        )
        const lineText = cursorLine ? cursorLine.translateToString().trim() : ''
        const tuiContainer = document.getElementById('terminal-container')
        if (tuiContainer && !isTuiExpanded) {
            if (lineText.startsWith('/')) {
                tuiContainer.style.height = '320px'
                debouncedResizePty()
            } else if (tuiContainer.style.height === '320px') {
                tuiContainer.style.height = '64px'
                debouncedResizePty()
            }
        }
    }, 20)
})

term.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {
        e.preventDefault()
        invoke('write_to_pty', {
            data: '\x1b\x0d',
            projectPath: activeProject,
            terminalType: currentEngine,
        }).catch(console.error)
        return false
    }
    return true
})

// Mini Terminal
const miniTerm = new Terminal({
    cursorBlink: true,
    fontSize: 12,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    theme: getMiniTermTheme(),
})

window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', (e) => {
        applyTheme()
        term.options.theme = getTermTheme()
        miniTerm.options.theme = getMiniTermTheme()

        // Inject the theme command to the backend engines ONLY if active engine is Claude
        if (currentEngine === 'claude' && activeProject) {
            const themeStr = e.matches ? 'dark' : 'light'
            const msg = `/theme ${themeStr}\x0d`
            invoke('write_to_pty', {
                data: msg,
                projectPath: activeProject,
                terminalType: 'claude',
            }).catch(console.error)
        }
    })
const miniFitAddon = new FitAddon()
miniTerm.loadAddon(miniFitAddon)
miniTerm.loadAddon(new WebLinksAddon(handleLink))
miniTerm.registerLinkProvider(new LocalPathLinkProvider(miniTerm, handleLink))

let miniInputBuffer = ''

miniTerm.onData((data) => {
    // Intercept Escape key
    if (data === '\x1b') {
        exitTerminalMode()
        return
    }

    // Write directly to PTY
    invoke('write_to_pty', {
        data,
        projectPath: activeProject,
        terminalType: 'mini',
    }).catch((err) => {
        console.error('Failed to write key to Mini PTY:', err)
    })

    // Check buffer for command exits
    for (let i = 0; i < data.length; i++) {
        const char = data[i]
        if (char === '\r' || char === '\n') {
            const cmd = miniInputBuffer.trim()
            if (cmd === 'exit' || cmd === 'exit()') {
                exitTerminalMode()
            }
            miniInputBuffer = ''
        } else if (char === '\x7f' || char === '\x08') {
            miniInputBuffer = miniInputBuffer.slice(0, -1)
        } else {
            miniInputBuffer += char
        }
    }
})

miniTerm.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {
        e.preventDefault()
        invoke('write_to_pty', {
            data: '\x1b\x0d',
            projectPath: activeProject,
            terminalType: 'mini',
        }).catch(console.error)
        return false
    }
    return true
})

const exitTerminalMode = () => {
    isTerminalMode = false
    const currentProj = projects.find((p) => p.path === activeProject)
    if (currentProj) {
        currentProj.isTerminalMode = false
        saveProjects()
    }
    applyTerminalModeUI()
}

const resizePty = () => {
    fitAddon.fit()
    miniFitAddon.fit()
    invoke('resize_pty', {
        rows: term.rows,
        cols: term.cols,
        projectPath: activeProject,
        terminalType: 'engine',
    }).catch((err) => {
        console.error('Failed to resize Engine PTY:', err)
    })
    invoke('resize_pty', {
        rows: miniTerm.rows,
        cols: miniTerm.cols,
        projectPath: activeProject,
        terminalType: 'mini',
    }).catch((err) => {
        console.error('Failed to resize Mini PTY:', err)
    })
}

let resizePtyTimeout: any = null
const debouncedResizePty = () => {
    if (resizePtyTimeout) clearTimeout(resizePtyTimeout)
    resizePtyTimeout = setTimeout(() => {
        resizePty()
    }, 50)
}

const container = document.getElementById('terminal-container')
if (container) {
    term.open(container)
}

const miniContainer = document.getElementById('mini-terminal-container')
if (miniContainer) {
    miniTerm.open(miniContainer)
}

window.addEventListener('resize', () => {
    debouncedResizePty()
})

// ----------------------------------------------------
// 7. Output Modal & Virtual Terminal Parser
// ----------------------------------------------------
const markdownPreviewPane = document.getElementById('markdown-preview-pane')

// Parse transcript steps and render custom TUI log view in real time
interface Step {
    step_index: number
    source: string
    type: string
    status: string
    content?: string
    tool_calls?: Array<{
        name: string
        args?: Record<string, any>
    }>
}

interface ToolCallItem {
    name: string
    actionSummary: string
    icon: string
    targetPath?: string
}

interface RenderBlock {
    type: 'user_input' | 'planner_response' | 'tool_calls'
    content?: string
    calls?: ToolCallItem[]
    historicalContext?: string
    threadId?: string
}

const renderer = {
    code(token: any) {
        const text = token.text || '';
        const lang = token.lang || '';
        const escapedText = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        return `
            <div class="relative group my-4">
                <button class="absolute top-2 right-2 px-2 py-1 rounded bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 text-[10px] font-sans opacity-0 group-hover:opacity-100 transition-opacity z-10 border border-gray-300 dark:border-gray-700 cursor-pointer" data-content="${encodeURIComponent(text)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                <pre style="margin:0;"><code class="language-${lang}">${escapedText}</code></pre>
            </div>
        `;
    }
};
marked.use({ renderer });

const buildTimelineHtml = (steps: Step[]): string => {
    const blocks: RenderBlock[] = []
    let currentToolCalls: ToolCallItem[] = []

    const flushToolCalls = () => {
        if (currentToolCalls.length > 0) {
            blocks.push({ type: 'tool_calls', calls: [...currentToolCalls] })
            currentToolCalls = []
        }
    }

    steps.forEach((step) => {
        if (step.type === 'USER_INPUT' && step.content) {
            flushToolCalls()
            let prompt = step.content
            const startTag = '<USER_REQUEST>'
            const endTag = '</USER_REQUEST>'
            const startIdx = prompt.indexOf(startTag)
            const endIdx = prompt.indexOf(endTag)
            if (startIdx !== -1 && endIdx !== -1) {
                prompt = prompt
                    .substring(startIdx + startTag.length, endIdx)
                    .trim()
            }

            let historicalContextText = ''
            let threadId = ''

            if (prompt.includes('Continuing conversation from history')) {
                // Find thread ID if present
                const threadIdMatch = prompt.match(
                    /Thread ID:\s*([a-fA-F0-9-]+)/
                )
                if (threadIdMatch) {
                    threadId = threadIdMatch[1]
                }

                // Find historical context boundary
                const histIdx = prompt.indexOf('Historical Context:\n')
                const userReqIdx = prompt.indexOf('\n\nUser request: ')

                if (
                    histIdx !== -1 &&
                    userReqIdx !== -1 &&
                    userReqIdx > histIdx
                ) {
                    historicalContextText = prompt
                        .substring(
                            histIdx + 'Historical Context:\n'.length,
                            userReqIdx
                        )
                        .trim()
                    prompt = prompt
                        .substring(userReqIdx + '\n\nUser request: '.length)
                        .trim()
                } else {
                    const oldHistIdx = prompt.indexOf('Historical Context:\n')
                    const oldUserReqIdx = prompt.lastIndexOf('User request: ')
                    if (
                        oldHistIdx !== -1 &&
                        oldUserReqIdx !== -1 &&
                        oldUserReqIdx > oldHistIdx
                    ) {
                        historicalContextText = prompt
                            .substring(
                                oldHistIdx + 'Historical Context:\n'.length,
                                oldUserReqIdx
                            )
                            .trim()
                        prompt = prompt
                            .substring(oldUserReqIdx + 'User request: '.length)
                            .trim()
                    }
                }
            }

            blocks.push({
                type: 'user_input',
                content: prompt,
                historicalContext: historicalContextText || undefined,
                threadId: threadId || undefined,
            })
        } else {
            if (step.tool_calls && step.tool_calls.length > 0) {
                step.tool_calls.forEach((call) => {
                    let actionSummary = ''
                    if (
                        call.args &&
                        typeof call.args.toolSummary === 'string'
                    ) {
                        actionSummary = call.args.toolSummary
                    } else if (
                        call.args &&
                        typeof call.args.toolAction === 'string'
                    ) {
                        actionSummary = call.args.toolAction
                    }

                    if (
                        actionSummary.startsWith('"') &&
                        actionSummary.endsWith('"')
                    ) {
                        actionSummary = actionSummary.slice(1, -1)
                    }

                    if (!actionSummary) {
                        actionSummary = `Running tool ${call.name}`
                    }

                    let icon = '🛠️'
                    if (
                        call.name.includes('search') ||
                        call.name.includes('grep')
                    )
                        icon = '🔍'
                    else if (
                        call.name.includes('file') ||
                        call.name.includes('write') ||
                        call.name.includes('replace')
                    )
                        icon = '📝'
                    else if (
                        call.name.includes('command') ||
                        call.name.includes('run')
                    )
                        icon = '💻'
                    else if (
                        call.name.includes('dir') ||
                        call.name.includes('list')
                    )
                        icon = '📂'

                    let targetPath = ''
                    if (call.args) {
                        if (typeof call.args.TargetFile === 'string')
                            targetPath = call.args.TargetFile
                        else if (typeof call.args.AbsolutePath === 'string')
                            targetPath = call.args.AbsolutePath
                        else if (typeof call.args.DirectoryPath === 'string')
                            targetPath = call.args.DirectoryPath
                        else if (typeof call.args.SearchPath === 'string')
                            targetPath = call.args.SearchPath
                    }

                    currentToolCalls.push({
                        name: call.name,
                        actionSummary,
                        icon,
                        targetPath: targetPath || undefined,
                    })
                })
            }

            if (
                step.source === 'MODEL' &&
                step.type === 'PLANNER_RESPONSE' &&
                step.content
            ) {
                flushToolCalls()
                blocks.push({ type: 'planner_response', content: step.content })
            }
        }
    })
    flushToolCalls()

    let html = ''
    const renderToolCallHtml = (call: ToolCallItem) => {
        let pathHtml = ''
        if (call.targetPath) {
            const displayPath = formatPathForUser(call.targetPath)
            pathHtml = ` <a href="#" onclick="window.openPath('${call.targetPath.replace(/'/g, "\\'")}')" class="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 underline font-semibold ml-1" title="${formatPathForUser(call.targetPath)}">${displayPath}</a>`
        }
        return `
            <div class="w-full flex justify-start mb-2 select-none">
                <div class="pl-3 border-l-2 border-blue-500/40 dark:border-blue-500/50 text-[10px] text-gray-500 dark:text-gray-400 font-mono">
                    <span>${call.icon}</span>
                    <span class="font-bold text-gray-800 dark:text-gray-200">${call.actionSummary}</span>${pathHtml}
                </div>
            </div>
        `
    }

    blocks.forEach((block) => {
        if (block.type === 'user_input' && block.content) {
            if (block.historicalContext) {
                const escapedThreadId = block.threadId || ''
                html += `
                <div class="w-full flex justify-start mb-4 select-text">
                    <div class="w-full max-w-[65ch] bg-gray-50/90 dark:bg-gray-900/60 border border-gray-250/70 dark:border-gray-800/80 rounded-xl p-3 text-xs font-sans shadow-sm">
                        <details class="group">
                            <summary class="flex items-center justify-between cursor-pointer font-bold text-gray-500 dark:text-gray-400 select-none">
                                <span class="flex items-center gap-1.5">
                                    <span class="text-[14px]">📜</span>
                                    <span>Historical Context of active thread ${escapedThreadId ? `(${escapedThreadId.substring(0, 8)}...)` : ''}</span>
                                </span>
                                <span class="text-[9px] text-gray-400 dark:text-gray-500 font-mono transition-transform group-open:rotate-90">▶</span>
                            </summary>
                            <div class="mt-2.5 text-gray-600 dark:text-gray-300 font-mono whitespace-pre-wrap leading-relaxed max-h-[350px] overflow-y-auto pr-1 text-[11px] border-t border-gray-150 dark:border-gray-800/60 pt-2">
${block.historicalContext}
                            </div>
                        </details>
                    </div>
                </div>
                `
            }
            html += `
            <div class="w-full flex justify-end mb-4 select-text">
                <div class="group relative max-w-[65ch] bg-gray-150/80 dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-250 dark:border-gray-700/60 rounded-2xl px-4 text-sm font-sans whitespace-pre-wrap shadow-sm">
                    <button class="absolute -top-3 -right-2 px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity z-10 border border-gray-300 dark:border-gray-600 shadow-sm cursor-pointer" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    ${block.content}
                </div>
            </div>
            `
        } else if (block.type === 'planner_response' && block.content) {
            html += `
            <div class="w-full flex justify-start mb-4 select-text">
                <div class="group relative w-full prose dark:prose-invert prose-sm text-gray-800 dark:text-gray-300 prose-headings:text-gray-950 dark:prose-headings:text-white prose-pre:bg-gray-100 dark:prose-pre:bg-gray-950 prose-pre:border prose-pre:border-gray-250 dark:prose-pre:border-gray-900">
                    <button class="absolute -top-3 -left-2 px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 text-[10px] opacity-0 group-hover:opacity-100 transition-opacity z-10 border border-gray-300 dark:border-gray-600 shadow-sm cursor-pointer" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    ${marked.parse(block.content)}
                </div>
            </div>
            `
        } else if (block.type === 'tool_calls' && block.calls) {
            const calls = block.calls
            if (calls.length <= 2) {
                calls.forEach((call) => {
                    html += renderToolCallHtml(call)
                })
            } else {
                const collapsedCalls = calls.slice(0, -2)
                const visibleCalls = calls.slice(-2)

                html += `
                <details class="group mb-2 max-w-[65ch]">
                    <summary class="flex items-center gap-1.5 cursor-pointer text-[10px] font-mono text-blue-500/70 hover:text-blue-500 dark:text-blue-400/70 dark:hover:text-blue-400 select-none pb-1.5 pl-3 border-l-2 border-blue-500/20 dark:border-blue-500/20">
                        <span class="font-semibold text-gray-700 dark:text-gray-300">Show older steps (${collapsedCalls.length})</span>
                        <span class="text-[8px] text-gray-700 dark:text-gray-300 transition-transform group-open:rotate-90">▶</span>
                    </summary>
                    <div class="mt-1">
                        ${collapsedCalls.map(renderToolCallHtml).join('')}
                    </div>
                </details>
                `

                visibleCalls.forEach((call) => {
                    html += renderToolCallHtml(call)
                })
            }
        }
    })

    return html
}

let lastRenderedThreadLog = ''
let lastRenderedThreadId = ''

const renderCustomTuiLog = (jsonlContent: string) => {
    if (!markdownPreviewPane) return

    const lines = jsonlContent.trim().split('\n')
    const steps: Step[] = []
    const editedFilesSet = new Set<string>()

    for (const line of lines) {
        if (!line.trim()) continue
        try {
            const step: Step = JSON.parse(line)
            steps.push(step)

            // Collect edited files
            if (step.tool_calls) {
                for (const call of step.tool_calls) {
                    if (
                        call.name === 'replace_file_content' ||
                        call.name === 'multi_replace_file_content' ||
                        call.name === 'write_to_file'
                    ) {
                        if (
                            call.args &&
                            typeof call.args.TargetFile === 'string'
                        ) {
                            editedFilesSet.add(call.args.TargetFile)
                        }
                    }
                }
            }
        } catch {
            // Ignore
        }
    }

    if (steps.length === 0) {
        markdownPreviewPane.innerHTML =
            '<div class="text-gray-400 dark:text-gray-600 italic text-center mt-10">No conversation steps found.</div>'
        return
    }

    let html = ''

    // 1. Edited Files Header
    if (editedFilesSet.size > 0) {
        const files = Array.from(editedFilesSet)
        html += `
        <div class="mb-4 p-2 bg-blue-50/50 dark:bg-blue-950/20 rounded border border-blue-100 dark:border-blue-900/30 flex flex-wrap items-center gap-1.5 select-none max-w-[65ch]">
            <span class="text-[9px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">Edited Files:</span>
            ${files
                .map((file) => {
                    const parts = file.split('/')
                    const name = parts[parts.length - 1]
                    return `<span class="px-1.5 py-0.5 bg-blue-100/50 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 rounded text-[10px] font-mono border border-blue-200/50 dark:border-blue-800/60" title="${formatPathForUser(file)}">${name}</span>`
                })
                .join('')}
        </div>
        `
    }

    // 2. Timeline Steps
    html += buildTimelineHtml(steps)

    // 3. Thinking Indicator
    let isThinking = false
    if (steps.length > 0) {
        const lastStep = steps[steps.length - 1]
        if (lastStep.source === 'MODEL' && lastStep.status !== 'DONE') {
            isThinking = true
        }
    }

    if (!isThinking && pauseStatus === 'Running') {
        const lastStep = steps[steps.length - 1]
        if (
            lastStep &&
            (lastStep.type === 'USER_INPUT' ||
                (lastStep.tool_calls && lastStep.tool_calls.length > 0))
        ) {
            isThinking = true
        }
    }

    if (isThinking) {
        html += `
        <div class="w-full flex justify-start mb-4">
            <div class="flex items-center gap-2 p-2 bg-blue-500/5 dark:bg-blue-500/10 border border-blue-500/20 dark:border-blue-500/30 rounded animate-pulse select-none">
                <div class="relative flex h-3 w-3">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                </div>
                <span class="text-[10px] font-semibold text-blue-500 dark:text-blue-400 font-mono tracking-wider">Agent is thinking & working...</span>
            </div>
        </div>
        `
    }

    // Preserve state of <details> elements
    const openDetailsIndices: number[] = []
    const detailsElements = markdownPreviewPane.querySelectorAll('details')
    detailsElements.forEach((el, index) => {
        if (el.open) {
            openDetailsIndices.push(index)
        }
    })

    markdownPreviewPane.innerHTML = html

    // Restore state of <details> elements
    const newDetailsElements = markdownPreviewPane.querySelectorAll('details')
    openDetailsIndices.forEach((index) => {
        if (newDetailsElements[index]) {
            newDetailsElements[index].open = true
        }
    })

    // Auto-scroll the preview pane to bottom if it is currently generating
    if (isThinking) {
        setTimeout(() => {
            markdownPreviewPane.scrollTop = markdownPreviewPane.scrollHeight
        }, 30)
    }
}

// Poll the active thread's log file
setInterval(async () => {
    if (!activeThreadId) return
    const filepath = threadFilepaths.get(activeThreadId)
    if (!filepath) return

    try {
        const fileExists = await invoke<boolean>('file_exists', { filepath })
        if (fileExists) {
            const content = await invoke<string>('read_thread_log', {
                filepath,
            })
            if (
                content !== lastRenderedThreadLog ||
                activeThreadId !== lastRenderedThreadId
            ) {
                lastRenderedThreadLog = content
                lastRenderedThreadId = activeThreadId
                renderCustomTuiLog(content)
            }
        }
    } catch (e) {
        console.error('[AI-OS Thread Log Poll] Error:', e)
    }
}, 500)

const formatMarkdown = (text: string): string => {
    let formatted = text
    formatted = formatted.replace(/\*\*([^\*]+)\*\*/g, '\x1b[1m$1\x1b[22m')
    formatted = formatted.replace(/`([^`]+)`/g, '\x1b[36m$1\x1b[39m')
    return formatted
}

// Listen to Backend PTY events
listen<{ data: string; project_path: string; terminal_type: string }>(
    'pty-output',
    (event) => {
        let { data, project_path, terminal_type } = event.payload

        if (terminal_type === 'agy') {
            data = formatMarkdown(data)
        }

        // Choose correct buffer
        let buffers = miniTermBuffers
        if (terminal_type === 'claude') {
            buffers = claudeBuffers
        } else if (terminal_type === 'agy') {
            buffers = agyBuffers
        }

        // Append to cache buffer
        if (!buffers[project_path]) {
            buffers[project_path] = ''
        }
        buffers[project_path] += data
        if (buffers[project_path].length > 100000) {
            buffers[project_path] = buffers[project_path].substring(
                buffers[project_path].length - 50000
            )
        }

        if (project_path === activeProject) {
            if (terminal_type === 'mini') {
                miniTerm.write(data)
            } else if (terminal_type === currentEngine) {
                term.write(data)
            }
        }
    }
)

// TUI Toggle Button Event Listener
const toggleTuiBtn = document.getElementById('toggle-tui-btn')
const tuiContainer = document.getElementById('terminal-container')
const previewWrapper = document.getElementById('preview-wrapper')

if (toggleTuiBtn && tuiContainer && previewWrapper) {
    toggleTuiBtn.addEventListener('click', () => {
        isTuiExpanded = !isTuiExpanded
        if (isTuiExpanded) {
            // Expand
            tuiContainer.style.height = 'calc(100% - 28px)'
            previewWrapper.style.display = 'none'
            toggleTuiBtn.innerHTML = `
                <span>Collapse Terminal</span>
                <svg class="w-2.5 h-2.5 transform transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
            `
        } else {
            // Collapse
            tuiContainer.style.height = '110px'
            previewWrapper.style.display = 'flex'
            toggleTuiBtn.innerHTML = `
                <span>Expand Terminal</span>
                <svg class="w-2.5 h-2.5 transform transition-transform duration-300 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
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
}

// ----------------------------------------------------
// 4. Splitter Drag Resizing Panel (Legacy Splitter guards)
// ----------------------------------------------------
const splitter = document.getElementById('pane-splitter')
const panesContainer = document.getElementById('panes-container')

if (splitter && miniContainer && panesContainer) {
    let isDragging = false
    let startY = 0
    let startHeight = 0

    splitter.addEventListener('mousedown', (e) => {
        isDragging = true
        startY = e.clientY
        startHeight = miniContainer.offsetHeight
        document.body.style.cursor = 'row-resize'
        e.preventDefault()
    })

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return

        const deltaY = e.clientY - startY
        const newMiniHeight = startHeight - deltaY

        const containerRect = panesContainer.getBoundingClientRect()
        const minHeight = 50
        const maxHeight = containerRect.height * 0.8

        if (newMiniHeight >= minHeight && newMiniHeight <= maxHeight) {
            miniContainer.style.height = `${newMiniHeight}px`
            debouncedResizePty()
        }
    })

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false
            document.body.style.cursor = ''
            resizePty()
        }
    })
}

// 4a. Sidebar Width Resizing
const sidebarSplitter = document.getElementById('sidebar-splitter')
const sidebar = document.getElementById('projects-sidebar')

if (sidebarSplitter && sidebar) {
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
            debouncedResizePty()
        }
    })

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false
            document.body.style.cursor = ''
            resizePty()
        }
    })
}

// 4c. Main Panes Horizontal Resizing
const mainSplitter = document.getElementById('main-splitter')
const terminalsWrapper = document.getElementById('terminals-wrapper')

if (mainSplitter && terminalsWrapper && panesContainer) {
    let isDragging = false
    let startX = 0
    let startWidth = 0

    mainSplitter.addEventListener('mousedown', (e) => {
        isDragging = true
        startX = e.clientX
        startWidth = terminalsWrapper.offsetWidth
        document.body.style.cursor = 'col-resize'
        e.preventDefault()
    })

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return

        const deltaX = e.clientX - startX
        const newWidth = startWidth + deltaX

        const containerRect = panesContainer.getBoundingClientRect()
        const leftPercent = (newWidth / containerRect.width) * 100

        const minPercent = 15
        const maxPercent = 85

        if (leftPercent >= minPercent && leftPercent <= maxPercent) {
            terminalsWrapper.style.width = `${leftPercent}%`
            debouncedResizePty()
        }
    })

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false
            document.body.style.cursor = ''
            resizePty()
        }
    })
}

// ----------------------------------------------------
// 5. Dynamic Mode UI Application
// ----------------------------------------------------
const applyTerminalModeUI = () => {
    const bottomArea = document.getElementById('bottom-input-area')

    if (isTerminalMode) {
        if (splitter) splitter.style.display = 'block'
        if (miniContainer) miniContainer.style.display = 'block'
        if (bottomArea) bottomArea.style.display = 'none'
        setTimeout(() => {
            miniTerm.focus()
            resizePty()
        }, 50)
    } else {
        if (splitter) splitter.style.display = 'none'
        if (miniContainer) miniContainer.style.display = 'none'
        if (bottomArea) bottomArea.style.display = 'flex'
        setTimeout(() => {
            textarea?.focus()
            updatePlaceholder()
            resizePty()
        }, 50)
    }
}

// ----------------------------------------------------
// 6. UI Rendering: Sidebar & Project Swapper
// ----------------------------------------------------
const projectsListEl = document.getElementById('projects-list')
const currentDirPathEl = document.getElementById('current-dir-path')
const textarea = document.getElementById('prompt-input') as HTMLTextAreaElement

const renderProjects = () => {
    if (!projectsListEl) return
    projectsListEl.innerHTML = ''

    // Sort by recency
    const sorted = [...projects].sort((a, b) => b.lastActive - a.lastActive)

    sorted.forEach((project) => {
        const item = document.createElement('div')
        const isActive = project.path === activeProject

        item.className = `flex flex-col p-1 rounded transition-all border ${
            isActive
                ? 'bg-gray-100 dark:bg-gray-800/40 border-gray-200 dark:border-gray-700/80 shadow-sm'
                : 'bg-transparent border-transparent'
        }`

        const header = document.createElement('div')
        header.className = `flex items-center justify-between p-1.5 rounded cursor-pointer transition-all ${
            isActive
                ? 'text-gray-900 dark:text-white font-semibold bg-gray-200/70 dark:bg-gray-800 border border-gray-300 dark:border-gray-700'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-250 hover:bg-gray-200/50 dark:hover:bg-gray-900/50'
        }`

        header.innerHTML = `
            <div class="flex flex-col gap-0.5 truncate select-none min-w-0 flex-1">
                <div class="flex items-center gap-2 truncate">
                    <span class="w-2 rounded-full shrink-0 aspect-square" style="background-color: ${project.color}"></span>
                    <span class="truncate text-xs">${project.name}</span>
                </div>
                <span class="pl-4 truncate text-[9px] text-gray-400 dark:text-gray-500 font-mono">${formatPathForUser(project.path)}</span>
            </div>
            <div class="flex items-center action-btns opacity-0 transition-opacity ml-1.5 shrink-0">
                <button class="open-btn text-[10px] text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 px-1 py-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-all select-none" title="Open in Finder">📁</button>
                <button class="delete-btn text-[10px] text-gray-500 hover:text-red-600 dark:hover:text-red-400 px-1 py-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-all select-none" title="Remove Project">✕</button>
            </div>
        `

        // Swap project click
        header.addEventListener('click', (e) => {
            const target = e.target as HTMLElement

            // Delete project
            if (target.classList.contains('delete-btn')) {
                e.stopPropagation()
                projects = projects.filter((p) => p.path !== project.path)
                saveProjects()
                invoke('close_project_session', {
                    projectPath: project.path,
                }).catch((err) => {
                    console.error(
                        'Failed to close project session in Rust:',
                        err
                    )
                })
                // If deleted active, switch to first available
                if (activeProject === project.path && projects.length > 0) {
                    switchToProject(projects[0].path)
                } else {
                    renderProjects()
                }
                return
            }

            // Open in Finder
            if (
                target.classList.contains('open-btn') ||
                target.parentElement?.classList.contains('open-btn')
            ) {
                e.stopPropagation()
                invoke('open_path', { path: project.path }).catch(console.error)
                return
            }

            switchToProject(project.path)
        })

        // Show buttons on hover
        header.addEventListener('mouseenter', () => {
            const btns = header.querySelector('.action-btns') as HTMLElement
            if (btns) {
                btns.style.opacity = '1'
                const delBtn = btns.querySelector('.delete-btn') as HTMLElement
                if (
                    delBtn &&
                    project.path === '/Users/matthewmurphy/projects/ai-os'
                ) {
                    delBtn.style.display = 'none'
                }
            }
        })
        header.addEventListener('mouseleave', () => {
            const btns = header.querySelector('.action-btns') as HTMLElement
            if (btns) btns.style.opacity = '0'
        })

        item.appendChild(header)

        if (isActive) {
            const threadsContainer = document.createElement('div')
            threadsContainer.className =
                'mt-1.5 ml-0.5 pl-2.5 border-l border-gray-300 dark:border-gray-700/80 flex flex-col'

            const threadsHeader = document.createElement('div')
            threadsHeader.className =
                'flex items-center justify-between pr-1.5 text-[9px] font-semibold uppercase tracking-wider text-gray-500'
            threadsHeader.innerHTML = `
                <span>Threads</span>
                <button class="new-thread-btn text-[9px] font-bold text-gray-400 dark:text-gray-500 hover:text-gray-900 dark:hover:text-white px-1 py-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors" title="Start New Thread">+</button>
            `

            const threadsList = document.createElement('div')
            threadsList.id = 'project-threads-list'
            threadsList.className = 'max-h-96 overflow-y-auto pr-1'
            threadsList.innerHTML =
                '<div class="text-[9px] text-gray-500 italic p-1">Loading...</div>'

            threadsContainer.appendChild(threadsHeader)
            threadsContainer.appendChild(threadsList)
            item.appendChild(threadsContainer)

            // Attach event listener for the "+" button to start a new thread
            const newThreadBtn = threadsHeader.querySelector('.new-thread-btn')
            newThreadBtn?.addEventListener('click', async (e) => {
                e.stopPropagation()
                const existingPlaceholder = threadsList.querySelector('.new-thread-placeholder') as HTMLElement
                if (existingPlaceholder) {
                    existingPlaceholder.click()
                    const textarea = document.getElementById(
                        'prompt-entry-textarea'
                    ) as HTMLTextAreaElement | null
                    textarea?.focus()
                    return
                }

                activeThreadId = null
                activeThreadContext = null
                isWaitingForNewThread = true
                try {
                    const currentThreads = await invoke<ThreadLog[]>(
                        'get_project_threads',
                        { projectPath: activeProject }
                    )
                    waitingExistingThreadIds = new Set(
                        currentThreads.map((t) => t.id)
                    )
                } catch (err) {
                    console.error(
                        'Failed to get current threads on new thread click:',
                        err
                    )
                    waitingExistingThreadIds = new Set(
                        Array.from(threadFilepaths.keys())
                    )
                }
                updatePlaceholder(true)

                threadsList
                    .querySelectorAll(':scope > div')
                    .forEach((child) => {
                        child.className =
                            'group p-1.5 rounded border border-gray-200 dark:border-gray-855 bg-white dark:bg-gray-900/40 hover:bg-gray-100 dark:hover:bg-gray-850 cursor-pointer transition-all space-y-0.5'
                    })

                const loadingMsg = threadsList.querySelector('.italic')
                if (loadingMsg && loadingMsg.textContent?.includes('Loading')) {
                    loadingMsg.remove()
                }

                const placeholderEl = document.createElement('div')
                placeholderEl.className =
                    'group new-thread-placeholder p-1.5 rounded border border-blue-500/30 dark:border-blue-500/40 bg-blue-50/50 dark:bg-blue-500/10 cursor-pointer transition-all space-y-0.5'
                placeholderEl.innerHTML = `
                    <div class="flex items-center justify-between text-[9px] font-semibold text-gray-500 dark:text-gray-400">
                        <span class="truncate pr-1">#New Thread...</span>
                        <span class="shrink-0 text-[8px] text-gray-700 dark:text-gray-300 font-mono font-medium">Just now</span>
                    </div>
                    <div class="text-[10px] font-bold text-gray-900 dark:text-gray-100 truncate" title="New Thread">New Thread</div>
                    <div class="text-[9px] text-gray-600 dark:text-gray-400 line-clamp-1 leading-normal">Starting...</div>
                `
                threadsList.prepend(placeholderEl)

                placeholderEl.addEventListener('click', (e) => {
                    e.stopPropagation()
                    activeThreadId = null
                    isWaitingForNewThread = true
                    threadsList
                        .querySelectorAll(':scope > div')
                        .forEach((child) => {
                            child.className =
                                'group p-1.5 rounded border border-gray-200 dark:border-gray-855 bg-white dark:bg-gray-900/40 hover:bg-gray-100 dark:hover:bg-gray-850 cursor-pointer transition-all space-y-0.5'
                        })
                    placeholderEl.className =
                        'group new-thread-placeholder p-1.5 rounded border border-blue-500/30 dark:border-blue-500/40 bg-blue-50/50 dark:bg-blue-500/10 cursor-pointer transition-all space-y-0.5'

                    const previewPane = document.getElementById(
                        'markdown-preview-pane'
                    )
                    if (previewPane) {
                        previewPane.innerHTML =
                            '<div class="text-[10px] text-gray-500 dark:text-gray-600 italic text-center p-4">Select a thread or log file to view preview...</div>'
                    }
                })

                const previewPane = document.getElementById(
                    'markdown-preview-pane'
                )
                if (previewPane) {
                    previewPane.innerHTML =
                        '<div class="text-[10px] text-gray-500 dark:text-gray-600 italic text-center p-4">Select a thread or log file to view preview...</div>'
                }

                await selectAgyEngine()
                invoke('write_to_pty', {
                    data: '/clear\r',
                    projectPath: activeProject,
                    terminalType: 'agy',
                })
                textarea?.focus()
            })
        }

        projectsListEl.appendChild(item)
    })
}

// Switch active project workspace
const switchToProject = async (
    path: string,
    autoSelectFirstThread: boolean = false
) => {
    // Save draft and engine setting of the current project before switching
    const currentProj = projects.find((p) => p.path === activeProject)
    if (currentProj) {
        currentProj.promptDraft = textarea ? textarea.value : ''
        currentProj.engine = currentEngine
        currentProj.isTerminalMode = isTerminalMode
    }

    activeProject = path
    activeThreadId = null
    activeThreadContext = null
    isWaitingForNewThread = false
    waitingExistingThreadIds.clear()
    lastThreadsJson = ''

    // Update lastActive timestamp & restore state
    const nextProj = projects.find((p) => p.path === path)
    if (nextProj) {
        nextProj.lastActive = Date.now()
        if (textarea) {
            // Restore draft from localStorage first
            const savedDraft = localStorage.getItem(
                `ai-os-prompt-draft-${path}`
            )
            if (savedDraft !== null) {
                textarea.value = savedDraft
                adjustHeight()
            } else {
                textarea.value = nextProj.promptDraft || ''
                adjustHeight()
            }

            // Restore draft from physical disk asynchronously
            invoke<string>('load_prompt_draft', { projectPath: path })
                .then((diskDraft) => {
                    if (diskDraft && diskDraft !== textarea.value) {
                        textarea.value = diskDraft
                        adjustHeight()
                        localStorage.setItem(
                            `ai-os-prompt-draft-${path}`,
                            diskDraft
                        )
                    }
                })
                .catch(console.error)
        }
        if (nextProj.engine) {
            currentEngine = nextProj.engine
            const radio = document.querySelector(
                `input[name="engine"][value="${nextProj.engine}"]`
            ) as HTMLInputElement
            if (radio) {
                radio.checked = true
            }
        }
        isTerminalMode = !!nextProj.isTerminalMode
        applyTerminalModeUI()
        saveProjects()
    }

    // Clear terminal screens and dump cached history
    term.reset()
    const activeBuffers =
        currentEngine === 'claude' ? claudeBuffers : agyBuffers
    if (activeBuffers[path]) {
        term.write(activeBuffers[path])
    } else {
        term.write(
            `\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(path)}...\x1b[0m\r\n`
        )
    }

    miniTerm.reset()
    if (miniTermBuffers[path]) {
        miniTerm.write(miniTermBuffers[path])
    } else {
        miniTerm.write(
            `\r\n\x1b[1;32m[ai-os] Connecting to Shell session at: ${formatPathForUser(path)}...\x1b[0m\r\n`
        )
    }

    if (currentDirPathEl) {
        currentDirPathEl.textContent = formatPathForUser(path)
    }

    commandHistory = loadCommandHistory(path)
    historyIndex = -1
    currentDraft = ''

    // Reset pause state for the active project
    updatePauseUI('Running')

    // Request Rust backend to load/switch the project shell session
    try {
        await invoke<{ shell_pid: number; is_new_session: boolean }>(
            'switch_active_project',
            { projectPath: path, engine: currentEngine }
        )

        // PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
    } catch (e) {
        console.error('Failed to switch session in Rust:', e)
    }

    // Restore or initialize PTY geometry sync
    resizePty()
    renderProjects()
    renderProjectThreads(path, autoSelectFirstThread)
    adjustHeight()
}

interface ThreadLog {
    id: string
    latest_leaf_id: string
    title: string
    snippet: string
    filepath: string
    mtime: number
    detected_project_path?: string
}

const syncProjectsFromAllThreads = async () => {
    try {
        const allThreads = await invoke<ThreadLog[]>('get_all_agy_threads')
        let projectsModified = false

        for (const thread of allThreads) {
            let targetPath = thread.detected_project_path

            // If the thread is a lone agy thread without a detected project path
            if (!targetPath) {
                targetPath = `/Users/matthewmurphy/projects/Misc`
            }

            // Strip trailing markdown symbols
            while (targetPath.length > 0 && /[`*.,:;)}"\]]$/.test(targetPath)) {
                targetPath = targetPath.slice(0, -1)
            }

            // Check if a project with this path already exists
            const exists = projects.some((p) => p.path === targetPath)
            if (!exists) {
                // Determine a name for the new project
                let name = ''
                if (targetPath === '/Users/matthewmurphy/projects/Misc') {
                    name = 'Misc'
                } else if (thread.detected_project_path) {
                    name =
                        thread.detected_project_path.split('/').pop() ||
                        'Unnamed'
                } else {
                    name = thread.title || `Thread ${thread.id.substring(0, 8)}`
                }

                while (name.length > 0 && /[`*.,:;)}"\]]$/.test(name)) {
                    name = name.slice(0, -1)
                }

                projects.push({
                    path: targetPath,
                    name: name,
                    color: getRandomProjectColor(),
                    lastActive:
                        thread.mtime > 0 ? thread.mtime * 1000 : Date.now(),
                    engine: 'agy',
                    isTerminalMode: false,
                })
                projectsModified = true
            }
        }

        if (projectsModified) {
            // Sort projects by lastActive descending
            projects.sort((a, b) => b.lastActive - a.lastActive)
            saveProjects()
            renderProjects()
        }
    } catch (err) {
        console.error('Failed to sync projects from all threads:', err)
    }
}

const selectAgyEngine = async () => {
    if (currentEngine !== 'agy') {
        currentEngine = 'agy'
        const currentProj = projects.find((p) => p.path === activeProject)
        if (currentProj) {
            currentProj.engine = 'agy'
            saveProjects()
        }

        const agyRadio = document.querySelector(
            'input[name="engine"][value="agy"]'
        ) as HTMLInputElement
        if (agyRadio) agyRadio.checked = true

        term.reset()
        if (agyBuffers[activeProject]) {
            term.write(agyBuffers[activeProject])
        } else {
            term.write(
                `\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(activeProject)}...\x1b[0m\r\n`
            )
        }

        try {
            await invoke<{ shell_pid: number; is_new_session: boolean }>(
                'switch_active_project',
                {
                    projectPath: activeProject,
                    engine: 'agy',
                }
            )
        } catch (err) {
            console.error('Failed to toggle engine session on backend:', err)
        }
        resizePty()
    }
}

function getCompactifiedContext(jsonlContent: string): string {
    const lines = jsonlContent.trim().split('\n')
    const steps: string[] = []
    let stepCount = 0

    for (const line of lines) {
        if (!line.trim()) continue
        try {
            const step = JSON.parse(line)
            const source = step.source
            const type = step.type
            const content = step.content

            if (type === 'USER_INPUT' && content) {
                stepCount++
                let prompt = content
                const startTag = '<USER_REQUEST>'
                const endTag = '</USER_REQUEST>'
                const startIdx = prompt.indexOf(startTag)
                const endIdx = prompt.indexOf(endTag)
                if (startIdx !== -1 && endIdx !== -1) {
                    prompt = prompt
                        .substring(startIdx + startTag.length, endIdx)
                        .trim()
                }

                // Extract actual user request if combined with historical context
                const userRequestMarker = 'User request:'
                const markerIdx = prompt.lastIndexOf(userRequestMarker)
                if (markerIdx !== -1) {
                    prompt = prompt
                        .substring(markerIdx + userRequestMarker.length)
                        .trim()
                }

                prompt = prompt.trim()
                if (prompt.length > 2500) {
                    prompt = prompt.substring(0, 2500) + '\n... [truncated]'
                }

                steps.push(`- User Step ${stepCount}: "${prompt}"`)
            } else if (
                source === 'MODEL' &&
                type === 'PLANNER_RESPONSE' &&
                content
            ) {
                let reply = content.trim()
                if (reply.length > 2500) {
                    reply = reply.substring(0, 2500) + '\n... [truncated]'
                }

                steps.push(`- Assistant: "${reply}"`)
            }
        } catch (e) {
            // Ignore
        }
    }

    const maxSteps = 15
    const slicedSteps = steps.length > maxSteps ? steps.slice(-maxSteps) : steps
    return slicedSteps.join('\n') + '\n'
}

const renderProjectThreads = async (
    projectPath: string,
    autoSelectFirstThread: boolean = false,
    preFetchedThreads?: ThreadLog[]
) => {
    const listEl = document.getElementById('project-threads-list')
    if (!listEl) return

    try {
        const threads =
            preFetchedThreads ||
            (await invoke<ThreadLog[]>('get_project_threads', {
                projectPath,
            }))
        listEl.innerHTML = ''
        if (threads.length === 0) {
            listEl.innerHTML =
                '<div class="text-[9px] text-gray-500 dark:text-gray-600 italic text-center p-3">No threads found for this project</div>'
            return
        }

        threads.forEach((thread) => {
            threadFilepaths.set(thread.id, thread.filepath)
            threadLatestLeafIds.set(thread.id, thread.latest_leaf_id)
            const el = document.createElement('div')
            const isActive = activeThreadId === thread.id
            el.className = isActive
                ? 'group p-1.5 rounded border border-blue-500/30 dark:border-blue-500/40 bg-blue-50/50 dark:bg-blue-500/10 hover:bg-blue-100/50 dark:hover:bg-blue-500/20 cursor-pointer transition-all space-y-0.5'
                : 'group p-1.5 rounded border border-gray-200 dark:border-gray-855 bg-white dark:bg-gray-900/40 hover:bg-gray-100 dark:hover:bg-gray-850 cursor-pointer transition-all space-y-0.5'

            const dateStr =
                thread.mtime > 0
                    ? new Date(thread.mtime * 1000).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                      })
                    : 'Unknown Date'

            el.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1 min-w-0 pr-1">
                        <div class="flex items-center justify-between text-[9px] font-semibold text-gray-500 dark:text-gray-400">
                            <span class="truncate pr-1">#${thread.id.substring(0, 8)}</span>
                            <span class="shrink-0 text-[8px] text-gray-700 dark:text-gray-300 font-mono font-medium">${dateStr}</span>
                        </div>
                        <div class="text-[10px] font-bold text-gray-900 dark:text-gray-100 truncate" title="${thread.title}">${thread.title}</div>
                        <div class="text-[9px] text-gray-600 dark:text-gray-400 line-clamp-1 leading-normal" title="${thread.snippet}">${thread.snippet}</div>
                    </div>
                    <button class="delete-thread-btn opacity-0 group-hover:opacity-100 text-[10px] text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-all select-none self-center p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 shrink-0" title="Delete Thread">✕</button>
                </div>
            `



            const delBtn = el.querySelector('.delete-thread-btn')
            if (delBtn) {
                delBtn.addEventListener('click', async (e) => {
                    e.stopPropagation()
                    try {
                        await invoke('delete_thread', { id: thread.id })
                        if (activeThreadId === thread.id) {
                            activeThreadId = null
                            activeThreadContext = null
                            updatePlaceholder(true)
                            const previewPane = document.getElementById(
                                'markdown-preview-pane'
                            )
                            if (previewPane) {
                                previewPane.innerHTML =
                                    '<div class="text-[10px] text-gray-500 dark:text-gray-600 italic text-center p-4">Select a thread or log file to view preview...</div>'
                            }
                        }
                        pollThreadsList()
                    } catch (err) {
                        console.error('Failed to delete thread:', err)
                    }
                })
            }

            el.addEventListener('click', async () => {
                document
                    .querySelectorAll('#project-threads-list > div')
                    .forEach((child) => {
                        child.className =
                            'group p-1.5 rounded border border-gray-200 dark:border-gray-855 bg-white dark:bg-gray-900/40 hover:bg-gray-100 dark:hover:bg-gray-850 cursor-pointer transition-all space-y-0.5'
                    })
                el.className =
                    'group p-1.5 rounded border border-blue-500/30 dark:border-blue-500/40 bg-blue-50/50 dark:bg-blue-500/10 hover:bg-blue-100/50 dark:hover:bg-blue-500/20 cursor-pointer transition-all space-y-0.5'

                activeThreadId = thread.id
                await selectAgyEngine()

                const previewPane = document.getElementById(
                    'markdown-preview-pane'
                )
                try {
                    const content = await invoke<string>('read_thread_log', {
                        filepath: thread.filepath,
                    })
                    activeThreadContext = getCompactifiedContext(content)
                    updatePlaceholder(true)

                    if (previewPane) {
                        renderCustomTuiLog(content)
                    }
                } catch (err) {
                    if (previewPane) {
                        previewPane.innerHTML = `<div class="text-red-500 p-4">Error loading thread log file: ${err}</div>`
                    }
                }

                try {
                    const res = await invoke<{
                        shell_pid: number
                        is_new_session: boolean
                    }>('switch_active_project', {
                        projectPath: activeProject,
                        engine: 'agy',
                    })
                    if (res.is_new_session) {
                        await new Promise((resolve) => setTimeout(resolve, 800))
                    }
                } catch (err) {
                    console.error(
                        'Failed to toggle engine session on backend:',
                        err
                    )
                }
                invoke('write_to_pty', {
                    data: `/resume ${thread.latest_leaf_id}\r`,
                    projectPath: activeProject,
                    terminalType: 'agy',
                })
            })

            listEl.appendChild(el)
        })

        if (autoSelectFirstThread) {
            const firstChild = listEl.querySelector(
                ':scope > div'
            ) as HTMLElement
            if (firstChild) {
                firstChild.click()
            }
        }
    } catch (err) {
        console.error('Failed to load project threads:', err)
        listEl.innerHTML = `<div class="text-red-500 text-[10px] p-2">Error: ${err}</div>`
    }
}

const pollThreadsList = async () => {
    if (!activeProject) return
    try {
        const threads = await invoke<ThreadLog[]>('get_project_threads', {
            projectPath: activeProject,
        })
        const threadsJson = JSON.stringify(threads)

        // If we are waiting for a new thread to be created, and one is found
        if (isWaitingForNewThread && threads.length > 0) {
            const newestThread = threads[0]
            if (!waitingExistingThreadIds.has(newestThread.id)) {
                activeThreadId = newestThread.id
                isWaitingForNewThread = false
                waitingExistingThreadIds.clear()

                activeThreadContext = ''
                updatePlaceholder(true)

                lastThreadsJson = threadsJson
                await renderProjectThreads(activeProject, false, threads)

                const filepath = newestThread.filepath
                if (filepath) {
                    const content = await invoke<string>('read_thread_log', {
                        filepath,
                    })
                    activeThreadContext = getCompactifiedContext(content)
                    renderCustomTuiLog(content)
                }
                return
            }
        }

        if (threadsJson !== lastThreadsJson) {
            lastThreadsJson = threadsJson
            await renderProjectThreads(activeProject, false, threads)
        }
    } catch (err) {
        console.error('Failed in pollThreadsList:', err)
    }
}

// Start the polling interval
setInterval(pollThreadsList, 1000)

// Add project modal and logic
const addProjectModal = document.getElementById('add-project-modal')
const closeModalBtn = document.getElementById('close-modal-btn')
const btnChoiceExisting = document.getElementById('btn-choice-existing')
const btnChoiceNew = document.getElementById('btn-choice-new')
const newProjectForm = document.getElementById('new-project-form')
const newProjNameInput = document.getElementById(
    'new-proj-name'
) as HTMLInputElement
const newProjGitInput = document.getElementById(
    'new-proj-git'
) as HTMLInputElement
const btnSubmitNewProject = document.getElementById(
    'btn-submit-new-project'
) as HTMLButtonElement

const openModal = () => {
    if (!addProjectModal) return
    addProjectModal.classList.remove('hidden')
    // Force browser reflow to trigger CSS transitions
    addProjectModal.offsetHeight
    addProjectModal.classList.remove('opacity-0')
    addProjectModal.classList.add('opacity-100')

    const modalContent = addProjectModal.querySelector('.transform')
    if (modalContent) {
        modalContent.classList.remove('scale-95')
        modalContent.classList.add('scale-100')
    }

    // Reset modal state
    if (newProjectForm) newProjectForm.classList.add('hidden')
    if (newProjNameInput) newProjNameInput.value = ''
    if (newProjGitInput) newProjGitInput.value = ''
}

const closeModal = () => {
    if (!addProjectModal) return
    addProjectModal.classList.remove('opacity-100')
    addProjectModal.classList.add('opacity-0')

    const modalContent = addProjectModal.querySelector('.transform')
    if (modalContent) {
        modalContent.classList.remove('scale-100')
        modalContent.classList.add('scale-95')
    }

    // Hide modal element after transition completes
    setTimeout(() => {
        addProjectModal.classList.add('hidden')
    }, 300)
}

// Toggle modal visibility
const addProjectBtn = document.getElementById('add-project-btn')
addProjectBtn?.addEventListener('click', openModal)
closeModalBtn?.addEventListener('click', closeModal)

// Close modal when clicking on the backdrop (outside modal content)
addProjectModal?.addEventListener('click', (e) => {
    if (e.target === addProjectModal) {
        closeModal()
    }
})

// Helper to choose random color for project card
const getRandomProjectColor = () => {
    const colors = [
        '#3b82f6',
        '#ec4899',
        '#10b981',
        '#f59e0b',
        '#8b5cf6',
        '#ef4444',
        '#06b6d4',
        '#6366f1',
        '#14b8a6',
        '#a855f7',
    ]
    return colors[Math.floor(Math.random() * colors.length)]
}

// Open Existing Project via File Picker
btnChoiceExisting?.addEventListener('click', async () => {
    try {
        const selectedDir = await invoke<string | null>('select_directory')
        if (!selectedDir) return // User canceled the dialog

        const cleanPath = selectedDir.trim()
        const name = cleanPath.split('/').pop() || 'unknown-project'

        const existing = projects.find((p) => p.path === cleanPath)
        if (existing) {
            switchToProject(cleanPath)
            closeModal()
            return
        }

        const newProj: Project = {
            path: cleanPath,
            name,
            color: getRandomProjectColor(),
            lastActive: Date.now(),
            engine: 'agy',
            isTerminalMode: false,
        }

        projects.push(newProj)
        saveProjects()
        switchToProject(cleanPath)
        closeModal()
    } catch (err) {
        alert('Failed to select directory: ' + err)
    }
})

// Show New Project Form
btnChoiceNew?.addEventListener('click', () => {
    if (newProjectForm) {
        newProjectForm.classList.remove('hidden')
        newProjNameInput?.focus()
    }
})

// Auto-generate git repository name from project name
newProjNameInput?.addEventListener('input', () => {
    if (newProjGitInput) {
        // Convert to kebab-case
        const kebab = newProjNameInput.value
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '')
        newProjGitInput.value = kebab
    }
})

// Create & Initialize New Project
btnSubmitNewProject?.addEventListener('click', async () => {
    const name = newProjNameInput.value.trim()
    const gitRepoName = newProjGitInput.value.trim()

    if (!name) {
        alert('Please enter a project name.')
        return
    }
    if (!gitRepoName) {
        alert('Please enter a git repository name.')
        return
    }

    // Disable submit button and show loading state
    const originalText = btnSubmitNewProject.innerHTML
    btnSubmitNewProject.disabled = true
    btnSubmitNewProject.innerHTML = `<span class="inline-block animate-spin mr-2">🔄</span> Creating...`

    try {
        const projectPath = await invoke<string>('create_new_project', {
            name,
            gitRepoName,
        })

        const newProj: Project = {
            path: projectPath,
            name,
            color: getRandomProjectColor(),
            lastActive: Date.now(),
            engine: 'agy',
            isTerminalMode: false,
        }

        projects.push(newProj)
        saveProjects()
        switchToProject(projectPath)
        closeModal()
    } catch (err) {
        alert('Failed to create project: ' + err)
    } finally {
        btnSubmitNewProject.disabled = false
        btnSubmitNewProject.innerHTML = originalText
    }
})

// ----------------------------------------------------
// 7. Engine Toggle & Routing
// ----------------------------------------------------
let currentEngine: 'claude' | 'agy' = 'agy'
const engineRadios = document.querySelectorAll<HTMLInputElement>(
    'input[name="engine"]'
)

engineRadios.forEach((radio) => {
    radio.addEventListener('change', async (e) => {
        currentEngine = (e.target as HTMLInputElement).value as 'claude' | 'agy'
        // Persist setting on the active project
        const currentProj = projects.find((p) => p.path === activeProject)
        if (currentProj) {
            currentProj.engine = currentEngine
            saveProjects()
        }

        // Reset terminal screen and show matching engine buffer
        term.reset()
        const activeBuffers =
            currentEngine === 'claude' ? claudeBuffers : agyBuffers
        if (activeBuffers[activeProject]) {
            term.write(activeBuffers[activeProject])
        } else {
            term.write(
                `\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(activeProject)}...\x1b[0m\r\n`
            )
        }

        try {
            // Lazy spawn or switch to the engine on backend
            await invoke<{ shell_pid: number; is_new_session: boolean }>(
                'switch_active_project',
                {
                    projectPath: activeProject,
                    engine: currentEngine,
                }
            )

            // PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
        } catch (err) {
            console.error('Failed to toggle engine session on backend:', err)
        }

        resizePty()
    })
})

// ----------------------------------------------------
// 8. Input Interception & Routing
// ----------------------------------------------------
let lastTextareaHeight = 0
const adjustHeight = () => {
    if (textarea) {
        textarea.style.height = 'auto'
        const newHeight = textarea.scrollHeight
        textarea.style.height = newHeight + 'px'
        if (newHeight !== lastTextareaHeight) {
            lastTextareaHeight = newHeight
            debouncedResizePty()
        }
    }
}

textarea?.addEventListener('input', () => {
    savePromptDraft(textarea.value)
    // Instantly toggle to terminal mode when user types exactly "!" in empty field
    if (textarea.value === '!') {
        isTerminalMode = true
        const currentProj = projects.find((p) => p.path === activeProject)
        if (currentProj) {
            currentProj.isTerminalMode = true
            saveProjects()
        }
        applyTerminalModeUI()
        textarea.value = ''
        adjustHeight()
    } else {
        adjustHeight()

        // Expand terminal if typing a slash command
        const tuiContainer = document.getElementById('terminal-container')
        if (tuiContainer && !isTuiExpanded) {
            if (textarea.value.trim().startsWith('/')) {
                tuiContainer.style.height = '320px'
                debouncedResizePty()
            } else if (tuiContainer.style.height === '320px') {
                tuiContainer.style.height = '64px'
                debouncedResizePty()
            }
        }
    }
})
const loadCommandHistory = (projectPath: string): string[] => {
    try {
        const historyJson = localStorage.getItem(`ai-os-history-${projectPath}`)
        if (historyJson) {
            return JSON.parse(historyJson)
        }
    } catch (e) {
        console.error('Failed to load command history', e)
    }
    return []
}

const saveCommandHistory = (projectPath: string, history: string[]) => {
    try {
        localStorage.setItem(
            `ai-os-history-${projectPath}`,
            JSON.stringify(history)
        )
    } catch (e) {
        console.error('Failed to save command history', e)
    }
}

let commandHistory: string[] = loadCommandHistory(activeProject)
let historyIndex = -1
let currentDraft = ''

let arrowUpPressedOnce = false
let arrowUpTimeout: any = null
let arrowUpOverlay: HTMLDivElement | null = null

const showArrowUpOverlay = () => {
    if (!arrowUpOverlay) {
        arrowUpOverlay = document.createElement('div')
        arrowUpOverlay.className =
            'absolute top-0 left-0 right-0 bg-blue-600/90 text-white text-xs font-bold px-3 py-1.5 flex items-center justify-center rounded-t pointer-events-none z-10 animate-pulse transition-opacity'
        arrowUpOverlay.textContent = 'Press ArrowUp again to recall history'
        const bottomArea = document.getElementById('bottom-input-area')
        if (bottomArea) {
            bottomArea.appendChild(arrowUpOverlay)
        }
    }
    arrowUpOverlay.style.opacity = '1'
}

const hideArrowUpOverlay = () => {
    if (arrowUpOverlay) {
        arrowUpOverlay.style.opacity = '0'
        setTimeout(() => {
            if (arrowUpOverlay && arrowUpOverlay.style.opacity === '0') {
                arrowUpOverlay.remove()
                arrowUpOverlay = null
            }
        }, 300)
    }
}

textarea?.addEventListener('keydown', async (e) => {
    if (e.key === 'ArrowUp') {
        if (textarea.selectionStart === 0 || historyIndex !== -1) {
            // If the textarea is empty, we don't need the double tap
            const isEmpty = textarea.value.trim() === ''

            if (
                !isEmpty &&
                historyIndex === -1 &&
                !arrowUpPressedOnce &&
                commandHistory.length > 0
            ) {
                arrowUpPressedOnce = true
                showArrowUpOverlay()

                if (arrowUpTimeout) clearTimeout(arrowUpTimeout)
                arrowUpTimeout = setTimeout(() => {
                    arrowUpPressedOnce = false
                    hideArrowUpOverlay()
                }, 2000)

                const resetArrowUpState = () => {
                    arrowUpPressedOnce = false
                    hideArrowUpOverlay()
                    textarea.removeEventListener('input', resetArrowUpState)
                    textarea.removeEventListener('blur', resetArrowUpState)
                }
                textarea.addEventListener('input', resetArrowUpState)
                textarea.addEventListener('blur', resetArrowUpState)
                return
            }

            e.preventDefault()

            if (arrowUpTimeout) clearTimeout(arrowUpTimeout)
            arrowUpPressedOnce = false
            hideArrowUpOverlay()

            if (historyIndex === -1) {
                currentDraft = textarea.value
            }
            if (historyIndex < commandHistory.length - 1) {
                historyIndex++
                textarea.value =
                    commandHistory[commandHistory.length - 1 - historyIndex]
                adjustHeight()
            }
        }
    } else if (e.key === 'ArrowDown') {
        if (arrowUpTimeout) clearTimeout(arrowUpTimeout)
        arrowUpPressedOnce = false
        hideArrowUpOverlay()

        if (historyIndex !== -1) {
            e.preventDefault()
            if (historyIndex > 0) {
                historyIndex--
                textarea.value =
                    commandHistory[commandHistory.length - 1 - historyIndex]
                adjustHeight()
            } else if (historyIndex === 0) {
                historyIndex = -1
                textarea.value = currentDraft
                adjustHeight()
            }
        }
    } else if (e.key === 'Enter') {
        if (e.shiftKey) {
            // Shift+Enter: insert a newline at the cursor position explicitly
            e.preventDefault()
            const start = textarea.selectionStart
            const end = textarea.selectionEnd
            const value = textarea.value
            textarea.value =
                value.substring(0, start) + '\n' + value.substring(end)
            textarea.selectionStart = textarea.selectionEnd = start + 1
            adjustHeight()
            return
        }

        e.preventDefault()

        let rawInput = textarea.value
        const trimmedInput = rawInput.trim()
        if (!trimmedInput) return

        if (!activeThreadId) {
            isWaitingForNewThread = true
            try {
                const currentThreads = await invoke<ThreadLog[]>(
                    'get_project_threads',
                    { projectPath: activeProject }
                )
                waitingExistingThreadIds = new Set(
                    currentThreads.map((t) => t.id)
                )
            } catch (err) {
                console.error(
                    'Failed to get current threads on Enter press:',
                    err
                )
                waitingExistingThreadIds = new Set(
                    Array.from(threadFilepaths.keys())
                )
            }
        }

        commandHistory.push(trimmedInput)
        saveCommandHistory(activeProject, commandHistory)
        historyIndex = -1

        const previewPane = document.getElementById('markdown-preview-pane')
        if (previewPane) {
            if (previewPane.innerHTML.includes('Select a thread')) {
                previewPane.innerHTML = ''
            }
            const escapedInput = trimmedInput
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
            const blockHtml = `
            <div class="w-full flex justify-end mb-4 select-text">
                <div class="max-w-[65ch] bg-gray-150/80 dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-250 dark:border-gray-700/60 rounded-2xl px-4 py-2.5 text-sm font-sans whitespace-pre-wrap shadow-sm">
${escapedInput}
                </div>
            </div>`
            previewPane.innerHTML += blockHtml
            setTimeout(() => {
                previewPane.scrollTop = previewPane.scrollHeight
            }, 10)
        }

        // Prompt Mode Engine Routing Logic
        let processedInput = trimmedInput

        // Obsidian Knowledge Routing
        if (processedInput.toLowerCase().includes('notes')) {
            processedInput += `\n\n[SYSTEM DIRECTIVE: Any read/write operations regarding "notes" MUST exclusively target this absolute path: /Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/]`
        }

        let isRunning = false
        try {
            isRunning = await invoke<boolean>('is_engine_running', {
                engine: currentEngine,
                projectPath: activeProject,
            })
        } catch (err) {
            console.error('Failed to check if engine is running:', err)
        }

        const clearCheckbox = document.getElementById(
            'clear-context-checkbox'
        ) as HTMLInputElement
        const shouldClear = clearCheckbox ? clearCheckbox.checked : true
        const isBypass = e.metaKey || e.ctrlKey || e.altKey || !shouldClear

        // Load the latest context dynamically from the thread's log file if inside a thread
        let currentContext = activeThreadContext
        if (activeThreadId && currentEngine === 'agy') {
            const filepath = threadFilepaths.get(activeThreadId)
            if (filepath) {
                try {
                    const content = await invoke<string>('read_thread_log', {
                        filepath,
                    })
                    currentContext = getCompactifiedContext(content)
                } catch (err) {
                    console.error('Failed to load active thread context:', err)
                }
            }
        }

        if (isRunning) {
            if (activeThreadId && currentContext && !isBypass) {
                invoke('write_to_pty', {
                    data: '/clear\r',
                    projectPath: activeProject,
                    terminalType: currentEngine,
                })
                await new Promise((resolve) => setTimeout(resolve, 450))

                const combinedPrompt = `Continuing conversation from history (Thread ID: ${activeThreadId}).\n\n[SYSTEM DIRECTIVE: This is a summary/compacted view of the thread history. If you need to view the full, untruncated details, tool calls, or files from this thread, you can run the following command in the terminal:\n  pnpm run view-thread ${activeThreadId}\nor specifically for a step:\n  pnpm run view-thread ${activeThreadId} --step <index>\n]\n\nHistorical Context:\n${currentContext}\n\nUser request: ${processedInput}`
                const dataToSend = `\x1b[200~${combinedPrompt}\x1b[201~\r`
                invoke('write_to_pty', {
                    data: dataToSend,
                    projectPath: activeProject,
                    terminalType: currentEngine,
                })
            } else {
                const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`
                if (isBypass) {
                    invoke('write_to_pty', {
                        data: dataToSend,
                        projectPath: activeProject,
                        terminalType: currentEngine,
                    })
                } else {
                    invoke('write_to_pty', {
                        data: '/clear\r',
                        projectPath: activeProject,
                        terminalType: currentEngine,
                    })
                    await new Promise((resolve) => setTimeout(resolve, 450))
                    invoke('write_to_pty', {
                        data: dataToSend,
                        projectPath: activeProject,
                        terminalType: currentEngine,
                    })
                }
            }
        } else {
            if (currentEngine === 'agy') {
                try {
                    await invoke('switch_active_project', {
                        projectPath: activeProject,
                        engine: 'agy',
                    })
                    await invoke('spawn_fresh_engine', {
                        projectPath: activeProject,
                        engine: 'agy',
                    })
                    await new Promise((resolve) => setTimeout(resolve, 1000))
                } catch (err) {
                    console.error('Failed to spawn fresh agy engine:', err)
                }

                if (activeThreadId && currentContext) {
                    const leafId = threadLatestLeafIds.get(activeThreadId) || activeThreadId
                    invoke('write_to_pty', {
                        data: `/resume ${leafId}\r`,
                        projectPath: activeProject,
                        terminalType: 'agy',
                    })
                    await new Promise((resolve) => setTimeout(resolve, 800))

                    invoke('write_to_pty', {
                        data: '/clear\r',
                        projectPath: activeProject,
                        terminalType: 'agy',
                    })
                    await new Promise((resolve) => setTimeout(resolve, 450))

                    const combinedPrompt = `Continuing conversation from history (Thread ID: ${activeThreadId}).\n\n[SYSTEM DIRECTIVE: This is a summary/compacted view of the thread history. If you need to view the full, untruncated details, tool calls, or files from this thread, you can run the following command in the terminal:\n  pnpm run view-thread ${activeThreadId}\nor specifically for a step:\n  pnpm run view-thread ${activeThreadId} --step <index>\n]\n\nHistorical Context:\n${currentContext}\n\nUser request: ${processedInput}`
                    const dataToSend = `\x1b[200~${combinedPrompt}\x1b[201~\r`
                    invoke('write_to_pty', {
                        data: dataToSend,
                        projectPath: activeProject,
                        terminalType: 'agy',
                    })
                } else {
                    const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`
                    invoke('write_to_pty', {
                        data: dataToSend,
                        projectPath: activeProject,
                        terminalType: 'agy',
                    })
                }
            } else {
                const escapedInput = processedInput.replace(/"/g, '\\"')
                let commandToExecute = ''

                if (currentEngine === 'claude') {
                    commandToExecute = `claude -p "${escapedInput}"`
                }

                invoke('write_to_pty', {
                    data: commandToExecute + '\r',
                    projectPath: activeProject,
                    terminalType: currentEngine,
                })
            }
        }

        textarea.value = ''
        savePromptDraft('')
        adjustHeight()

        // Auto-clear context toggle turns itself back on after each message is sent
        if (clearCheckbox) {
            clearCheckbox.checked = true
            autoClearContext = true
            localStorage.setItem('ai-os-auto-clear', 'true')
            // We poll is_engine_running in the background, but we can optimistically call updatePlaceholder(true) since we just spawned/used it
            updatePlaceholder(true)
        }
    }
})

// Tauri File Drop handling
listen<string[]>('tauri://file-drop', (event) => {
    if (!textarea) return
    const paths = event.payload
    if (paths && paths.length > 0) {
        const textToAppend = paths.join(' ')
        if (textarea.value) {
            textarea.value += ' ' + textToAppend
        } else {
            textarea.value = textToAppend
        }
        adjustHeight()
    }
})

// ----------------------------------------------------
// 8. Clipboard Copy & Paste for TUI (xterm.js)
// ----------------------------------------------------
document.addEventListener('keydown', (e) => {
    // Intercept Cmd+C (Mac) or Ctrl+C to copy selected text from xterm.js or window
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'c') {
        let textToCopy = ''
        const activeEl = document.activeElement

        // Only prioritize xterm.js selections if the terminal elements are focused
        if (
            activeEl &&
            (container?.contains(activeEl) || term.element?.contains(activeEl))
        ) {
            if (term.hasSelection()) {
                textToCopy = term.getSelection()
            } else {
                invoke('copy_tmux_selection', {
                    projectPath: activeProject,
                    terminalType: currentEngine,
                }).catch((err) => {
                    console.error('Failed to copy tmux selection:', err)
                })
            }
        } else if (
            activeEl &&
            (miniContainer?.contains(activeEl) ||
                miniTerm.element?.contains(activeEl))
        ) {
            if (miniTerm.hasSelection()) {
                textToCopy = miniTerm.getSelection()
            } else {
                invoke('copy_tmux_selection', {
                    projectPath: activeProject,
                    terminalType: 'mini',
                }).catch((err) => {
                    console.error('Failed to copy tmux selection:', err)
                })
            }
        } else {
            textToCopy = window.getSelection()?.toString() || ''
        }

        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy).catch((err) => {
                console.error('Failed to copy text:', err)
            })
        }
    }
})

document.addEventListener('paste', async (e) => {
    // If user is focused on the prompt input, let default paste happen
    if (document.activeElement === textarea) {
        return
    }
    let pastedText = e.clipboardData?.getData('text')
    if (pastedText) {
        const activeEl = document.activeElement
        const isEngineFocus =
            activeEl &&
            (container?.contains(activeEl) || term.element?.contains(activeEl))

        if (isEngineFocus) {
            let isRunning = false
            try {
                isRunning = await invoke<boolean>('is_engine_running', {
                    engine: currentEngine,
                    projectPath: activeProject,
                })
            } catch (err) {
                console.error('Failed to check if engine is running:', err)
            }
            if (isRunning) {
                // When pasting directly into an active interactive session, map newlines to Esc+LF (\x1b\n)
                // so the interactive shell buffers the entire pasted block without submitting line-by-line
                pastedText = pastedText
                    .replace(/\r\n/g, '\n')
                    .replace(/\n/g, '\x1b\n')
            }
            invoke('write_to_pty', {
                data: pastedText,
                projectPath: activeProject,
                terminalType: currentEngine,
            })
        } else if (
            activeEl &&
            (miniContainer?.contains(activeEl) ||
                miniTerm.element?.contains(activeEl))
        ) {
            // For raw terminals/shells, use bracketed paste sequences if multiline to prevent premature executes
            if (pastedText.includes('\n')) {
                invoke('write_to_pty', {
                    data: '\x1b[200~' + pastedText + '\x1b[201~',
                    projectPath: activeProject,
                    terminalType: 'mini',
                })
            } else {
                invoke('write_to_pty', {
                    data: pastedText,
                    projectPath: activeProject,
                    terminalType: 'mini',
                })
            }
        }
    }
})

// ----------------------------------------------------
// 9. Focus Management & Initialization
// ----------------------------------------------------
textarea?.focus()

// Auto-clear context checkbox handling
const clearCheckbox = document.getElementById(
    'clear-context-checkbox'
) as HTMLInputElement
let autoClearContext = true
const savedAutoClear = localStorage.getItem('ai-os-auto-clear')
if (savedAutoClear !== null) {
    autoClearContext = savedAutoClear === 'true'
}

const updatePlaceholder = (isRunning = true) => {
    const contextContainer = document.getElementById('clear-context-container')
    const labelText = document.getElementById('clear-context-label-text')
    if (textarea) {
        if (!isRunning) {
            textarea.placeholder = `Type a prompt... [Will launch ${currentEngine} and send] (Enter to send, Shift+Enter for newline)`
            if (contextContainer) {
                contextContainer.style.display = 'none'
            }
        } else {
            if (contextContainer) {
                contextContainer.style.display = 'flex'
            }
            if (clearCheckbox && clearCheckbox.checked) {
                textarea.placeholder =
                    'Type a prompt... [Runs /clear first] (Enter to send, Shift+Enter for newline)'
                if (contextContainer) {
                    contextContainer.className =
                        'flex items-center cursor-pointer select-none text-xs font-bold px-2 py-0.5 rounded border transition-all bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                }
                if (labelText) labelText.textContent = 'Auto-Clear: ACTIVE'
            } else {
                textarea.placeholder =
                    'Type a prompt... [Continuing thread] (Enter to send, Shift+Enter for newline)'
                if (contextContainer) {
                    contextContainer.className =
                        'flex items-center cursor-pointer select-none text-xs font-medium px-2 py-0.5 rounded border transition-all bg-gray-900/40 border-gray-800 text-gray-500 hover:text-gray-400'
                }
                if (labelText) labelText.textContent = 'Auto-Clear: OFF'
            }
        }
    }
}

if (clearCheckbox) {
    clearCheckbox.checked = autoClearContext
    clearCheckbox.addEventListener('change', () => {
        autoClearContext = clearCheckbox.checked
        localStorage.setItem('ai-os-auto-clear', String(autoClearContext))
        updatePlaceholder()
    })
    // Call initially
    setTimeout(updatePlaceholder, 100)
}

document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    const selection = window.getSelection()

    // Focus appropriate terminal or textarea
    const isEngineTermClick = container?.contains(target)
    const isMiniTermClick = miniContainer?.contains(target)
    const isSidebarClick = document
        .getElementById('projects-sidebar')
        ?.contains(target)

    if (isEngineTermClick) {
        term.focus()
    } else if (isMiniTermClick) {
        miniTerm.focus()
    } else if (
        !isSidebarClick &&
        target.tagName !== 'INPUT' &&
        target.tagName !== 'TEXTAREA' &&
        (!selection || selection.toString() === '')
    ) {
        if (isTerminalMode) {
            miniTerm.focus()
        } else {
            textarea?.focus()
            updatePlaceholder()
        }
    }
})

// Initialize workspace session
;(async () => {
    await syncProjectsFromAllThreads()
    try {
        const initialProject = await invoke<string | null>(
            'get_initial_project'
        )
        if (initialProject) {
            const cleanPath = initialProject.trim()
            const existing = projects.find((p) => p.path === cleanPath)
            if (existing) {
                activeProject = cleanPath
            } else {
                const name = cleanPath.split('/').pop() || 'unknown-project'
                const newProj: Project = {
                    path: cleanPath,
                    name,
                    color: getRandomProjectColor(),
                    lastActive: Date.now(),
                    engine: 'agy',
                    isTerminalMode: false,
                }
                projects.push(newProj)
                saveProjects()
                activeProject = cleanPath
            }
        } else {
            // Sort by recency to get the most recent active project on startup
            const sorted = [...projects].sort(
                (a, b) => b.lastActive - a.lastActive
            )
            if (sorted.length > 0) {
                activeProject = sorted[0].path
            }
        }
    } catch (e) {
        console.error('Failed to get initial project:', e)
        const sorted = [...projects].sort((a, b) => b.lastActive - a.lastActive)
        if (sorted.length > 0) {
            activeProject = sorted[0].path
        }
    }
    await switchToProject(activeProject, true)
})()

// Periodically sync projects from threads
setInterval(syncProjectsFromAllThreads, 10000)

// Poll engine running state
setInterval(async () => {
    if (!activeProject || isTerminalMode) return
    try {
        const isRunning = await invoke<boolean>('is_engine_running', {
            engine: currentEngine,
            projectPath: activeProject,
        })
        // Only update if we aren't showing the arrow up overlay (so we don't mess up placeholder)
        if (!arrowUpPressedOnce) {
            updatePlaceholder(isRunning)
        }
    } catch (e) {
        console.error(e)
    }
}, 1000)

// Poll Quota
async function updateQuotaDisplay() {
    try {
        const quotaJson = await invoke<string>('get_quota')
        const data = JSON.parse(quotaJson)

        let googlePct = '0%'
        let anthropicPct = '0%'

        const googleModels = data.Models.filter(
            (m: any) =>
                m.Provider === 'MODEL_PROVIDER_GOOGLE' &&
                !m.ResetTime.startsWith('0001')
        )
        const anthropicModels = data.Models.filter(
            (m: any) =>
                m.Provider === 'MODEL_PROVIDER_ANTHROPIC' &&
                !m.ResetTime.startsWith('0001')
        )

        if (googleModels.length > 0) {
            const minRem = Math.min(
                ...googleModels.map((m: any) => m.RemainingFraction)
            )
            googlePct = (minRem * 100).toFixed(0) + '%'
        }

        if (anthropicModels.length > 0) {
            const minRem = Math.min(
                ...anthropicModels.map((m: any) => m.RemainingFraction)
            )
            anthropicPct = (minRem * 100).toFixed(0) + '%'
        }

        const display = document.getElementById('quota-display')
        if (display) {
            display.innerText = `QUOTAS | Google: ${googlePct}, Anthropic: ${anthropicPct}`
            display.classList.remove('hidden')
        }

        const tooltip = document.getElementById('quota-tooltip')
        if (tooltip) {
            tooltip.innerHTML =
                '<div class="flex gap-8"><div id="quota-col-google" class="flex flex-col gap-2"></div><div id="quota-col-anthropic" class="flex flex-col gap-2"></div></div>'

            const getProviderData = (
                name: string,
                pName: string,
                colId: string
            ) => {
                const allModels = data.Models.filter(
                    (m: any) =>
                        m.Provider === pName && !m.ResetTime.startsWith('0001')
                )
                const col = document.getElementById(colId)
                if (!col) return

                col.innerHTML += `<div class="font-bold text-gray-200 mb-1 border-b border-gray-700 pb-1">${name}</div>`

                const highModels = allModels.filter(
                    (m: any) =>
                        !(
                            m.ModelID.includes('-low') ||
                            (m.DisplayName && m.DisplayName.includes('(Low)'))
                        )
                )
                const lowModels = allModels.filter(
                    (m: any) =>
                        m.ModelID.includes('-low') ||
                        (m.DisplayName && m.DisplayName.includes('(Low)'))
                )

                const renderBucket = (label: string, models: any[]) => {
                    if (models.length === 0) return
                    const minRem = Math.min(
                        ...models.map((m: any) => m.RemainingFraction)
                    )
                    const pct = (minRem * 100).toFixed(0) + '%'

                    const rt = models[0].ResetTime
                    const d = new Date(rt as string)

                    const diffMs = d.getTime() - Date.now()
                    let timeStr = 'Now'
                    if (diffMs > 0) {
                        const h = Math.floor(diffMs / 3600000)
                        const m = Math.floor((diffMs % 3600000) / 60000)
                        let localT = d
                            .toLocaleTimeString([], {
                                hour: 'numeric',
                                minute: '2-digit',
                            })
                            .toLowerCase()
                        localT = localT
                            .replace(/\s+/g, '')
                            .replace('am', 'a')
                            .replace('pm', 'p')
                        timeStr = `in ${h}h ${m}m (${localT})`
                    }

                    const row = document.createElement('div')
                    row.className =
                        'flex justify-between items-center gap-4 font-mono text-[11px] whitespace-nowrap'
                    row.innerHTML = `<span class="font-bold text-gray-400 w-12">${label}:</span> <div class="flex gap-2 text-right"> <span class="${minRem < 0.2 ? 'text-red-400' : 'text-green-400'} font-bold w-9">${pct}</span> <span class="text-gray-500">resets ${timeStr}</span></div>`
                    col.appendChild(row)
                }

                renderBucket('5-hr', highModels)
                renderBucket('Weekly', lowModels)
            }

            getProviderData(
                'Google',
                'MODEL_PROVIDER_GOOGLE',
                'quota-col-google'
            )
            getProviderData(
                'Anthropic',
                'MODEL_PROVIDER_ANTHROPIC',
                'quota-col-anthropic'
            )

            tooltip.classList.remove('hidden')
        }
    } catch (e) {
        console.error('Failed to update quota:', e)
    }
}

updateQuotaDisplay()
setInterval(updateQuotaDisplay, 60000)
