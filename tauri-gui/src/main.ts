import "@xterm/xterm/css/xterm.css"
import "overlayscrollbars/overlayscrollbars.css"
import "./styles.scss"
import { OverlayScrollbars } from "overlayscrollbars"

function getScrollEl(element: HTMLElement | null): HTMLElement | null {
	if (!element) return null;
	const osInstance = OverlayScrollbars(element);
	return osInstance ? osInstance.elements().viewport : element;
}

function getContentEl(element: HTMLElement | null): HTMLElement | null {
	if (!element) return null;
	const osInstance = OverlayScrollbars(element);
	return osInstance ? osInstance.elements().content : element;
}

function initOS(element: HTMLElement | null): any {
	if (!element) return null;
	return OverlayScrollbars(element, {
		scrollbars: {
			autoHide: "scroll",
			autoHideDelay: 800,
			theme: "os-theme-macos"
		}
	});
}


import type { ILink, ILinkProvider } from "@xterm/xterm"
import {
	PhysicalPosition,
	PhysicalSize,
	appWindow,
	invoke,
	listen,
	open,
} from "./tauriWrapper"
import { getFullDateStr, getRelativeDateStr } from "./dateUtils"

import { Autocompleter } from "./autocomplete"
import { FitAddon } from "@xterm/addon-fit"
import { Terminal } from "@xterm/xterm"
import { WebLinksAddon } from "@xterm/addon-web-links"
import { marked } from "marked"
import { renderThreadNotesSidebar } from "./threadNotes"
import { HermesChatClient } from "./hermesChat"

window.addEventListener("keydown", (e) => {
	if (e.metaKey && e.altKey && e.key.toLowerCase() === "i") {
		invoke("open_devtools").catch(console.error)
	}
	if (e.metaKey && e.key.toLowerCase() === "n") {
		e.preventDefault()
		const newThreadBtn = document.querySelector(
			".new-thread-btn",
		) as HTMLButtonElement | null
		if (newThreadBtn) {
			newThreadBtn.click()
		}
	}

	// Map cmd/alt+1, 2, and 3 to terminal preset sizes
	if ((e.metaKey || e.altKey) && !e.ctrlKey) {
		if (e.code === "Digit1") {
			if (e.altKey) e.preventDefault() //? otherwise will insert a special character into text input
			applyTerminalPreset(0)
		} else if (e.code === "Digit2") {
			if (e.altKey) e.preventDefault() //? otherwise will insert a special character into text input
			applyTerminalPreset(1)
		} else if (e.code === "Digit3") {
			if (e.altKey) e.preventDefault() //? otherwise will insert a special character into text input
			applyTerminalPreset(2)
		}
	}

	// Keyboard shortcuts for refreshing/redrawing terminal
	if ((e.metaKey && e.shiftKey && e.key.toLowerCase() === "r") ||
		(e.metaKey && e.altKey && e.key.toLowerCase() === "r")) {
		e.preventDefault()
		try {
			(window as any).refreshActiveTerminal()
		} catch (err) {}
	}
})

// ----------------------------------------------------
// 1. Interfaces & Types
// ----------------------------------------------------
async function restoreWindowState() {
	try {
		const sizeStr = localStorage.getItem("windowSize")
		if (sizeStr) {
			const { width, height } = JSON.parse(sizeStr)
			await appWindow.setSize(new PhysicalSize(width, height))
		}
		const posStr = localStorage.getItem("windowPosition")
		if (posStr) {
			const { x, y } = JSON.parse(posStr)
			await appWindow.setPosition(new PhysicalPosition(x, y))
		}
	} catch (e) {
		console.error("Failed to restore window state:", e)
	}

	appWindow.onResized(async ({ payload: size }: { payload: any }) => {
		localStorage.setItem(
			"windowSize",
			JSON.stringify({ width: size.width, height: size.height }),
		)
	})
	appWindow.onMoved(async ({ payload: position }: { payload: any }) => {
		localStorage.setItem(
			"windowPosition",
			JSON.stringify({ x: position.x, y: position.y }),
		)
	})
}
restoreWindowState()

interface Project {
	path: string
	name: string
	color: string
	lastActive: number // timestamp
	engine: "claude" | "agy" | "hermes"
	promptDraft?: string
	isTerminalMode?: boolean
}

// ----------------------------------------------------
// 2. Global State Management
// ----------------------------------------------------
let activeProject: string = "/Users/matt/projects/ai-os"
let maxVisibleThreads: number = 15

const cleanPath = (path: string): string => {
	if (!path) return ""
	return path.replace(/^["'“‘]+|["'”’]+$/g, "").trim()
}

const formatPathForUser = (
	path: string,
	projectPath: string = activeProject,
): string => {
	if (!path) return ""
	const projectPrefix =
		projectPath.endsWith("/") ? projectPath : projectPath + "/"
	if (path.startsWith(projectPrefix)) {
		return path.substring(projectPrefix.length)
	}
	return path.replace("/Users/matt", "~")
}

let isTerminalMode: boolean = false

let activeThreadId: string | null = null
setInterval(() => {
	;(window as any).activeThreadId = activeThreadId
}, 50)
let activeThreadContext: string | null = null
const threadFilepaths = new Map<string, string>()
const threadLatestLeafIds = new Map<string, string>()
let lastThreadsJson = ""
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
		content.endsWith(" ") || content.endsWith("\n") || content.endsWith("\t")

	if (saveDraftTimeout) {
		clearTimeout(saveDraftTimeout)
	}

	const writeToDisk = () => {
		invoke("save_prompt_draft", {
			projectPath: activeProject,
			content,
		}).catch((err) =>
			console.error("Failed to save prompt draft to disk:", err),
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
const hermesBuffers: Record<string, string> = {}
const miniTermBuffers: Record<string, string> = {}

let pauseStatus: "Running" | "Pending" | "Paused" = "Running"
const pauseBtnEl = document.getElementById("pause-btn")

const updatePauseUI = (status: "Running" | "Pending" | "Paused") => {
	pauseStatus = status
	if (pauseBtnEl) {
		if (status === "Pending") {
			pauseBtnEl.textContent = "Pending..."
			pauseBtnEl.className = "pause-btn-base"
		} else if (status === "Paused") {
			pauseBtnEl.textContent = "Resume"
			pauseBtnEl.className = "pause-btn-hover"
		} else {
			pauseBtnEl.textContent = "Pause"
			pauseBtnEl.className = "pause-btn-active"
		}
	}
}

pauseBtnEl?.addEventListener("click", async () => {
	const requestPause = pauseStatus === "Running"
	try {
		await invoke("toggle_process_pause", {
			projectPath: activeProject,
			engine: currentEngine,
			pause: requestPause,
			threadId: activeThreadId || "",
		})
	} catch (e) {
		console.error("Failed to toggle pause:", e)
	}
})

listen<{ project_path: string; status: "Running" | "Pending" | "Paused" }>(
	"pause-status",
	(event) => {
		const { project_path, status } = event.payload
		if (project_path === activeProject) {
			updatePauseUI(status)
			if (
				activeThreadId &&
				typeof lastRenderedThreadLog === "string" &&
				typeof renderCustomTuiLog === "function"
			) {
				renderCustomTuiLog(lastRenderedThreadLog)
			}
		}
	},
)

// Hardcoded initial projects list mapped with unique random colors and default engines
const initialProjects: Project[] = [
	{
		path: "/Users/matt/projects/ai-os",
		name: "ai-os",
		color: "#3b82f6",
		lastActive: Date.now(),
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/structural-constraint-art",
		name: "structural-constraint-art",
		color: "#ec4899",
		lastActive: Date.now() - 1000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/now-music",
		name: "now-music",
		color: "#10b981",
		lastActive: Date.now() - 2000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/antigravity-optimization",
		name: "antigravity-optimization",
		color: "#f59e0b",
		lastActive: Date.now() - 3000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/webpage-compressor",
		name: "webpage-compressor",
		color: "#8b5cf6",
		lastActive: Date.now() - 4000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/tic-tac-toe",
		name: "tic-tac-toe",
		color: "#ef4444",
		lastActive: Date.now() - 5000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/agy-animation",
		name: "agy-animation",
		color: "#06b6d4",
		lastActive: Date.now() - 6000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/atlas-calculator",
		name: "atlas-calculator",
		color: "#10b981",
		lastActive: Date.now() - 7000,
		engine: "agy",
		isTerminalMode: false,
	},
	{
		path: "/Users/matt/projects/animation_project",
		name: "animation_project",
		color: "#6366f1",
		lastActive: Date.now() - 8000,
		engine: "agy",
		isTerminalMode: false,
	},
]

// Load projects from localStorage or use initial list
let projects: Project[] = (() => {
	const saved = localStorage.getItem("ai-os-projects")
	let loadedList: any[] = []
	if (saved) {
		try {
			loadedList = JSON.parse(saved)
		} catch (e) {
			console.error("Failed to parse saved projects:", e)
			loadedList = initialProjects
		}
	} else {
		loadedList = initialProjects
	}

	const uniqueProjectsMap = new Map<string, Project>()
	for (const p of loadedList) {
		let cleanPath = p.path || ""
		if (
			cleanPath.includes("/projects/thread-") ||
			cleanPath.includes("/Users/matthewmurphy")
		) {
			continue // Filter out legacy mock thread projects and legacy user projects
		}
		while (cleanPath.length > 0 && /[`*.,:;)}"\]]$/.test(cleanPath)) {
			cleanPath = cleanPath.slice(0, -1)
		}
		let cleanName = p.name || ""
		while (cleanName.length > 0 && /[`*.,:;)}"\]]$/.test(cleanName)) {
			cleanName = cleanName.slice(0, -1)
		}

		if (!cleanPath) continue

		const mapped: Project = {
			path: cleanPath,
			name: cleanName,
			color: p.color || "#3b82f6",
			lastActive: p.lastActive || Date.now(),
			engine: p.engine || "agy",
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
			localStorage.setItem("ai-os-projects", JSON.stringify(cleaned))
		} catch (e) {
			console.error("Failed to save cleaned projects:", e)
		}
	}
	return cleaned
})()

const saveProjects = () => {
	localStorage.setItem("ai-os-projects", JSON.stringify(projects))
}

// ----------------------------------------------------
// 3. Terminals Setup & Integration
// ----------------------------------------------------

const isDarkMode = () =>
	window.matchMedia("(prefers-color-scheme: dark)").matches

const applyTheme = () => {
	if (isDarkMode()) {
		document.documentElement.classList.add("dark")
	} else {
		document.documentElement.classList.remove("dark")
	}
}

// Initialize dark mode class on load
applyTheme()

const getTermTheme = () => {
	return isDarkMode() ?
			{ background: "#000000", foreground: "#ffffff" }
		:	{ background: "#ffffff", foreground: "#000000" }
}

const getMiniTermTheme = () => {
	return isDarkMode() ?
			{ background: "#000000", foreground: "#10b981" }
		:	{ background: "#ffffff", foreground: "#059669" }
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

const handleLink = (e: MouseEvent, uri: string) => {
	if (e.metaKey) {
		let finalUri = uri

		// Handle web URLs
		if (finalUri.startsWith("http://") || finalUri.startsWith("https://")) {
			open(finalUri).catch((err) =>
				console.error("Failed to open web link:", err),
			)
			return
		}

		// Clean up file:// prefix if present
		if (finalUri.startsWith("file://")) {
			finalUri = finalUri.replace("file://", "")
		}

		// Resolve relative paths against the active project
		if (!finalUri.startsWith("/") && !finalUri.startsWith("~/")) {
			if (finalUri.startsWith("./")) {
				finalUri = finalUri.slice(2)
			}
			finalUri = `${activeProject}/${finalUri}`
		}

		// Use custom rust command to circumvent Tauri `open` URL restrictions
		invoke("open_path", { path: finalUri }).catch((err) =>
			console.error("Failed to open path:", err),
		)
	}
}

;(window as any).openPath = (path: string) => {
	invoke("open_path", { path }).catch((err) =>
		console.error("Failed to open path:", err),
	)
}

;(window as any).copyTextToClipboard = (text: string, btn: HTMLButtonElement) => {
	navigator.clipboard.writeText(text).then(() => {
		const originalHtml = btn.innerHTML
		btn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon"><polyline points="20 6 9 17 4 12"></polyline></svg>`
		btn.classList.add("copied")
		setTimeout(() => {
			btn.innerHTML = originalHtml
			btn.classList.remove("copied")
		}, 2000)
	}).catch(err => {
		console.error("Failed to copy:", err)
	})
}

class LocalPathLinkProvider implements ILinkProvider {
	constructor(
		private term: Terminal,
		private handler: (e: MouseEvent, uri: string) => void,
	) {}
	provideLinks(
		bufferLineNumber: number,
		callback: (links: ILink[] | undefined) => void,
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
				activate: (e: MouseEvent, text: string) => this.handler(e, text),
			})
		}
		callback(links)
	}
}

term.loadAddon(new WebLinksAddon(handleLink))
term.registerLinkProvider(new LocalPathLinkProvider(term, handleLink))

term.onData((data) => {
	invoke("write_to_pty", {
		data,
		projectPath: activeProject,
		terminalType: currentEngine,
	}).catch((err) => {
		console.error("Failed to write key to Engine PTY:", err)
	})

	// Removed auto-adjust terminal height on slash command here because it causes tmux to frenzy
	// and checking startsWith('/') on a terminal line is unreliable due to shell prompts.
})

term.onResize(({ cols, rows }) => {
	if (cols > 0 && rows > 0) {
		invoke("resize_pty", {
			rows,
			cols,
			projectPath: activeProject,
			terminalType: "engine",
		}).catch((err) => {
			console.error("Failed to resize Engine PTY:", err)
		})
	}
})

term.attachCustomKeyEventHandler((e) => {
	if (e.key === "v" && e.metaKey && e.type === "keydown") {
		navigator.clipboard.readText().then((text) => {
			invoke("write_to_pty", {
				data: text,
				projectPath: activeProject,
				terminalType: currentEngine,
			}).catch(console.error)
		})
		return false
	}
	if (e.key === "Enter" && e.shiftKey && e.type === "keydown") {
		e.preventDefault()
		invoke("write_to_pty", {
			data: "\x1b\x0d",
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
	.matchMedia("(prefers-color-scheme: dark)")
	.addEventListener("change", (e) => {
		applyTheme()
		term.options.theme = getTermTheme()
		miniTerm.options.theme = getMiniTermTheme()

		// Inject the theme command to the backend engines ONLY if active engine is Claude
		if (currentEngine === "claude" && activeProject) {
			const themeStr = e.matches ? "dark" : "light"
			const msg = `/theme ${themeStr}\x0d`
			invoke("write_to_pty", {
				data: msg,
				projectPath: activeProject,
				terminalType: "claude",
			}).catch(console.error)
		}
	})
const miniFitAddon = new FitAddon()
miniTerm.loadAddon(miniFitAddon)
miniTerm.loadAddon(new WebLinksAddon(handleLink))
miniTerm.registerLinkProvider(new LocalPathLinkProvider(miniTerm, handleLink))

let miniInputBuffer = ""

miniTerm.onData((data) => {
	// Intercept Escape key
	if (data === "\x1b") {
		exitTerminalMode()
		return
	}

	// Write directly to PTY
	invoke("write_to_pty", {
		data,
		projectPath: activeProject,
		terminalType: "mini",
	}).catch((err) => {
		console.error("Failed to write key to Mini PTY:", err)
	})

	// Check buffer for command exits
	for (let i = 0; i < data.length; i++) {
		const char = data[i]
		if (char === "\r" || char === "\n") {
			const cmd = miniInputBuffer.trim()
			if (cmd === "exit" || cmd === "exit()") {
				exitTerminalMode()
			}
			miniInputBuffer = ""
		} else if (char === "\x7f" || char === "\x08") {
			miniInputBuffer = miniInputBuffer.slice(0, -1)
		} else {
			miniInputBuffer += char
		}
	}
})

miniTerm.onResize(({ cols, rows }) => {
	if (cols > 0 && rows > 0) {
		invoke("resize_pty", {
			rows,
			cols,
			projectPath: activeProject,
			terminalType: "mini",
		}).catch((err) => {
			console.error("Failed to resize Mini PTY:", err)
		})
	}
})

miniTerm.attachCustomKeyEventHandler((e) => {
	if (e.key === "v" && e.metaKey && e.type === "keydown") {
		navigator.clipboard.readText().then((text) => {
			invoke("write_to_pty", {
				data: text,
				projectPath: activeProject,
				terminalType: "mini",
			}).catch(console.error)
		})
		return false
	}
	if (e.key === "Enter" && e.shiftKey && e.type === "keydown") {
		e.preventDefault()
		invoke("write_to_pty", {
			data: "\x1b\x0d",
			projectPath: activeProject,
			terminalType: "mini",
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
	if (
		term.element &&
		term.element.clientWidth > 0 &&
		term.element.clientHeight > 0
	) {
		try {
			fitAddon.fit()
		} catch (e) {}
	}
	if (
		miniTerm.element &&
		miniTerm.element.clientWidth > 0 &&
		miniTerm.element.clientHeight > 0
	) {
		try {
			miniFitAddon.fit()
		} catch (e) {}
	}
}

let resizePtyTimeout: any = null
const debouncedResizePty = () => {
	if (resizePtyTimeout) clearTimeout(resizePtyTimeout)
	resizePtyTimeout = setTimeout(() => {
		resizePty()
	}, 50)
}

const container = document.getElementById("terminal-container")
if (container) {
	term.open(container)
}

const miniContainer = document.getElementById("mini-terminal-container")
if (miniContainer) {
	miniTerm.open(miniContainer)
}

window.addEventListener("resize", () => {
	debouncedResizePty()
})

// ----------------------------------------------------
// 7. Output Modal & Virtual Terminal Parser
// ----------------------------------------------------
const markdownPreviewPane = document.getElementById("markdown-preview-pane")
if (markdownPreviewPane) {
	initOS(markdownPreviewPane)
}

let previewAutoScroll = true
let isUpdatingPreviewDOM = false

const forceScrollToBottom = (pane: HTMLElement) => {
	previewAutoScroll = true
	const scrollEl = getScrollEl(pane) || pane
	scrollEl.scrollTop = scrollEl.scrollHeight
	const btn = document.getElementById("scroll-to-bottom-btn")
	if (btn) {
		btn.classList.remove("visible")
	}
}

const checkAndScrollToBottom = (pane: HTMLElement) => {
	const btn = document.getElementById("scroll-to-bottom-btn")
	const scrollEl = getScrollEl(pane) || pane
	if (previewAutoScroll) {
		scrollEl.scrollTop = scrollEl.scrollHeight
		if (btn) {
			btn.classList.remove("visible")
		}
	} else {
		if (btn) {
			btn.classList.add("visible")
		}
	}
}

if (markdownPreviewPane) {
	const scrollEl = getScrollEl(markdownPreviewPane)
	if (scrollEl) {
		scrollEl.addEventListener("scroll", () => {
			if (isUpdatingPreviewDOM) return
			const isAtBottom =
				scrollEl.scrollHeight - scrollEl.scrollTop <=
				scrollEl.clientHeight + 40
			if (isAtBottom) {
				previewAutoScroll = true
				const btn = document.getElementById("scroll-to-bottom-btn")
				if (btn) {
					btn.classList.remove("visible")
				}
			} else {
				previewAutoScroll = false
			}
		})
	}
	// Also listen on host element in case overflow-y: auto !important makes it scrollable
	markdownPreviewPane.addEventListener("scroll", () => {
		if (isUpdatingPreviewDOM) return
		console.log('[SCROLL-DEBUG] HOST scroll event fired, scrollTop=', markdownPreviewPane.scrollTop, 'scrollHeight=', markdownPreviewPane.scrollHeight, 'clientHeight=', markdownPreviewPane.clientHeight)
	})
}

const scrollToBottomBtn = document.getElementById("scroll-to-bottom-btn")
if (scrollToBottomBtn && markdownPreviewPane) {
	scrollToBottomBtn.addEventListener("click", () => {
		forceScrollToBottom(markdownPreviewPane)
	})
}

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
	created_at?: string
}

interface ToolCallItem {
	name: string
	actionSummary: string
	icon: string
	targetPath?: string
	args?: any
}

interface RenderBlock {
	type: "user_input" | "planner_response" | "tool_call" | "thought"
	content?: string
	call?: ToolCallItem
	historicalContext?: string
	threadId?: string
	createdAt?: string
}

const renderer = {
	code(token: any) {
		const text = token.text || ""
		const lang = token.lang || ""
		const escapedText = text
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;")
		return `
            <div class="group">
                <button class="copy-btn" data-content="${encodeURIComponent(text)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                <pre><code class="language-${lang}">${escapedText}</code></pre>
            </div>
        `
	},
}
marked.use({ renderer })

const buildTimelineHtml = (
	steps: Step[],
	isThinking: boolean,
): { html: string; hasOutputInLastTurn: boolean; latestThought: string } => {
	const blocks: RenderBlock[] = []
	let latestThought = ""

	steps.forEach((step) => {
		if (step.type === "USER_INPUT" && step.content) {
			let prompt = step.content

			prompt = prompt
				.replace(/<SYSTEM_INSTRUCTIONS>[\s\S]*?<\/SYSTEM_INSTRUCTIONS>/gi, "")
				.trim()
			prompt = prompt
				.replace(/<ADDITIONAL_METADATA>[\s\S]*?<\/ADDITIONAL_METADATA>/gi, "")
				.trim()
			prompt = prompt
				.replace(/<USER_SETTINGS_CHANGE>[\s\S]*?<\/USER_SETTINGS_CHANGE>/gi, "")
				.trim()
			prompt = prompt.replace(/<user_rules>[\s\S]*?<\/user_rules>/gi, "").trim()
			prompt = prompt
				.replace(/<ephemeral_message>[\s\S]*?<\/ephemeral_message>/gi, "")
				.trim()
			prompt = prompt.replace(/\[SYSTEM DIRECTIVE:[\s\S]*?\]\n*/g, "").trim()

			let historicalContextText = ""
			let threadId = ""

			const convHistoryMarker = "# Conversation History\n"
			const convHistoryIdx = prompt.indexOf(convHistoryMarker)
			if (convHistoryIdx !== -1) {
				historicalContextText = prompt.substring(convHistoryIdx).trim()
				prompt = prompt.substring(0, convHistoryIdx).trim()
			}

			const startTag = "<USER_REQUEST>"
			const endTag = "</USER_REQUEST>"
			const startIdx = prompt.indexOf(startTag)
			const endIdx = prompt.indexOf(endTag)
			if (startIdx !== -1 && endIdx !== -1) {
				prompt = prompt.substring(startIdx + startTag.length, endIdx).trim()
			}

			if (prompt.includes("Continuing conversation from history")) {
				const threadIdMatch = prompt.match(/Thread ID:\s*([a-fA-F0-9-]+)/)
				if (threadIdMatch) {
					threadId = threadIdMatch[1]
				}

				const histIdx = prompt.indexOf("Historical Context:\n")
				const userReqIdx = prompt.indexOf("\n\nUser request: ")

				if (histIdx !== -1 && userReqIdx !== -1 && userReqIdx > histIdx) {
					const legacyContext = prompt
						.substring(histIdx + "Historical Context:\n".length, userReqIdx)
						.trim()
					historicalContextText =
						historicalContextText ?
							legacyContext + "\n\n" + historicalContextText
						:	legacyContext
					prompt = prompt
						.substring(userReqIdx + "\n\nUser request: ".length)
						.trim()
				} else {
					const oldHistIdx = prompt.indexOf("Historical Context:\n")
					const oldUserReqIdx = prompt.lastIndexOf("User request: ")
					if (
						oldHistIdx !== -1 &&
						oldUserReqIdx !== -1 &&
						oldUserReqIdx > oldHistIdx
					) {
						const legacyContext = prompt
							.substring(
								oldHistIdx + "Historical Context:\n".length,
								oldUserReqIdx,
							)
							.trim()
						historicalContextText =
							historicalContextText ?
								legacyContext + "\n\n" + historicalContextText
							:	legacyContext
						prompt = prompt
							.substring(oldUserReqIdx + "User request: ".length)
							.trim()
					}
				}
			}

			blocks.push({
				type: "user_input",
				content: prompt,
				historicalContext: historicalContextText || undefined,
				threadId: threadId || undefined,
				createdAt: step.created_at,
			})
		} else {
			let thoughtProcess = undefined
			let cleanedContent = undefined

			if (
				step.source === "MODEL" &&
				step.type === "PLANNER_RESPONSE" &&
				step.content
			) {
				const thoughtMatch = step.content.match(
					/<thought>([\s\S]*?)<\/thought>/i,
				)
				if (thoughtMatch) {
					thoughtProcess = thoughtMatch[1].trim()
					latestThought = thoughtProcess
					cleanedContent = step.content
						.replace(/<thought>[\s\S]*?<\/thought>/i, "")
						.replace(/<THREAD_NAME>[\s\S]*?<\/THREAD_NAME>/gi, "")
						.trim()
				} else {
					cleanedContent = step.content
						.replace(/<THREAD_NAME>[\s\S]*?<\/THREAD_NAME>/gi, "")
						.trim()
				}
			}

			if (thoughtProcess) {
				blocks.push({ type: "thought", content: thoughtProcess, createdAt: step.created_at })
			}

			if (step.tool_calls && step.tool_calls.length > 0) {
				step.tool_calls.forEach((call) => {
					let actionSummary = ""
					if (call.args && typeof call.args.toolSummary === "string") {
						actionSummary = call.args.toolSummary
					} else if (call.args && typeof call.args.toolAction === "string") {
						actionSummary = call.args.toolAction
					}

					if (actionSummary.startsWith('"') && actionSummary.endsWith('"')) {
						actionSummary = actionSummary.slice(1, -1)
					}

					if (!actionSummary) {
						actionSummary = `Running tool ${call.name}`
					}

					let icon = "🛠️"
					if (call.name.includes("search") || call.name.includes("grep"))
						icon = "🔍"
					else if (
						call.name.includes("file") ||
						call.name.includes("write") ||
						call.name.includes("replace")
					)
						icon = "📝"
					else if (call.name.includes("command") || call.name.includes("run"))
						icon = "💻"
					else if (call.name.includes("dir") || call.name.includes("list"))
						icon = "📂"

					let targetPath = ""
					if (call.args) {
						if (typeof call.args.TargetFile === "string")
							targetPath = cleanPath(call.args.TargetFile)
						else if (typeof call.args.AbsolutePath === "string")
							targetPath = cleanPath(call.args.AbsolutePath)
						else if (typeof call.args.DirectoryPath === "string")
							targetPath = cleanPath(call.args.DirectoryPath)
						else if (typeof call.args.SearchPath === "string")
							targetPath = cleanPath(call.args.SearchPath)
					}

					blocks.push({
						type: "tool_call",
						call: {
							name: call.name,
							actionSummary,
							icon,
							targetPath: targetPath || undefined,
							args: call.args,
						},
						createdAt: step.created_at,
					})
				})
			}

			if (cleanedContent) {
				blocks.push({ type: "planner_response", content: cleanedContent, createdAt: step.created_at })
			}
		}
	})

	let html = ""
	const renderToolCallHtml = (call: ToolCallItem) => {
		let pathHtml = ""
		if (call.targetPath) {
			const displayPath = formatPathForUser(call.targetPath)
			pathHtml = ` <a href="#" onclick="window.openPath('${call.targetPath.replace(/'/g, "\\'")}')" class="file-link" title="${formatPathForUser(call.targetPath)}">${displayPath}</a>`
		}

		let argsHtml = ""
		if (call.args) {
			let argsListHtml = ""
			try {
				if (typeof call.args === "object" && call.args !== null) {
					for (const [key, value] of Object.entries(call.args)) {
						let displayValue: any = value
						let isMultiline = false

						if (typeof displayValue === "string") {
							if (displayValue.includes("\n")) {
								displayValue = displayValue.replace(/\n/g, "\n")
							}
							if (displayValue.includes("\n")) {
								isMultiline = true
							}
						}

						if (isMultiline) {
							const parsedHtml = marked.parse(displayValue as string) as string
							argsListHtml += `<tr><td class="tool-call-arg-name">${key}</td><td class="tool-call-arg-value"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border tool-call-multiline-val">${parsedHtml}</div></td></tr>`
						} else if (typeof displayValue === "string") {
							argsListHtml += `<tr><td class="tool-call-arg-name">${key}</td><td class="tool-call-arg-value"><span class="tool-call-string-val">${displayValue.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</span></td></tr>`
						} else {
							argsListHtml += `<tr><td class="tool-call-arg-name">${key}</td><td class="tool-call-arg-value"><pre class="tool-call-json-val"><code>${JSON.stringify(displayValue).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre></td></tr>`
						}
					}
					argsHtml = `<table class="tool-call-args-table"><tbody>${argsListHtml}</tbody></table>`
				} else {
					throw new Error("Not an object")
				}
			} catch (e) {
				const argsStr = JSON.stringify(call.args, null, 2)
					.replace(/&/g, "&amp;")
					.replace(/</g, "&lt;")
					.replace(/>/g, "&gt;")
				argsHtml = `<pre class="tool-call-raw-args"><code>${argsStr}</code></pre>`
			}
		}

		return `
            <div class="unified-tool-call-row">
                <details class="tool-call-details"><summary>
                        <div>
                            <span class="toggle-icon">▶</span>
                            <span>${call.icon}</span>
                            <span class="tool-summary">${call.actionSummary}</span>
                        </div>
                        ${pathHtml ? `<div>${pathHtml}</div>` : ""}
                    </summary><div class="tool-call-details-body">${argsHtml.trim()}</div></details>
            </div>
        `
	}

	interface Turn {
		userInput: RenderBlock | null
		agentBlocks: RenderBlock[]
	}
	const turns: Turn[] = []
	let currentTurn: Turn = { userInput: null, agentBlocks: [] }

	blocks.forEach((block) => {
		if (block.type === "user_input") {
			if (currentTurn.userInput || currentTurn.agentBlocks.length > 0) {
				turns.push(currentTurn)
			}
			currentTurn = { userInput: block, agentBlocks: [] }
		} else {
			currentTurn.agentBlocks.push(block)
		}
	})
	if (currentTurn.userInput || currentTurn.agentBlocks.length > 0) {
		turns.push(currentTurn)
	}

	let hasOutputInLastTurn = false

	interface MessageItem {
		sender: "user" | "agent" | "historical"
		type: "historical" | "user" | "tool-call-group" | "agent-text"
		createdAt?: string
		html: string
		copyContent?: string
	}

	const messageItems: MessageItem[] = []

	const renderTimestampHtml = (createdAt?: string) => {
		if (!createdAt) return ""
		const dateMs = new Date(createdAt).getTime()
		if (isNaN(dateMs)) return ""
		const relative = getRelativeDateStr(dateMs)
		const full = getFullDateStr(dateMs)
		const escRelative = relative.replace(/'/g, "&#39;")
		const escFull = full.replace(/'/g, "&#39;")
		return `
			<span class="message-timestamp" 
				  data-relative="${escRelative}" 
				  data-full="${escFull}" 
				  data-mode="relative"
				  onmouseenter="if(this.getAttribute('data-mode')==='relative') this.textContent = this.getAttribute('data-full')" 
				  onmouseleave="if(this.getAttribute('data-mode')==='relative') this.textContent = this.getAttribute('data-relative')"
				  onclick="const m = this.getAttribute('data-mode') === 'relative' ? 'full' : 'relative'; this.setAttribute('data-mode', m); this.textContent = this.getAttribute('data-' + m);">
				${relative}
			</span>
		`
	}

	turns.forEach((turn, index) => {
		const isLastTurn = index === turns.length - 1

		if (turn.userInput && turn.userInput.content) {
			const block = turn.userInput
			if (block.historicalContext) {
				const escapedThreadId = block.threadId || ""
				const historicalHtml = `
                        <details class="group">
                            <summary class="historical-summary">
                                <span>📜 Historical Context of active thread ${escapedThreadId ? `(${escapedThreadId.substring(0, 8)}...)` : ""}</span>
                                <span class="toggle-icon">▶</span>
                            </summary>
                             <div class="historical-details">
${marked.parse(block.historicalContext)}
                             </div>
                        </details>
                `
				messageItems.push({
					sender: "user",
					type: "historical",
					createdAt: block.createdAt,
					html: historicalHtml
				})
			}
			const escapedContent = (block.content || "")
				.replace(/&/g, "&amp;")
				.replace(/</g, "&lt;")
				.replace(/>/g, "&gt;")

			messageItems.push({
				sender: "user",
				type: "user",
				createdAt: block.createdAt,
				html: escapedContent,
				copyContent: block.content || ""
			})
		}

		const intertwineHtml: string[] = []
		const textResponses: Array<{ content: string; createdAt?: string }> = []
		let toolCallCreatedAt: string | undefined = undefined

		turn.agentBlocks.forEach((b, idx) => {
			if (b.type === "tool_call" && b.call) {
				intertwineHtml.push(renderToolCallHtml(b.call))
				if (!toolCallCreatedAt) {
					toolCallCreatedAt = b.createdAt
				}
			} else if (b.type === "thought" && b.content) {
				const thoughtHtml = `<div class="agent-thought">${b.content.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>`
				intertwineHtml.push(thoughtHtml)
				if (!toolCallCreatedAt) {
					toolCallCreatedAt = b.createdAt
				}
			} else if (b.type === "planner_response" && b.content) {
				const followedByToolCall = turn.agentBlocks
					.slice(idx + 1)
					.some((sibling) => sibling.type === "tool_call")
				if (followedByToolCall) {
					const interstitialHtml = `
                     <div class="agent-interstitial-response prose prose-sm">
                         <div class="text-content">${(marked.parse(b.content.trim()) as string).trim()}</div>
                     </div>
                     `
					intertwineHtml.push(interstitialHtml)
					if (!toolCallCreatedAt) {
						toolCallCreatedAt = b.createdAt
					}
				} else {
					textResponses.push({ content: b.content, createdAt: b.createdAt })
					if (isLastTurn) {
						hasOutputInLastTurn = true
					}
				}
			}
		})

		if (intertwineHtml.length > 0) {
			const shouldOpen = isLastTurn && isThinking
			const boxId =
				isLastTurn ?
					"unified-tool-calls-box"
				:	`tool-calls-box-${Math.random().toString(36).substr(2, 9)}`
			const listId =
				isLastTurn ?
					"unified-tool-calls-list"
				:	`tool-calls-list-${Math.random().toString(36).substr(2, 9)}`

			const toolCallCount = turn.agentBlocks.filter(
				(b) => b.type === "tool_call",
			).length
			const headerText =
				toolCallCount > 0 ?
					`Tool Calls & Thinking (${toolCallCount})`
				:	`Agent Thinking...`

			let toolCallText = ""
			turn.agentBlocks.forEach((b, idx2) => {
				if (b.type === "tool_call" && b.call) {
					let callText = `[Tool Call: ${b.call.name}]\n`
					if (b.call.targetPath) {
						callText += `Path: ${b.call.targetPath}\n`
					}
					if (b.call.args) {
						callText += `Arguments: ${JSON.stringify(b.call.args, null, 2)}\n`
					}
					toolCallText += callText + "\n"
				} else if (b.type === "thought" && b.content) {
					toolCallText += `[Thought]\n${b.content}\n\n`
				} else if (b.type === "planner_response" && b.content) {
					const followedByToolCall2 = turn.agentBlocks
						.slice(idx2 + 1)
						.some((sibling) => sibling.type === "tool_call")
					if (followedByToolCall2) {
						toolCallText += `${b.content}\n\n`
					}
				}
			})

			const toolCallGroupHtml = `
                    <details class="group tool-calls-box" id="${boxId}" ${shouldOpen ? "open" : ""}>
                        <summary class="tool-call-summary">
                            <span>${headerText}</span>
                            <span class="toggle-icon">▶</span>
                        </summary>
                        <div class="historical-details unified-tool-calls-list" id="${listId}">
                            ${intertwineHtml.join("")}
                        </div>
                    </details>
            `
			messageItems.push({
				sender: "agent",
				type: "tool-call-group",
				createdAt: toolCallCreatedAt,
				html: toolCallGroupHtml,
				copyContent: toolCallText.trim()
			})
		}

		textResponses.forEach((r) => {
			const cleanedContent = r.content
				.replace(/<THREAD_NAME>[\s\S]*?<\/THREAD_NAME>/g, "")
				.trim()
			if (cleanedContent) {
				messageItems.push({
					sender: "agent",
					type: "agent-text",
					createdAt: r.createdAt,
					html: marked.parse(cleanedContent) as string,
					copyContent: cleanedContent
				})
			}
		})
	})

	interface GroupedMessage {
		sender: "user" | "agent" | "historical"
		items: MessageItem[]
	}

	const grouped: GroupedMessage[] = []
	let currentGroup: GroupedMessage | null = null

	messageItems.forEach((item) => {
		if (item.sender === "historical") {
			if (currentGroup) {
				grouped.push(currentGroup)
				currentGroup = null
			}
			grouped.push({ sender: "historical", items: [item] })
		} else {
			if (currentGroup && currentGroup.sender === item.sender) {
				currentGroup.items.push(item)
			} else {
				if (currentGroup) {
					grouped.push(currentGroup)
				}
				currentGroup = { sender: item.sender, items: [item] }
			}
		}
	})
	if (currentGroup) {
		grouped.push(currentGroup)
	}

	grouped.forEach((g) => {
		if (g.sender === "historical") {
			const item = g.items[0]
			html += `
            <div class="chat-message agent historical">
                <div class="message-content">
                    ${item.createdAt ? `<div class="message-meta">${renderTimestampHtml(item.createdAt)}</div>` : ""}
                    ${item.html}
                </div>
            </div>
            `
		} else if (g.sender === "user") {
			let groupContentHtml = ""
			let copyUserText = ""
			g.items.forEach((item, idx) => {
				const isText = item.type === "user" || item.type === "agent-text"
				groupContentHtml += `
                <div class="message-sub-block">
                    <div class="message-meta">
                        ${renderTimestampHtml(item.createdAt)}
                    </div>
                    <div class="message-text-container">
                        ${isText ? `<div class="text-content">${item.html}</div>` : item.html}
                    </div>
                </div>
                `
				if (idx < g.items.length - 1) {
					groupContentHtml += `<div class="message-divider"></div>`
				}
				if (item.copyContent) {
					if (copyUserText) copyUserText += "\n\n"
					copyUserText += item.copyContent
				}
			})

			const encUser = encodeURIComponent(copyUserText)
			const copyButtonsHtml = `
            <div class="agent-copy-buttons">
                ${copyUserText ? `
                <button class="agent-copy-btn" title="Copy user message" onclick="window.copyTextToClipboard(decodeURIComponent('${encUser.replace(/'/g, "\\'")}'), this)">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </button>
                ` : ""}
            </div>
            `

			html += `
            <div class="chat-message user">
                ${copyButtonsHtml}
                <div class="message-content group">
                    ${groupContentHtml}
                </div>
            </div>
            `
		} else if (g.sender === "agent") {
			let groupContentHtml = ""
			let copyToolsText = ""
			let copyMessagesText = ""

			g.items.forEach((item, idx) => {
				const isText = item.type === "user" || item.type === "agent-text"
				groupContentHtml += `
                <div class="message-sub-block">
                    <div class="message-meta">
                        ${renderTimestampHtml(item.createdAt)}
                    </div>
                    <div class="message-text-container">
                        ${isText ? `<div class="text-content">${item.html}</div>` : item.html}
                    </div>
                </div>
                `
				if (idx < g.items.length - 1) {
					groupContentHtml += `<div class="message-divider"></div>`
				}

				if (item.type === "tool-call-group" && item.copyContent) {
					if (copyToolsText) copyToolsText += "\n\n"
					copyToolsText += item.copyContent
				} else if (item.type === "agent-text" && item.copyContent) {
					if (copyMessagesText) copyMessagesText += "\n\n"
					copyMessagesText += item.copyContent
				}
			})

			const copyAllText = [copyToolsText.trim(), copyMessagesText.trim()].filter(Boolean).join("\n\n")
			const encAll = encodeURIComponent(copyAllText)
			const encTools = encodeURIComponent(copyToolsText)
			const encMsgs = encodeURIComponent(copyMessagesText)

			const copyButtonsHtml = `
            <div class="agent-copy-buttons">
                ${copyAllText ? `
                <button class="agent-copy-btn" title="Copy entire response (tool calls + messages)" onclick="window.copyTextToClipboard(decodeURIComponent('${encAll.replace(/'/g, "\\'")}'), this)">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                </button>
                ` : ""}
                ${copyToolsText ? `
                <button class="agent-copy-btn" title="Copy tool calls & thinking only" onclick="window.copyTextToClipboard(decodeURIComponent('${encTools.replace(/'/g, "\\'")}'), this)">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                </button>
                ` : ""}
                ${copyMessagesText ? `
                <button class="agent-copy-btn" title="Copy agent messages only" onclick="window.copyTextToClipboard(decodeURIComponent('${encMsgs.replace(/'/g, "\\'")}'), this)">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </button>
                ` : ""}
            </div>
            `

			const hasToolCalls = g.items.some((item) => item.type === "tool-call-group");
			html += `
            <div class="chat-message agent${hasToolCalls ? " tool-call-group" : ""}">
                ${copyButtonsHtml}
                <div class="message-content group prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border">
                    ${groupContentHtml}
                </div>
            </div>
            `
		}
	})

	return { html, hasOutputInLastTurn, latestThought }
}

let lastRenderedThreadLog = ""
let lastRenderedThreadId = ""
let lastRenderedThinking = false
let liveAgyStream = ""
let toolCallsAutoScroll = true
let previousIsThinking = false

const renderCustomTuiLog = (jsonlContent: string, isThreadSwitch = false, forceEngineRunning?: boolean) => {
	if (!markdownPreviewPane) return

	const lines = jsonlContent.trim().split("\n")
	const steps: Step[] = []
	const editedFilesSet = new Set<string>()

	for (const line of lines) {
		if (!line.trim()) continue
		try {
			const step: Step = JSON.parse(line)
			steps.push(step)

			if (step.tool_calls) {
				for (const call of step.tool_calls) {
					if (
						call.name === "replace_file_content" ||
						call.name === "multi_replace_file_content" ||
						call.name === "write_to_file"
					) {
						if (call.args && typeof call.args.TargetFile === "string") {
							editedFilesSet.add(cleanPath(call.args.TargetFile))
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
			'<div class=">No conversation steps found.</div>'
		return
	}

	let html = ""

	if (editedFilesSet.size > 0) {
		const files = Array.from(editedFilesSet)
		html += `
        <div class="edited-files-container">
            <span class="edited-files-label">Edited Files:</span>
            ${files
							.map((file) => {
								const cleanedFile = cleanPath(file)
								const parts = cleanedFile.split("/")
								const name = parts[parts.length - 1]
								return `<a href="#" onclick="window.openPath('${cleanedFile.replace(/'/g, "\\'")}')" class="edited-file-link" title="${formatPathForUser(cleanedFile)}">${name}</a>`
							})
							.join("")}
        </div>
        `
	}

	let isThinking = false
	if (steps.length > 0) {
		let foundIndicator = false
		for (let i = steps.length - 1; i >= 0; i--) {
			const step = steps[i]
			if (step.status !== "DONE" && step.status !== "ERROR") {
				isThinking = true
				foundIndicator = true
				break
			}
			if (step.type === "PLANNER_RESPONSE") {
				if (step.tool_calls && step.tool_calls.length > 0) {
					isThinking = true
				} else {
					isThinking = false
				}
				foundIndicator = true
				break
			}
			if (step.type === "USER_INPUT") {
				isThinking = true
				foundIndicator = true
				break
			}
		}
		if (!foundIndicator) {
			isThinking = true
		}
	}

	if (forceEngineRunning === false) {
		isThinking = false
	}

	if (isThreadSwitch) {
		previousIsThinking = isThinking
		previewAutoScroll = true
		const btn = document.getElementById("scroll-to-bottom-btn")
		if (btn) {
			btn.classList.remove("visible")
		}
	}

	const justStartedThinking = isThinking && !previousIsThinking
	const justFinishedThinking = !isThinking && previousIsThinking
	previousIsThinking = isThinking

	const timelineResult = buildTimelineHtml(steps, isThinking)
	html += timelineResult.html

	if (isThinking && !timelineResult.hasOutputInLastTurn) {
		let statusText = "Agent is thinking & working..."
		if (timelineResult.latestThought) {
			const lines = timelineResult.latestThought
				.split("\n")
				.filter((l) => l.trim().length > 0)
			if (lines.length > 0) {
				statusText = lines[lines.length - 1].trim()
				if (statusText.length > 80) {
					statusText = statusText.substring(0, 80) + "..."
				}
			}
		}

		html += `
        <div class="chat-message agent thinking">
            <div class="message-content">
                <div class="thinking-loader">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
                <span class="thinking-text">${statusText.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</span>
            </div>
        </div>
        `
	}

	const detailsState = new Map<string, boolean>()
	const detailsCounts: Record<string, number> = {}

	const getDetailsKey = (
		el: HTMLDetailsElement,
		counts: Record<string, number>,
	) => {
		if (el.id === "unified-tool-calls-box") return el.id
		const summaryText =
			el.querySelector("summary")?.textContent?.trim() || "no-summary"
		counts[summaryText] = (counts[summaryText] || 0) + 1
		return `${summaryText}-${counts[summaryText]}`
	}

	const contentEl = getContentEl(markdownPreviewPane) || markdownPreviewPane
	const detailsElements = contentEl.querySelectorAll("details")
	if (!isThreadSwitch) {
		detailsElements.forEach((el) => {
			if (
				(justStartedThinking || justFinishedThinking) &&
				el.id === "unified-tool-calls-box"
			) {
				return
			}
			detailsState.set(getDetailsKey(el, detailsCounts), el.open)
		})
	}

	const oldToolCallsList = contentEl.querySelector(
		"#unified-tool-calls-list",
	) as HTMLElement | null
	let savedScrollTop = -1
	if (oldToolCallsList) {
		const oldScrollEl = getScrollEl(oldToolCallsList)
		savedScrollTop = oldScrollEl ? oldScrollEl.scrollTop : oldToolCallsList.scrollTop
		OverlayScrollbars(oldToolCallsList)?.destroy()
	}

	const previewScrollEl = getScrollEl(markdownPreviewPane) || markdownPreviewPane
	const savedPreviewScrollTop = previewScrollEl.scrollTop
	const savedHostScrollTop = markdownPreviewPane.scrollTop
	console.log('[SCROLL-DEBUG] BEFORE innerHTML: viewport.scrollTop=', savedPreviewScrollTop, 'host.scrollTop=', savedHostScrollTop, 'previewAutoScroll=', previewAutoScroll)

	isUpdatingPreviewDOM = true

	const previewContentEl = getContentEl(markdownPreviewPane)
	if (previewContentEl) {
		previewContentEl.innerHTML = html
	} else {
		markdownPreviewPane.innerHTML = html
	}

	console.log('[SCROLL-DEBUG] AFTER innerHTML: viewport.scrollTop=', previewScrollEl.scrollTop, 'host.scrollTop=', markdownPreviewPane.scrollTop)

	const newDetailsCounts: Record<string, number> = {}
	const newDetailsElements = contentEl.querySelectorAll("details")
	newDetailsElements.forEach((el) => {
		const key = getDetailsKey(el, newDetailsCounts)
		if (detailsState.has(key)) {
			el.open = detailsState.get(key)!
		}
	})

	const toolCallsList = contentEl.querySelector(
		"#unified-tool-calls-list",
	) as HTMLElement | null
	const toolCallsBox = contentEl.querySelector(
		"#unified-tool-calls-box",
	) as HTMLDetailsElement | null

	if (toolCallsList && toolCallsBox) {
		initOS(toolCallsList)
		const toolCallsScrollEl = getScrollEl(toolCallsList) || toolCallsList

		if (justStartedThinking) {
			toolCallsBox.open = true
		} else if (justFinishedThinking) {
			toolCallsBox.open = false
		}

		if (!toolCallsAutoScroll && savedScrollTop >= 0) {
			toolCallsScrollEl.scrollTop = savedScrollTop
		}

		toolCallsScrollEl.addEventListener("scroll", () => {
			const isAtBottom =
				toolCallsScrollEl.scrollHeight - toolCallsScrollEl.scrollTop <=
				toolCallsScrollEl.clientHeight + 20
			toolCallsAutoScroll = isAtBottom
		})

		if (
			toolCallsAutoScroll &&
			isThinking &&
			!timelineResult.hasOutputInLastTurn
		) {
			setTimeout(() => {
				const currentToolCallsList = (getContentEl(markdownPreviewPane) || markdownPreviewPane).querySelector(
					"#unified-tool-calls-list",
				) as HTMLElement | null
				const currentToolCallsScrollEl = getScrollEl(currentToolCallsList)
				if (currentToolCallsScrollEl) {
					currentToolCallsScrollEl.scrollTop = currentToolCallsScrollEl.scrollHeight
				}
			}, 30)
		}
	}

	// Restore scroll position using requestAnimationFrame (after layout)
	const targetScrollTop = previewAutoScroll ? previewScrollEl.scrollHeight : savedPreviewScrollTop
	previewScrollEl.scrollTop = targetScrollTop
	markdownPreviewPane.scrollTop = previewAutoScroll ? markdownPreviewPane.scrollHeight : savedHostScrollTop

	console.log('[SCROLL-DEBUG] SYNC restore: viewport.scrollTop=', previewScrollEl.scrollTop, 'host.scrollTop=', markdownPreviewPane.scrollTop, 'target=', targetScrollTop)

	requestAnimationFrame(() => {
		const rafTarget = previewAutoScroll ? previewScrollEl.scrollHeight : savedPreviewScrollTop
		previewScrollEl.scrollTop = rafTarget
		markdownPreviewPane.scrollTop = previewAutoScroll ? markdownPreviewPane.scrollHeight : savedHostScrollTop
		console.log('[SCROLL-DEBUG] RAF restore: viewport.scrollTop=', previewScrollEl.scrollTop, 'host.scrollTop=', markdownPreviewPane.scrollTop, 'target=', rafTarget)
		isUpdatingPreviewDOM = false
	})

	if (isThinking && !timelineResult.hasOutputInLastTurn) {
		setTimeout(() => {
			checkAndScrollToBottom(markdownPreviewPane)
		}, 50)
	}
}

// Poll the active thread's log file
setInterval(async () => {
	if (!activeThreadId) return
	const filepath = threadFilepaths.get(activeThreadId)
	if (!filepath) return

	try {
		const fileExists = await invoke<boolean>("file_exists", { filepath })
		if (fileExists) {
			const content = await invoke<string>("read_thread_log", {
				filepath,
			})
			const isRunning = await invoke<boolean>("is_engine_running", {
				engine: currentEngine,
				projectPath: activeProject,
				threadId: activeThreadId,
			})
			if (
				content !== lastRenderedThreadLog ||
				activeThreadId !== lastRenderedThreadId ||
				isRunning !== lastRenderedThinking
			) {
				const isThreadSwitch = activeThreadId !== lastRenderedThreadId
				if (isThreadSwitch) {
					liveAgyStream = ""
				}
				lastRenderedThreadLog = content
				lastRenderedThreadId = activeThreadId
				lastRenderedThinking = isRunning
				renderCustomTuiLog(content, isThreadSwitch, isRunning)
			}
		}
	} catch (e) {
		console.error("[AI-OS Thread Log Poll] Error:", e)
	}
}, 500)

const formatMarkdown = (text: string): string => {
	let formatted = text
	formatted = formatted.replace(/\*\*([^\*]+)\*\*/g, "\x1b[1m$1\x1b[22m")
	formatted = formatted.replace(/`([^`]+)`/g, "\x1b[36m$1\x1b[39m")
	return formatted
}

// Listen to Backend PTY events
listen<{ data: string; project_path: string; terminal_type: string }>(
	"pty-output",
	(event) => {
		let { data, project_path, terminal_type } = event.payload

		if (terminal_type === "agy") {
			data = formatMarkdown(data)
		}

		// Choose correct buffer
		let buffers = miniTermBuffers
		if (terminal_type === "claude") {
			buffers = claudeBuffers
		} else if (terminal_type === "agy") {
			buffers = agyBuffers
		} else if (terminal_type === "hermes") {
			buffers = hermesBuffers
		}

		// Append to cache buffer
		if (!buffers[project_path]) {
			buffers[project_path] = ""
		}
		buffers[project_path] += data
		if (buffers[project_path].length > 100000) {
			buffers[project_path] = buffers[project_path].substring(
				buffers[project_path].length - 50000,
			)
		}

		if (project_path === activeProject) {
			if (terminal_type === "agy") {
				const stripped = data
					.replace(/\x1B(?:\[[0-?]*[ -/]*[@-~]|[\(\)][a-zA-Z0-9])/g, "")
					.replace(/\x1B/g, "")
				for (let i = 0; i < stripped.length; i++) {
					if (stripped[i] === "\r") {
						const lastNewline = liveAgyStream.lastIndexOf("\n")
						liveAgyStream = liveAgyStream.substring(0, lastNewline + 1)
					} else if (stripped[i] === "\b") {
						liveAgyStream = liveAgyStream.slice(0, -1)
					} else {
						liveAgyStream += stripped[i]
					}
				}
				if (liveAgyStream.length > 20000) {
					liveAgyStream = liveAgyStream.substring(liveAgyStream.length - 10000)
				}
				const streamPane = document.getElementById("live-stream-pane")
				if (streamPane) {
					streamPane.textContent = liveAgyStream
					const previewPane = document.getElementById("markdown-preview-pane")
					if (previewPane) {
						checkAndScrollToBottom(previewPane)
					}
				}
			}

			if (terminal_type === "mini") {
				try {
					miniTerm.write(data)
				} catch (e) {}
			} else if (terminal_type === currentEngine) {
				try {
					term.write(data)
				} catch (e) {}

				// Auto-expand TUI if interactive prompt is detected
				setTimeout(() => {
					const tuiContainer = document.getElementById("terminal-container")
					let isInteractive = false
					let recentText = ""
					// Check the last few lines of the terminal buffer for prompts
					const baseY = term.buffer.active.baseY
					const cursorY = term.buffer.active.cursorY
					const numLinesToCheck = 5
					const startLine = Math.max(0, baseY + cursorY - numLinesToCheck)

					for (let i = startLine; i <= baseY + cursorY; i++) {
						const line = term.buffer.active.getLine(i)
						if (line) {
							const text = line.translateToString(true).trim()
							recentText += text + "\n"
							if (
								text.match(/(\(y\/n\)|\[y\/N\]|Approve\?)$/i) ||
								text.match(/^(Select|Choose) /i) ||
								text.endsWith("❯") ||
								text.endsWith("?")
							) {
								isInteractive = true
							}
						}
					}

					if (isInteractive && tuiContainer && activeTerminalPreset === 0) {
						applyTerminalPreset(1) // Auto-expand to medium on prompt if small
					}
				}, 50)
			}
		}
	},
)

// TUI Presets & Drag Resizing
const tuiContainer = document.getElementById("terminal-container")
const previewWrapper = document.getElementById("preview-wrapper")
const tuiResizeHandle = document.getElementById("tui-resize-handle")
const presetBtns = document.querySelectorAll(".preset-btn:not(.refresh-btn)")

let terminalPresets = [110, 300, 600]
try {
	const savedPresets = localStorage.getItem("terminalPresets")
	if (savedPresets) terminalPresets = JSON.parse(savedPresets)
} catch (e) {}

let activeTerminalPreset = 0
try {
	const savedActivePreset = localStorage.getItem("activeTerminalPreset")
	if (savedActivePreset !== null)
		activeTerminalPreset = parseInt(savedActivePreset, 10)
} catch (e) {}

function applyTerminalPreset(index: number) {
	activeTerminalPreset = index
	localStorage.setItem("activeTerminalPreset", index.toString())
	presetBtns.forEach((btn) => btn.classList.remove("active"))
	const activeBtn = document.querySelector(
		`.preset-btn[data-preset="${index}"]`,
	)
	if (activeBtn) activeBtn.classList.add("active")

	if (tuiContainer && previewWrapper) {
		tuiContainer.style.height = `${terminalPresets[index]}px`
	}

	setTimeout(() => {
		try {
			resizePty()
		} catch (e) {}
	}, 50)
	setTimeout(() => {
		try {
			resizePty()
		} catch (e) {}
	}, 150)
}
;(window as any).applyTerminalPreset = applyTerminalPreset

if (presetBtns.length > 0) {
	presetBtns.forEach((btn) => {
		btn.addEventListener("click", (e) => {
			const el = e.currentTarget as HTMLElement
			const index = parseInt(el.dataset.preset || "0", 10)
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

	tuiResizeHandle.addEventListener("mousedown", (e) => {
		isResizingTui = true
		startY = e.clientY
		startHeight = tuiContainer.offsetHeight
		document.body.style.cursor = "row-resize"
		e.preventDefault()
	})

	document.addEventListener("mousemove", (e) => {
		if (!isResizingTui) return
		const deltaY = startY - e.clientY // Dragging UP increases height
		let newHeight = startHeight + deltaY
		const minHeight = 50
		const maxHeight = window.innerHeight - 100

		if (newHeight >= minHeight && newHeight <= maxHeight) {
			tuiContainer.style.height = `${newHeight}px`
			terminalPresets[activeTerminalPreset] = newHeight
			localStorage.setItem("terminalPresets", JSON.stringify(terminalPresets))
			try {
				debouncedResizePty()
			} catch (e) {}
		}
	})

	document.addEventListener("mouseup", () => {
		if (isResizingTui) {
			isResizingTui = false
			document.body.style.cursor = "default"
			try {
				resizePty()
			} catch (e) {}
		}
	})
}

// Refresh terminal functionality
const refreshActiveTerminal = async () => {
	if (!activeProject) return

	// Reset xterm.js UI buffers
	term.reset()
	const activeBuffers =
		currentEngine === "claude"
			? claudeBuffers
			: currentEngine === "hermes"
				? hermesBuffers
				: agyBuffers
	if (activeBuffers[activeProject]) {
		term.write(activeBuffers[activeProject])
	} else {
		term.write(
			`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(activeProject)}...\x1b[0m\r\n`,
		)
	}

	// Trigger Rust backend to refresh the tmux client
	try {
		await invoke("refresh_tmux_session", {
			projectPath: activeProject,
			engine: currentEngine,
		})
	} catch (e) {
		console.error("Failed to trigger tmux refresh on backend:", e)
	}

	// Force resize
	resizePty()
}
;(window as any).refreshActiveTerminal = refreshActiveTerminal

const refreshBtn = document.getElementById("tui-refresh-btn")
if (refreshBtn) {
	refreshBtn.addEventListener("click", () => {
		refreshActiveTerminal()
	})
}

// Focus auto-refresh
window.addEventListener("focus", () => {
	refreshActiveTerminal()
})

// ResizeObserver on the terminal container to auto-resize PTY
if (tuiContainer) {
	try {
		const ro = new ResizeObserver(() => {
			debouncedResizePty()
		})
		ro.observe(tuiContainer)
	} catch (e) {
		console.warn("ResizeObserver failed or not supported:", e)
	}
}

// ----------------------------------------------------
// 4. Splitter Drag Resizing Panel (Legacy Splitter guards)
// ----------------------------------------------------
const splitter = document.getElementById("pane-splitter")
const panesContainer = document.getElementById("panes-container")

if (splitter && miniContainer && panesContainer) {
	let isDragging = false
	let startY = 0
	let startHeight = 0

	splitter.addEventListener("mousedown", (e) => {
		isDragging = true
		startY = e.clientY
		startHeight = miniContainer.offsetHeight
		document.body.style.cursor = "row-resize"
		e.preventDefault()
	})

	document.addEventListener("mousemove", (e) => {
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

	document.addEventListener("mouseup", () => {
		if (isDragging) {
			isDragging = false
			document.body.style.cursor = ""
			resizePty()
		}
	})
}

// 4a. Sidebar Width Resizing
const sidebarSplitter = document.getElementById("sidebar-splitter")
const sidebar = document.getElementById("projects-sidebar")

if (sidebarSplitter && sidebar) {
	const savedSidebarWidth = localStorage.getItem("sidebarWidth")
	if (savedSidebarWidth) {
		sidebar.style.width = `${savedSidebarWidth}px`
	}

	let isDragging = false
	let startX = 0
	let startWidth = 0

	sidebarSplitter.addEventListener("mousedown", (e) => {
		isDragging = true
		startX = e.clientX
		startWidth = sidebar.offsetWidth
		document.body.style.cursor = "col-resize"
		e.preventDefault()
	})

	document.addEventListener("mousemove", (e) => {
		if (!isDragging) return

		const deltaX = e.clientX - startX
		const newWidth = startWidth + deltaX
		const minWidth = 150
		const maxWidth = 600

		if (newWidth >= minWidth && newWidth <= maxWidth) {
			sidebar.style.width = `${newWidth}px`
			localStorage.setItem("sidebarWidth", newWidth.toString())
			debouncedResizePty()
		}
	})

	document.addEventListener("mouseup", () => {
		if (isDragging) {
			isDragging = false
			document.body.style.cursor = ""
			resizePty()
		}
	})
}

// 4c. Main Panes Horizontal Resizing
const mainSplitter = document.getElementById("main-splitter")
const terminalsWrapper = document.getElementById("terminals-wrapper")

if (mainSplitter && terminalsWrapper && panesContainer) {
	let isDragging = false
	let startX = 0
	let startWidth = 0

	mainSplitter.addEventListener("mousedown", (e) => {
		isDragging = true
		startX = e.clientX
		startWidth = terminalsWrapper.offsetWidth
		document.body.style.cursor = "col-resize"
		e.preventDefault()
	})

	document.addEventListener("mousemove", (e) => {
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

	document.addEventListener("mouseup", () => {
		if (isDragging) {
			isDragging = false
			document.body.style.cursor = ""
			resizePty()
		}
	})
}

// ----------------------------------------------------
// 5. Dynamic Mode UI Application
// ----------------------------------------------------
const applyTerminalModeUI = () => {
	const bottomArea = document.getElementById("bottom-input-area")

	if (isTerminalMode) {
		if (splitter) splitter.style.display = "block"
		if (miniContainer) miniContainer.style.display = "block"
		if (bottomArea) bottomArea.style.display = "none"
		setTimeout(() => {
			miniTerm.focus()
			resizePty()
		}, 50)
	} else {
		if (splitter) splitter.style.display = "none"
		if (miniContainer) miniContainer.style.display = "none"
		if (bottomArea) bottomArea.style.display = "flex"
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
const projectsListEl = document.getElementById("projects-list")
if (projectsListEl) {
	initOS(projectsListEl)
}
const currentDirPathEl = document.getElementById("current-dir-path")
const textarea = document.getElementById("prompt-input") as HTMLTextAreaElement
new Autocompleter(textarea, () => activeProject)

const renderProjects = () => {
	if (!projectsListEl) return
	const contentEl = getContentEl(projectsListEl) || projectsListEl
	contentEl.innerHTML = ""

	// Sort by recency
	const sorted = [...projects].sort((a, b) => b.lastActive - a.lastActive)

	sorted.forEach((project) => {
		const item = document.createElement("div")
		const isActive = project.path === activeProject

		item.className =
			isActive ? "project-item project-item-active" : "project-item"

		const header = document.createElement("div")
		header.className =
			isActive ?
				"project-item-header project-item-header-active"
			:	"project-item-header"

		header.innerHTML = `
            <div>
                <div>
                    <span style="background-color: ${project.color}"></span>
                    <span>${project.name}</span>
                </div>
                <span>${formatPathForUser(project.path)}</span>
            </div>
            <div class="action-btns">
                <button class="open-btn" title="Open in Finder">📁</button>
                <button class="delete-btn" title="Remove Project">✕</button>
            </div>
        `

		// Swap project click
		header.addEventListener("click", (e) => {
			const target = e.target as HTMLElement

			// Delete project
			if (target.classList.contains("delete-btn")) {
				e.stopPropagation()
				projects = projects.filter((p) => p.path !== project.path)
				saveProjects()
				invoke("close_project_session", {
					projectPath: project.path,
				}).catch((err) => {
					console.error("Failed to close project session in Rust:", err)
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
				target.classList.contains("open-btn") ||
				target.parentElement?.classList.contains("open-btn")
			) {
				e.stopPropagation()
				invoke("open_path", { path: project.path }).catch(console.error)
				return
			}

			switchToProject(project.path)
		})

		// Show buttons on hover
		header.addEventListener("mouseenter", () => {
			const btns = header.querySelector(".action-btns") as HTMLElement
			if (btns) {
				btns.style.opacity = "1"
				const delBtn = btns.querySelector(".delete-btn") as HTMLElement
				if (delBtn && project.path === "/Users/matt/projects/ai-os") {
					delBtn.style.display = "none"
				}
			}
		})
		header.addEventListener("mouseleave", () => {
			const btns = header.querySelector(".action-btns") as HTMLElement
			if (btns) btns.style.opacity = "0"
		})

		item.appendChild(header)

		if (isActive) {
			const threadsContainer = document.createElement("div")
			threadsContainer.className = "thread-history-container"

			const threadsHeader = document.createElement("div")
			threadsHeader.className = "thread-history-header"
			threadsHeader.innerHTML = `
                <span>Threads</span>
                <button class="new-thread-btn" title="Start New Thread">+</button>
            `

			const threadsList = document.createElement("div")
			threadsList.id = "project-threads-list"
			threadsList.className = "thread-history-list"
			initOS(threadsList)
			const threadsScrollEl = getScrollEl(threadsList) || threadsList
			const threadsContentEl = getContentEl(threadsList) || threadsList
			threadsContentEl.innerHTML = '<div class="threads-loading">Loading...</div>'

			threadsScrollEl.addEventListener("scroll", () => {
				if (
					threadsScrollEl.scrollTop + threadsScrollEl.clientHeight >=
					threadsScrollEl.scrollHeight - 20
				) {
					maxVisibleThreads += 15
					renderProjectThreads(activeProject, false)
				}
			})

			threadsContainer.appendChild(threadsHeader)
			threadsContainer.appendChild(threadsList)
			item.appendChild(threadsContainer)

			// Attach event listener for the "+" button to start a new thread
			const newThreadBtn = threadsHeader.querySelector(".new-thread-btn")
			newThreadBtn?.addEventListener("click", async (e) => {
				e.stopPropagation()
				const existingPlaceholder = threadsList.querySelector(
					".new-thread-placeholder",
				) as HTMLElement
				if (existingPlaceholder) {
					existingPlaceholder.click()
					const textarea = document.getElementById(
						"prompt-entry-textarea",
					) as HTMLTextAreaElement | null
					textarea?.focus()
					return
				}

				let existingIds = new Set<string>()
				try {
					const currentThreads = await invoke<ThreadLog[]>(
						"get_project_threads",
						{ projectPath: activeProject },
					)
					existingIds = new Set(currentThreads.map((t) => t.id))
				} catch (err) {
					console.error(
						"Failed to get current threads on new thread click:",
						err,
					)
					existingIds = new Set(Array.from(threadFilepaths.keys()))
				}

				waitingExistingThreadIds = existingIds
				isWaitingForNewThread = true
				setupNewThreadUI()
				renderThreadNotesSidebar(activeProject, activeThreadId)
				updatePlaceholder(true)

				threadsContentEl.querySelectorAll(":scope > div").forEach((child) => {
					child.className = "thread-history-item group"
				})

				const loadingMsg = threadsContentEl.querySelector(".italic")
				if (loadingMsg && loadingMsg.textContent?.includes("Loading")) {
					loadingMsg.remove()
				}

				const placeholderEl = document.createElement("div")
				placeholderEl.className = "thread-history-item active group"
				placeholderEl.innerHTML = `
                <div class="thread-info">
                    <div class="thread-header">
                        <span class="thread-date">Just now</span>
                    </div>
                    <div class="thread-title" title="New Thread">New Thread</div>
                    <div class="thread-snippet" title="Starting...">Starting...</div>
                </div>
                `
				threadsContentEl.prepend(placeholderEl)

				placeholderEl.addEventListener("click", (e) => {
					e.stopPropagation()
					isWaitingForNewThread = true
					threadsContentEl.querySelectorAll(":scope > div").forEach((child) => {
						child.className = "thread-history-item-alt group"
					})
					placeholderEl.className = "thread-history-item active group"
					setupNewThreadUI()
				})

				const previewPane = document.getElementById("markdown-preview-pane")
				if (previewPane) {
					const contentEl = getContentEl(previewPane)
					if (contentEl) {
						contentEl.innerHTML =
							'<div class="select-prompt">Select a thread or log file to view preview...</div>'
					}
				}

				await selectAgyEngine()
				invoke("write_to_pty", {
					data: "/clear\r",
					projectPath: activeProject,
					terminalType: "agy",
				})
				textarea?.focus()
			})
		}

		const contentEl = getContentEl(projectsListEl) || projectsListEl;
		contentEl.appendChild(item)
	})
}

// Switch active project workspace
const switchToProject = async (
	path: string,
	autoSelectFirstThread: boolean = false,
) => {
	// Save draft and engine setting of the current project before switching
	const currentProj = projects.find((p) => p.path === activeProject)
	if (currentProj) {
		currentProj.promptDraft = textarea ? textarea.value : ""
		currentProj.engine = currentEngine
		currentProj.isTerminalMode = isTerminalMode
	}

	activeProject = path
	maxVisibleThreads = 15
	activeThreadId = null
	activeThreadContext = null
	isWaitingForNewThread = false
	waitingExistingThreadIds.clear()
	lastThreadsJson = ""
	lastRenderedThreadId = ""
	lastRenderedThreadLog = ""
	lastRenderedThinking = false

	// Update lastActive timestamp & restore state
	const nextProj = projects.find((p) => p.path === path)
	if (nextProj) {
		nextProj.lastActive = Date.now()
		if (textarea) {
			// Restore draft from localStorage first
			const savedDraft = localStorage.getItem(`ai-os-prompt-draft-${path}`)
			if (savedDraft !== null) {
				textarea.value = savedDraft
				adjustHeight()
			} else {
				textarea.value = nextProj.promptDraft || ""
				adjustHeight()
			}

			// Restore draft from physical disk asynchronously
			invoke<string>("load_prompt_draft", { projectPath: path })
				.then((diskDraft) => {
					if (diskDraft && diskDraft !== textarea.value) {
						textarea.value = diskDraft
						adjustHeight()
						localStorage.setItem(`ai-os-prompt-draft-${path}`, diskDraft)
					}
				})
				.catch(console.error)
		}
		const prevEngine = currentEngine
		if (nextProj.engine) {
			currentEngine = nextProj.engine
			const radio = document.querySelector(
				`input[name="engine"][value="${nextProj.engine}"]`,
			) as HTMLInputElement
			if (radio) {
				radio.checked = true
			}
		}
		syncEngineUI(prevEngine)
		isTerminalMode = !!nextProj.isTerminalMode
		applyTerminalModeUI()
		saveProjects()
	}

	// Clear terminal screens and dump cached history
	term.reset()
	const activeBuffers =
		currentEngine === "claude"
			? claudeBuffers
			: currentEngine === "hermes"
				? hermesBuffers
				: agyBuffers
	if (activeBuffers[path]) {
		term.write(activeBuffers[path])
	} else {
		term.write(
			`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(path)}...\x1b[0m\r\n`,
		)
	}

	miniTerm.reset()
	if (miniTermBuffers[path]) {
		miniTerm.write(miniTermBuffers[path])
	} else {
		miniTerm.write(
			`\r\n\x1b[1;32m[ai-os] Connecting to Shell session at: ${formatPathForUser(path)}...\x1b[0m\r\n`,
		)
	}

	if (currentDirPathEl) {
		currentDirPathEl.textContent = formatPathForUser(path)
	}

	commandHistory = loadCommandHistory(path)
	historyIndex = -1
	currentDraft = ""

	// Reset pause state for the active project
	updatePauseUI("Running")

	// Request Rust backend to load/switch the project shell session
	try {
		await invoke<{ shell_pid: number; is_new_session: boolean }>(
			"switch_active_project",
			{ projectPath: path, engine: currentEngine },
		)

		// PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
	} catch (e) {
		console.error("Failed to switch session in Rust:", e)
	}

	// Restore or initialize PTY geometry sync
	resizePty()
	// Let's also do a delayed resizePty to make sure the backend registers the dimensions after PTY connection is fully active/negotiated.
	setTimeout(() => {
		resizePty()
	}, 100)
	setTimeout(() => {
		resizePty()
	}, 300)
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
		const allThreads = await invoke<ThreadLog[]>("get_all_agy_threads")
		let projectsModified = false

		for (const thread of allThreads) {
			let targetPath = thread.detected_project_path

			// If the thread is a lone agy thread without a detected project path
			if (!targetPath) {
				targetPath = `/Users/matt/projects/Misc`
			}

			// Strip trailing markdown symbols
			while (targetPath.length > 0 && /[`*.,:;)}"\]]$/.test(targetPath)) {
				targetPath = targetPath.slice(0, -1)
			}

			if (targetPath.includes("/Users/matthewmurphy")) {
				continue
			}

			// Check if a project with this path already exists
			const exists = projects.some((p) => p.path === targetPath)
			if (!exists) {
				// Determine a name for the new project
				let name = ""
				if (targetPath === "/Users/matt/projects/Misc") {
					name = "Misc"
				} else if (thread.detected_project_path) {
					name = thread.detected_project_path.split("/").pop() || "Unnamed"
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
					lastActive: thread.mtime > 0 ? thread.mtime * 1000 : Date.now(),
					engine: "agy",
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
		console.error("Failed to sync projects from all threads:", err)
	}
}

const selectAgyEngine = async () => {
	if (currentEngine !== "agy") {
		currentEngine = "agy"
		const currentProj = projects.find((p) => p.path === activeProject)
		if (currentProj) {
			currentProj.engine = "agy"
			saveProjects()
		}

		const agyRadio = document.querySelector(
			'input[name="engine"][value="agy"]',
		) as HTMLInputElement
		if (agyRadio) agyRadio.checked = true

		term.reset()
		if (agyBuffers[activeProject]) {
			term.write(agyBuffers[activeProject])
		} else {
			term.write(
				`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(activeProject)}...\x1b[0m\r\n`,
			)
		}

		try {
			await invoke<{ shell_pid: number; is_new_session: boolean }>(
				"switch_active_project",
				{
					projectPath: activeProject,
					engine: "agy",
				},
			)
		} catch (err) {
			console.error("Failed to toggle engine session on backend:", err)
		}
		resizePty()
	}
}

function getCompactifiedContext(jsonlContent: string): string {
	const lines = jsonlContent.trim().split("\n")
	const steps: string[] = []
	let stepCount = 0

	for (const line of lines) {
		if (!line.trim()) continue
		try {
			const step = JSON.parse(line)
			const source = step.source
			const type = step.type
			const content = step.content

			if (type === "USER_INPUT" && content) {
				stepCount++
				let prompt = content

				prompt = prompt
					.replace(/<SYSTEM_INSTRUCTIONS>[\s\S]*?<\/SYSTEM_INSTRUCTIONS>/gi, "")
					.trim()
				prompt = prompt
					.replace(/<ADDITIONAL_METADATA>[\s\S]*?<\/ADDITIONAL_METADATA>/gi, "")
					.trim()
				prompt = prompt
					.replace(
						/<USER_SETTINGS_CHANGE>[\s\S]*?<\/USER_SETTINGS_CHANGE>/gi,
						"",
					)
					.trim()
				prompt = prompt
					.replace(/<user_rules>[\s\S]*?<\/user_rules>/gi, "")
					.trim()
				prompt = prompt
					.replace(/<ephemeral_message>[\s\S]*?<\/ephemeral_message>/gi, "")
					.trim()
				prompt = prompt.replace(/\[SYSTEM DIRECTIVE:[\s\S]*?\]\n*/g, "").trim()

				const convHistoryMarker = "# Conversation History\n"
				const convHistoryIdx = prompt.indexOf(convHistoryMarker)
				if (convHistoryIdx !== -1) {
					prompt = prompt.substring(0, convHistoryIdx).trim()
				}

				const startTag = "<USER_REQUEST>"
				const endTag = "</USER_REQUEST>"
				const startIdx = prompt.indexOf(startTag)
				const endIdx = prompt.indexOf(endTag)
				if (startIdx !== -1 && endIdx !== -1) {
					prompt = prompt.substring(startIdx + startTag.length, endIdx).trim()
				}

				// Extract actual user request if combined with historical context
				const userRequestMarker = "User request:"
				const markerIdx = prompt.lastIndexOf(userRequestMarker)
				if (markerIdx !== -1) {
					prompt = prompt.substring(markerIdx + userRequestMarker.length).trim()
				}

				prompt = prompt.trim()
				if (prompt.length > 2500) {
					prompt = prompt.substring(0, 2500) + "\n... [truncated]"
				}

				steps.push(`- User Step ${stepCount}: "${prompt}"`)
			} else if (source === "MODEL" && type === "PLANNER_RESPONSE" && content) {
				let reply = content.trim()
				if (reply.length > 2500) {
					reply = reply.substring(0, 2500) + "\n... [truncated]"
				}

				steps.push(`- Assistant: "${reply}"`)
			}
		} catch (e) {
			// Ignore
		}
	}

	const maxSteps = 15
	const slicedSteps = steps.length > maxSteps ? steps.slice(-maxSteps) : steps
	return slicedSteps.join("\n") + "\n"
}

const selectAndLoadThread = async (thread: any) => {
	activeThreadId = thread.id
	renderThreadNotesSidebar(activeProject, activeThreadId)
	await selectAgyEngine()

	const previewPane = document.getElementById("markdown-preview-pane")
	try {
		const content = await invoke<string>("read_thread_log", {
			filepath: thread.filepath,
		})
		activeThreadContext = getCompactifiedContext(content)
		updatePlaceholder(true)

		const isRunning = await invoke<boolean>("is_engine_running", {
			engine: "agy",
			projectPath: activeProject,
			threadId: thread.id,
		})
		lastRenderedThinking = isRunning

		if (previewPane) {
			renderCustomTuiLog(content, true, isRunning)
		}
	} catch (err) {
		if (previewPane) {
			const contentEl = getContentEl(previewPane)
			if (contentEl) {
				contentEl.innerHTML = `<div class="error-msg">Error loading thread log file: ${err}</div>`
			}
		}
	}

	try {
		const res = await invoke<{
			shell_pid: number
			is_new_session: boolean
		}>("switch_active_project", {
			projectPath: activeProject,
			engine: "agy",
		})
		if (res.is_new_session) {
			await new Promise((resolve) => setTimeout(resolve, 800))
		}
	} catch (err) {
		console.error("Failed to toggle engine session on backend:", err)
	}
	invoke("write_to_pty", {
		data: `\x15/resume ${thread.latest_leaf_id}\r`,
		projectPath: activeProject,
		terminalType: "agy",
	})

	// Update active state in UI lists
	const listEl = document.getElementById("project-threads-list")
	if (listEl) {
		const contentEl = getContentEl(listEl) || listEl
		contentEl.querySelectorAll(":scope > div").forEach((child) => {
			child.className = "thread-history-item group"
		})
		const activeProjectItem = Array.from(contentEl.querySelectorAll(":scope > div")).find(
			(child: any) => child.querySelector(".thread-title")?.getAttribute("title") === thread.title
		)
		if (activeProjectItem) {
			activeProjectItem.className = "thread-history-item active group"
		}
	}

	document.querySelectorAll(".search-result-thread-item").forEach((child) => {
		child.classList.remove("active")
	})
	const activeSearchItem = Array.from(document.querySelectorAll(".search-result-thread-item")).find(
		(child: any) => child.querySelector(".search-result-title")?.textContent === thread.title
	)
	if (activeSearchItem) {
		activeSearchItem.classList.add("active")
	}
}

const renderProjectThreads = async (
	projectPath: string,
	autoSelectFirstThread: boolean = false,
	preFetchedThreads?: ThreadLog[],
) => {
	const listEl = document.getElementById("project-threads-list")
	if (!listEl) return

	try {
		const threads =
			preFetchedThreads ||
			(await invoke<ThreadLog[]>("get_project_threads", {
				projectPath,
			}))
		const scrollEl = getScrollEl(listEl) || listEl
		const contentEl = getContentEl(listEl) || listEl
		const prevScrollTop = scrollEl.scrollTop
		contentEl.innerHTML = ""

		const threadsToShow = threads.slice(0, maxVisibleThreads)

		if (threadsToShow.length === 0) {
			contentEl.innerHTML = '<div class="no-threads">No threads found for this project</div>'
			return
		}

		threadsToShow.forEach((thread) => {
			threadFilepaths.set(thread.id, thread.filepath)
			threadLatestLeafIds.set(thread.id, thread.latest_leaf_id)
			const el = document.createElement("div")
			const isActive = activeThreadId === thread.id
			el.className =
				isActive ?
					"thread-history-item active group"
				:	"thread-history-item group"

			const ts = thread.mtime > 0 ? thread.mtime * 1000 : Date.now()
			const dateStr = getRelativeDateStr(ts)
			const fullDateStr = getFullDateStr(ts)

			el.innerHTML = `
                <div class="thread-info">
                    <div class="thread-title" title="${thread.title}">${thread.title}</div>
                    <div class="thread-snippet" title="${thread.snippet}">${thread.snippet}</div>
                </div>
                <div class="thread-date" title="${fullDateStr}">${dateStr}</div>
                <button class="delete-thread-btn" title="Delete Thread">✕</button>
            `

			const delBtn = el.querySelector(".delete-thread-btn")
			if (delBtn) {
				delBtn.addEventListener("click", async (e) => {
					e.stopPropagation()
					try {
						await invoke("delete_thread", { id: thread.id })
						if (activeThreadId === thread.id) {
							activeThreadId = null
							activeThreadContext = null
							updatePlaceholder(true)
							const previewPane = document.getElementById(
								"markdown-preview-pane",
							)
							if (previewPane) {
								const contentEl = getContentEl(previewPane)
								if (contentEl) {
									contentEl.innerHTML =
										'<div class="select-prompt">Select a thread or log file to view preview...</div>'
								}
							}
						}
						pollThreadsList()
					} catch (err) {
						console.error("Failed to delete thread:", err)
					}
				})
			}

			el.addEventListener("click", () => {
				selectAndLoadThread(thread)
			})


			contentEl.appendChild(el)
		})

		if (autoSelectFirstThread) {
			const firstChild = contentEl.querySelector(":scope > div") as HTMLElement
			if (firstChild) {
				firstChild.click()
			}
		}

		scrollEl.scrollTop = prevScrollTop
	} catch (err) {
		console.error("Failed to load project threads:", err)
		const contentEl = getContentEl(listEl) || listEl
		contentEl.innerHTML = `<div class="error-msg">Error: ${err}</div>`
	}
}

const pollThreadsList = async () => {
	if (!activeProject) return
	try {
		const threads = await invoke<ThreadLog[]>("get_project_threads", {
			projectPath: activeProject,
		})
		const threadsJson = JSON.stringify(threads)

		// If we are waiting for a new thread to be created, and one is found
		if (isWaitingForNewThread && threads.length > 0) {
			const newestThread = threads[0]
			if (!waitingExistingThreadIds.has(newestThread.id)) {
				activeThreadId = newestThread.id
				renderThreadNotesSidebar(activeProject, activeThreadId)
				isWaitingForNewThread = false
				waitingExistingThreadIds.clear()

				activeThreadContext = ""
				updatePlaceholder(true)

				lastThreadsJson = threadsJson
				await renderProjectThreads(activeProject, false, threads)

				const filepath = newestThread.filepath
				if (filepath) {
					const content = await invoke<string>("read_thread_log", {
						filepath,
					})
					activeThreadContext = getCompactifiedContext(content)
					lastRenderedThinking = true
					renderCustomTuiLog(content, false, true)
				}
				return
			}
		}

		if (threadsJson !== lastThreadsJson) {
			lastThreadsJson = threadsJson
			await renderProjectThreads(activeProject, false, threads)
		}
	} catch (err) {
		console.error("Failed in pollThreadsList:", err)
	}
}

// Start the polling interval
setInterval(pollThreadsList, 1000)

// Add project modal and logic
const addProjectModal = document.getElementById("add-project-modal")
const closeModalBtn = document.getElementById("close-modal-btn")
const btnChoiceExisting = document.getElementById("btn-choice-existing")
const btnChoiceNew = document.getElementById("btn-choice-new")
const newProjectForm = document.getElementById("new-project-form")
const newProjNameInput = document.getElementById(
	"new-proj-name",
) as HTMLInputElement
const newProjGitInput = document.getElementById(
	"new-proj-git",
) as HTMLInputElement
const btnSubmitNewProject = document.getElementById(
	"btn-submit-new-project",
) as HTMLButtonElement

const openModal = () => {
	if (!addProjectModal) return
	addProjectModal.classList.remove("hidden")
	// Force browser reflow to trigger CSS transitions
	addProjectModal.offsetHeight
	addProjectModal.classList.remove("opacity-0")
	addProjectModal.classList.add("opacity-100")

	const modalContent = addProjectModal.querySelector(".transform")
	if (modalContent) {
		modalContent.classList.remove("scale-95")
		modalContent.classList.add("scale-100")
	}

	// Reset modal state
	if (newProjectForm) newProjectForm.classList.add("hidden")
	if (newProjNameInput) newProjNameInput.value = ""
	if (newProjGitInput) newProjGitInput.value = ""
}

const closeModal = () => {
	if (!addProjectModal) return
	addProjectModal.classList.remove("opacity-100")
	addProjectModal.classList.add("opacity-0")

	const modalContent = addProjectModal.querySelector(".transform")
	if (modalContent) {
		modalContent.classList.remove("scale-100")
		modalContent.classList.add("scale-95")
	}

	// Hide modal element after transition completes
	setTimeout(() => {
		addProjectModal.classList.add("hidden")
	}, 300)
}

// Toggle modal visibility
const addProjectBtn = document.getElementById("add-project-btn")
addProjectBtn?.addEventListener("click", openModal)
closeModalBtn?.addEventListener("click", closeModal)

// Close modal when clicking on the backdrop (outside modal content)
addProjectModal?.addEventListener("click", (e) => {
	if (e.target === addProjectModal) {
		closeModal()
	}
})

// Helper to choose random color for project card
const getRandomProjectColor = () => {
	const colors = [
		"#3b82f6",
		"#ec4899",
		"#10b981",
		"#f59e0b",
		"#8b5cf6",
		"#ef4444",
		"#06b6d4",
		"#6366f1",
		"#14b8a6",
		"#a855f7",
	]
	return colors[Math.floor(Math.random() * colors.length)]
}

// Open Existing Project via File Picker
btnChoiceExisting?.addEventListener("click", async () => {
	try {
		const selectedDir = await invoke<string | null>("select_directory")
		if (!selectedDir) return // User canceled the dialog

		const cleanPath = selectedDir.trim()
		const name = cleanPath.split("/").pop() || "unknown-project"

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
			engine: "agy",
			isTerminalMode: false,
		}

		projects.push(newProj)
		saveProjects()
		switchToProject(cleanPath)
		closeModal()
	} catch (err) {
		alert("Failed to select directory: " + err)
	}
})

// Show New Project Form
btnChoiceNew?.addEventListener("click", () => {
	if (newProjectForm) {
		newProjectForm.classList.remove("hidden")
		newProjNameInput?.focus()
	}
})

// Auto-generate git repository name from project name
newProjNameInput?.addEventListener("input", () => {
	if (newProjGitInput) {
		// Convert to kebab-case
		const kebab = newProjNameInput.value
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/(^-|-$)/g, "")
		newProjGitInput.value = kebab
	}
})

// Create & Initialize New Project
btnSubmitNewProject?.addEventListener("click", async () => {
	const name = newProjNameInput.value.trim()
	const gitRepoName = newProjGitInput.value.trim()

	if (!name) {
		alert("Please enter a project name.")
		return
	}
	if (!gitRepoName) {
		alert("Please enter a git repository name.")
		return
	}

	// Disable submit button and show loading state
	const originalText = btnSubmitNewProject.innerHTML
	btnSubmitNewProject.disabled = true
	btnSubmitNewProject.innerHTML = `<span class=">🔄</span> Creating...`

	try {
		const projectPath = await invoke<string>("create_new_project", {
			name,
			gitRepoName,
		})

		const newProj: Project = {
			path: projectPath,
			name,
			color: getRandomProjectColor(),
			lastActive: Date.now(),
			engine: "agy",
			isTerminalMode: false,
		}

		projects.push(newProj)
		saveProjects()
		switchToProject(projectPath)
		closeModal()
	} catch (err) {
		alert("Failed to create project: " + err)
	} finally {
		btnSubmitNewProject.disabled = false
		btnSubmitNewProject.innerHTML = originalText
	}
})

// ----------------------------------------------------
// 7. Engine Toggle & Routing
// ----------------------------------------------------
let currentEngine: "claude" | "agy" | "hermes" = "agy"

// Hermes WebSocket Chat Client
const hermesChat = new HermesChatClient()
let hermesCurrentMessageId: string | null = null

function initHermesChat(cwd?: string): Promise<void> {
	if (hermesChat.connectionState === "connected" && hermesChat.sessionId && hermesChat.cwd === cwd) {
		return Promise.resolve()
	}
	let prep = Promise.resolve()
	if (hermesChat.sessionId && hermesChat.cwd !== cwd) {
		prep = hermesChat.closeSession().catch(() => {})
	}
	return prep
		.then(() => invoke("ensure_hermes_running"))
		.then(() => hermesChat.connect())
		.then(() => {
			if (!hermesChat.sessionId) {
				return hermesChat.createSession(cwd)
			}
		})
}

function setupNewThreadUI() {
	activeThreadId = null
	activeThreadContext = null
	lastRenderedThreadId = ""
	lastRenderedThreadLog = ""
	lastRenderedThinking = false

	// 1. Clear terminal PTY screen
	term.reset()
	term.write("\r\n\x1b[1;32m[ai-os] Ready for new thread. Type a prompt to begin...\x1b[0m\r\n")

	// 2. Clear Markdown preview pane if present
	const previewPane = document.getElementById("markdown-preview-pane")
	if (previewPane) {
		const contentEl = getContentEl(previewPane)
		if (contentEl) {
			contentEl.innerHTML = '<div class="select-prompt">Select a thread or log file to view preview...</div>'
		}
	}

	// 3. Clear Hermes messages container
	const msgsEl = document.getElementById("hermes-messages")
	if (msgsEl) {
		msgsEl.innerHTML = `<div class="hermes-welcome">
			<h3>Welcome to Hermes Chat</h3>
			<p>Type a prompt below to begin your conversation.</p>
		</div>`
	}

	// 4. Close and re-init Hermes session if current engine is hermes
	if (currentEngine === "hermes") {
		hermesChat.closeSession().catch(() => {}).then(() => {
			return initHermesChat(activeProject)
		}).catch(err => {
			console.error("Failed to start fresh Hermes session for new thread:", err)
		})
	}
}

function showHermesChatUI(show: boolean) {
	const termContainer = document.getElementById("terminal-container")
	const chatContainer = document.getElementById("hermes-chat-container")
	if (termContainer) termContainer.style.display = show ? "none" : ""
	if (chatContainer) chatContainer.style.display = show ? "" : "none"
}

function appendHermesUserMessage(text: string) {
	const msgsEl = document.getElementById("hermes-messages")
	if (!msgsEl) return
	// Remove welcome
	const welcome = msgsEl.querySelector(".hermes-welcome")
	if (welcome) welcome.remove()

	const div = document.createElement("div")
	div.className = "hermes-message hermes-message-user"
	div.innerHTML = `<div class="hermes-message-role">You</div><div class="hermes-message-content">${escapeHtml(text)}</div>`
	msgsEl.appendChild(div)
	msgsEl.scrollTop = msgsEl.scrollHeight
}

function updateHermesMessageContent(msgId: string, text: string) {
	const el = document.getElementById(msgId)
	if (!el) return
	const content = el.querySelector(".hermes-message-content")
	if (content) {
		const cursor = content.querySelector(".hermes-streaming-cursor")
		if (cursor) cursor.remove()
		content.textContent = text
		content.appendChild(Object.assign(document.createElement("span"), { className: "hermes-streaming-cursor" }))
	}
	const msgsEl = document.getElementById("hermes-messages")
	if (msgsEl) msgsEl.scrollTop = msgsEl.scrollHeight
}

function finalizeHermesMessage(msgId: string) {
	const el = document.getElementById(msgId)
	if (!el) return
	const cursor = el.querySelector(".hermes-streaming-cursor")
	if (cursor) cursor.remove()
}

function addHermesThinkingBlock(msgId: string, text: string) {
	const el = document.getElementById(msgId)
	if (!el) return
	let block = el.querySelector(".hermes-thinking-block") as HTMLElement | null
	if (!block) {
		const newBlock = document.createElement("div")
		newBlock.className = "hermes-thinking-block"
		newBlock.innerHTML = `<div class="hermes-thinking-header">💭 Thinking</div><div class="hermes-thinking-body"></div>`
		newBlock.addEventListener("click", () => newBlock.classList.toggle("expanded"))
		el.appendChild(newBlock)
		block = newBlock
	}
	const body = block.querySelector(".hermes-thinking-body")
	if (body) body.textContent += text
}

function addHermesToolCall(msgId: string, toolId: string, name: string) {
	const el = document.getElementById(msgId)
	if (!el) return
	// Remove previous tool's cursor
	const prevRunning = el.querySelector(".hermes-tool-call.running")
	if (prevRunning) prevRunning.classList.remove("running")

	const div = document.createElement("div")
	div.className = "hermes-tool-call running"
	div.id = "tool-" + toolId
	div.innerHTML = `<div class="hermes-tool-name">🔧 ${escapeHtml(name)}</div><div class="hermes-tool-status">Running...</div>`
	el.appendChild(div)
}

function completeHermesToolCall(msgId: string, toolId: string, _name: string, result: string) {
	const el = document.getElementById("tool-" + toolId) || document.getElementById(msgId)?.querySelector(".hermes-tool-call.running:last-child")
	if (!el) return
	el.classList.remove("running")
	el.classList.add("complete")
	const statusEl = el.querySelector(".hermes-tool-status")
	if (statusEl) statusEl.textContent = "✓ Complete"
	// Add expandable result
	const resultEl = document.createElement("div")
	resultEl.className = "hermes-tool-result"
	resultEl.textContent = result.length > 500 ? result.substring(0, 500) + "..." : result
	resultEl.addEventListener("click", () => resultEl.classList.toggle("visible"))
	el.appendChild(resultEl)
}

function addHermesError(msg: string) {
	const msgsEl = document.getElementById("hermes-messages")
	if (!msgsEl) return
	const div = document.createElement("div")
	div.className = "hermes-error"
	div.textContent = "⚠ " + msg
	msgsEl.appendChild(div)
	msgsEl.scrollTop = msgsEl.scrollHeight
}

function escapeHtml(text: string): string {
	return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}

function syncEngineUI(prevEngine?: string) {
	if (currentEngine === "hermes") {
		showHermesChatUI(true)
		initHermesChat(activeProject).catch(err => {
			console.error("Failed to auto-init Hermes chat:", err)
		})
		hermesChat.onMessageStart = (msgId) => {
			hermesCurrentMessageId = msgId
			const msgsEl = document.getElementById("hermes-messages")
			if (!msgsEl) return
			const welcome = msgsEl.querySelector(".hermes-welcome")
			if (welcome) welcome.remove()
			const div = document.createElement("div")
			div.className = "hermes-message hermes-message-assistant"
			div.id = msgId
			div.innerHTML = `<div class="hermes-message-role">Hermes</div><div class="hermes-message-content"><span class="hermes-streaming-cursor"></span></div>`
			msgsEl.appendChild(div)
			msgsEl.scrollTop = msgsEl.scrollHeight
		}
		hermesChat.onMessageDelta = (_msgId, text) => {
			if (hermesCurrentMessageId) updateHermesMessageContent(hermesCurrentMessageId, text)
		}
		hermesChat.onMessageComplete = (_msgId) => {
			if (hermesCurrentMessageId) finalizeHermesMessage(hermesCurrentMessageId)
			hermesCurrentMessageId = null
		}
		hermesChat.onThinkingDelta = (_msgId, text) => {
			if (hermesCurrentMessageId) addHermesThinkingBlock(hermesCurrentMessageId, text)
		}
		hermesChat.onToolStart = (_msgId, toolId, name) => {
			if (hermesCurrentMessageId) addHermesToolCall(hermesCurrentMessageId, toolId, name)
		}
		hermesChat.onToolComplete = (_msgId, toolId, name, result) => {
			if (hermesCurrentMessageId) completeHermesToolCall(hermesCurrentMessageId, toolId, name, result)
		}
		hermesChat.onError = (msg) => {
			addHermesError(msg)
		}
	} else {
		showHermesChatUI(false)
		if (prevEngine === "hermes") {
			hermesChat.closeSession().catch(() => {})
			hermesChat.disconnect()
		}
	}
}

const engineRadios = document.querySelectorAll<HTMLInputElement>(
	'input[name="engine"]',
)

engineRadios.forEach((radio) => {
	radio.addEventListener("change", async (e) => {
		const prevEngine = currentEngine
		currentEngine = (e.target as HTMLInputElement).value as "claude" | "agy" | "hermes"
		// Persist setting on the active project
		const currentProj = projects.find((p) => p.path === activeProject)
		if (currentProj) {
			currentProj.engine = currentEngine
			saveProjects()
		}

		syncEngineUI(prevEngine)

		// Reset terminal screen and show matching engine buffer (only for non-hermes)
		term.reset()
		const activeBuffers =
			currentEngine === "claude"
				? claudeBuffers
				: currentEngine === "hermes"
					? hermesBuffers
					: agyBuffers
		if (activeBuffers[activeProject]) {
			term.write(activeBuffers[activeProject])
		} else {
			term.write(
				`\r\n\x1b[1;34m[ai-os] Connecting to Engine session at: ${formatPathForUser(activeProject)}...\x1b[0m\r\n`,
			)
		}

		try {
			// Lazy spawn or switch to the engine on backend
			await invoke<{ shell_pid: number; is_new_session: boolean; hermes_ws_port: number }>(
				"switch_active_project",
				{
					projectPath: activeProject,
					engine: currentEngine,
				},
			)

			// PTY auto-spawn is now handled directly by the backend to bypass zsh rc files and launch instantly
		} catch (err) {
			console.error("Failed to toggle engine session on backend:", err)
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
		textarea.style.height = "auto"
		const newHeight = textarea.scrollHeight
		textarea.style.height = newHeight + "px"
		if (newHeight !== lastTextareaHeight) {
			lastTextareaHeight = newHeight
			debouncedResizePty()
		}
	}
}

textarea?.addEventListener("input", () => {
	savePromptDraft(textarea.value)
	// Instantly toggle to terminal mode when user types exactly "!" in empty field
	if (textarea.value === "!") {
		isTerminalMode = true
		const currentProj = projects.find((p) => p.path === activeProject)
		if (currentProj) {
			currentProj.isTerminalMode = true
			saveProjects()
		}
		applyTerminalModeUI()
		textarea.value = ""
		adjustHeight()
	} else {
		adjustHeight()

		// Removed flawed auto-expand logic for slash commands in textarea
	}
})
const loadCommandHistory = (projectPath: string): string[] => {
	try {
		const historyJson = localStorage.getItem(`ai-os-history-${projectPath}`)
		if (historyJson) {
			return JSON.parse(historyJson)
		}
	} catch (e) {
		console.error("Failed to load command history", e)
	}
	return []
}

const saveCommandHistory = (projectPath: string, history: string[]) => {
	try {
		localStorage.setItem(
			`ai-os-history-${projectPath}`,
			JSON.stringify(history),
		)
	} catch (e) {
		console.error("Failed to save command history", e)
	}
}

let commandHistory: string[] = loadCommandHistory(activeProject)
let historyIndex = -1
let currentDraft = ""

let arrowUpPressedOnce = false
let arrowUpTimeout: any = null
let arrowUpOverlay: HTMLDivElement | null = null

const showArrowUpOverlay = () => {
	if (!arrowUpOverlay) {
		arrowUpOverlay = document.createElement("div")
		arrowUpOverlay.className = "arrow-up-overlay"
		arrowUpOverlay.textContent = "Press ArrowUp again to recall history"
		const bottomArea = document.getElementById("bottom-input-area")
		if (bottomArea) {
			bottomArea.appendChild(arrowUpOverlay)
		}
	}
	arrowUpOverlay.style.opacity = "1"
}

const hideArrowUpOverlay = () => {
	if (arrowUpOverlay) {
		arrowUpOverlay.style.opacity = "0"
		setTimeout(() => {
			if (arrowUpOverlay && arrowUpOverlay.style.opacity === "0") {
				arrowUpOverlay.remove()
				arrowUpOverlay = null
			}
		}, 300)
	}
}

textarea?.addEventListener("keydown", async (e) => {
	if (e.key === "ArrowUp") {
		if (textarea.selectionStart === 0 || historyIndex !== -1) {
			// If the textarea is empty, we don't need the double tap
			const isEmpty = textarea.value.trim() === ""

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
					textarea.removeEventListener("input", resetArrowUpState)
					textarea.removeEventListener("blur", resetArrowUpState)
				}
				textarea.addEventListener("input", resetArrowUpState)
				textarea.addEventListener("blur", resetArrowUpState)
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
	} else if (e.key === "ArrowDown") {
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
	} else if (e.key === "Enter") {
		if (e.shiftKey) {
			// Shift+Enter: insert a newline at the cursor position explicitly
			e.preventDefault()
			const start = textarea.selectionStart
			const end = textarea.selectionEnd
			const value = textarea.value
			textarea.value = value.substring(0, start) + "\n" + value.substring(end)
			textarea.selectionStart = textarea.selectionEnd = start + 1
			adjustHeight()
			return
		}

		e.preventDefault()

		let rawInput = textarea.value
		const trimmedInput = rawInput.trim()
		if (!trimmedInput) return

		// Clear textarea immediately to keep UI responsive
		textarea.value = ""
		savePromptDraft("")
		adjustHeight()

		if (!activeThreadId) {
			let existingIds = new Set<string>()
			try {
				const currentThreads = await invoke<ThreadLog[]>(
					"get_project_threads",
					{ projectPath: activeProject },
				)
				existingIds = new Set(currentThreads.map((t) => t.id))
			} catch (err) {
				console.error("Failed to get current threads on Enter press:", err)
				existingIds = new Set(Array.from(threadFilepaths.keys()))
			}
			waitingExistingThreadIds = existingIds
			isWaitingForNewThread = true
			lastRenderedThreadId = ""
			lastRenderedThreadLog = ""
			lastRenderedThinking = false
		}

		commandHistory.push(trimmedInput)
		saveCommandHistory(activeProject, commandHistory)
		historyIndex = -1

		const previewPane = document.getElementById("markdown-preview-pane")
		if (previewPane) {
			const contentEl = getContentEl(previewPane) || previewPane
			if (contentEl.innerHTML.includes("Select a thread")) {
				contentEl.innerHTML = ""
			}
			const escapedInput = trimmedInput
				.replace(/&/g, "&amp;")
				.replace(/</g, "&lt;")
				.replace(/>/g, "&gt;")
			const blockHtml = `
            <div class="chat-message user">
                <div class="message-content group">
                    <div class="text-content">${escapedInput}</div>
                </div>
            </div>`
			contentEl.innerHTML += blockHtml
			setTimeout(() => {
				forceScrollToBottom(previewPane)
			}, 10)
		}

		// Prompt Mode Engine Routing Logic
		// Hermes WebSocket path
		if (currentEngine === "hermes") {
			if (hermesChat.connectionState === "connected" && hermesChat.sessionId) {
				// Show user message in Hermes chat
				appendHermesUserMessage(trimmedInput)
				hermesChat.submitPrompt(trimmedInput).catch(console.error)
			} else {
				console.warn("Hermes chat not connected, trying to connect...")
				initHermesChat(activeProject).then(() => {
					appendHermesUserMessage(trimmedInput)
					hermesChat.submitPrompt(trimmedInput).catch(console.error)
				}).catch(err => {
					console.error("Failed to init Hermes chat:", err)
					// Fallback: write to PTY
					invoke("write_to_pty", {
						data: `${trimmedInput}\r`,
						projectPath: activeProject,
						terminalType: "hermes",
					})
				})
			}
			return
		}

		let processedInput = trimmedInput

		if (processedInput.startsWith("/")) {
			let isRunning = false
			try {
				isRunning = await invoke<boolean>("is_engine_running", {
					engine: currentEngine,
					projectPath: activeProject,
				})
			} catch (err) {
				console.error("Failed to check if engine is running:", err)
			}

			if (!isRunning && currentEngine === "agy") {
				try {
					await invoke("switch_active_project", {
						projectPath: activeProject,
						engine: "agy",
					})
					await invoke("spawn_fresh_engine", {
						projectPath: activeProject,
						engine: "agy",
					})
					await new Promise((resolve) => setTimeout(resolve, 3000))
				} catch (err) {
					console.error("Failed to spawn fresh agy engine:", err)
				}
			}

			invoke("write_to_pty", {
				data: `${processedInput}\r`,
				projectPath: activeProject,
				terminalType: currentEngine,
			})

			// Textarea cleared at the start of submit handler

			const clearCheckbox = document.getElementById(
				"clear-context-checkbox",
			) as HTMLInputElement
			if (clearCheckbox) {
				clearCheckbox.checked = true
				autoClearContext = true
				localStorage.setItem("ai-os-auto-clear", "true")
				updatePlaceholder(true)
			}
			return
		}

		// Obsidian Knowledge Routing
		if (processedInput.toLowerCase().includes("notes")) {
			processedInput += `\n\n[SYSTEM DIRECTIVE: Any read/write operations regarding "notes" MUST exclusively target this absolute path: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/]`
		}

		const clearCheckbox = document.getElementById(
			"clear-context-checkbox",
		) as HTMLInputElement
		const shouldClear = clearCheckbox ? clearCheckbox.checked : true

		let isRunning = false
		try {
			isRunning = await invoke<boolean>("is_engine_running", {
				engine: currentEngine,
				projectPath: activeProject,
			})
		} catch (err) {
			console.error("Failed to check if engine is running:", err)
		}

		const isBypass = e.metaKey || e.ctrlKey || e.altKey || !shouldClear

		// Force a fresh engine swap if not bypassing, to guarantee the prompt is processed cleanly.
		if (!isBypass && currentEngine === "agy") {
			isRunning = false
		}

		// Load the latest context dynamically from the thread's log file if inside a thread
		let currentContext = activeThreadContext
		if (activeThreadId && currentEngine === "agy") {
			const filepath = threadFilepaths.get(activeThreadId)
			if (filepath) {
				try {
					const content = await invoke<string>("read_thread_log", {
						filepath,
					})
					currentContext = getCompactifiedContext(content)
				} catch (err) {
					console.error("Failed to load active thread context:", err)
				}
			}
		}

		if (isRunning) {
			if (activeThreadId && currentContext && !isBypass) {
				invoke("write_to_pty", {
					data: "/clear\r",
					projectPath: activeProject,
					terminalType: currentEngine,
				})
				await new Promise((resolve) => setTimeout(resolve, 450))

				const combinedPrompt = `Continuing conversation from history (Thread ID: ${activeThreadId}).\n\n[SYSTEM DIRECTIVE: This is a summary/compacted view of the thread history. If you need to view the full, untruncated details, tool calls, or files from this thread, you can run the following command in the terminal:\n  pnpm run view-thread ${activeThreadId}\nor specifically for a step:\n  pnpm run view-thread ${activeThreadId} --step <index>\n]\n\nHistorical Context:\n${currentContext}\n\nUser request: ${processedInput}`
				const dataToSend = `\x1b[200~${combinedPrompt}\x1b[201~\r`
				invoke("write_to_pty", {
					data: dataToSend,
					projectPath: activeProject,
					terminalType: currentEngine,
				})
			} else {
				const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`
				if (isBypass) {
					invoke("write_to_pty", {
						data: dataToSend,
						projectPath: activeProject,
						terminalType: currentEngine,
					})
				} else {
					invoke("write_to_pty", {
						data: "/clear\r",
						projectPath: activeProject,
						terminalType: currentEngine,
					})
					await new Promise((resolve) => setTimeout(resolve, 450))
					invoke("write_to_pty", {
						data: dataToSend,
						projectPath: activeProject,
						terminalType: currentEngine,
					})
				}
			}
		} else {
			if (currentEngine === "agy") {
				try {
					await invoke("switch_active_project", {
						projectPath: activeProject,
						engine: "agy",
					})
					await invoke("spawn_fresh_engine", {
						projectPath: activeProject,
						engine: "agy",
					})
					await new Promise((resolve) => setTimeout(resolve, 3000))
				} catch (err) {
					console.error("Failed to spawn fresh agy engine:", err)
				}

				if (activeThreadId && currentContext) {
					if (isBypass) {
						const leafId =
							threadLatestLeafIds.get(activeThreadId) || activeThreadId
						invoke("write_to_pty", {
							data: `\x15/resume ${leafId}\r`,
							projectPath: activeProject,
							terminalType: "agy",
						})
						await new Promise((resolve) => setTimeout(resolve, 800))

						invoke("write_to_pty", {
							data: "/clear\r",
							projectPath: activeProject,
							terminalType: "agy",
						})
						await new Promise((resolve) => setTimeout(resolve, 450))

						const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`
						invoke("write_to_pty", {
							data: dataToSend,
							projectPath: activeProject,
							terminalType: "agy",
						})
					} else {
						const combinedPrompt = `Continuing conversation from history (Thread ID: ${activeThreadId}).\n\n[SYSTEM DIRECTIVE: This is a summary/compacted view of the thread history. If you need to view the full, untruncated details, tool calls, or files from this thread, you can run the following command in the terminal:\n  pnpm run view-thread ${activeThreadId}\nor specifically for a step:\n  pnpm run view-thread ${activeThreadId} --step <index>\n]\n\nHistorical Context:\n${currentContext}\n\nUser request: ${processedInput}`
						const dataToSend = `\x1b[200~${combinedPrompt}\x1b[201~\r`
						invoke("write_to_pty", {
							data: dataToSend,
							projectPath: activeProject,
							terminalType: "agy",
						})
					}
				} else {
					const dataToSend = `\x1b[200~${processedInput}\x1b[201~\r`
					invoke("write_to_pty", {
						data: dataToSend,
						projectPath: activeProject,
						terminalType: "agy",
					})
				}
			} else {
				const escapedInput = processedInput.replace(/"/g, '\\"')
				let commandToExecute = ""

				if (currentEngine === "claude") {
					commandToExecute = `claude -p "${escapedInput}"`
				}

				invoke("write_to_pty", {
					data: commandToExecute + "\r",
					projectPath: activeProject,
					terminalType: currentEngine,
				})
			}
		}

		// Textarea cleared at the start of submit handler

		// Auto-clear context toggle turns itself back on after each message is sent
		if (clearCheckbox) {
			clearCheckbox.checked = true
			autoClearContext = true
			localStorage.setItem("ai-os-auto-clear", "true")
			// We poll is_engine_running in the background, but we can optimistically call updatePlaceholder(true) since we just spawned/used it
			updatePlaceholder(true)
		}
	}
})

// Tauri File Drop handling
listen<string[]>("tauri://file-drop", (event) => {
	if (!textarea) return
	const paths = event.payload
	if (paths && paths.length > 0) {
		const textToAppend = paths.join(" ")
		if (textarea.value) {
			textarea.value += " " + textToAppend
		} else {
			textarea.value = textToAppend
		}
		adjustHeight()
	}
})

// ----------------------------------------------------
// 8. Clipboard Copy & Paste for TUI (xterm.js)
// ----------------------------------------------------
document.addEventListener("keydown", (e) => {
	// Intercept Cmd+C (Mac) or Ctrl+C to copy selected text from xterm.js or window
	if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "c") {
		let textToCopy = ""
		const activeEl = document.activeElement

		// Only prioritize xterm.js selections if the terminal elements are focused
		if (
			activeEl &&
			(container?.contains(activeEl) || term.element?.contains(activeEl))
		) {
			if (term.hasSelection()) {
				textToCopy = term.getSelection()
			} else {
				invoke("copy_tmux_selection", {
					projectPath: activeProject,
					terminalType: currentEngine,
				}).catch((err) => {
					console.error("Failed to copy tmux selection:", err)
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
				invoke("copy_tmux_selection", {
					projectPath: activeProject,
					terminalType: "mini",
				}).catch((err) => {
					console.error("Failed to copy tmux selection:", err)
				})
			}
		} else {
			textToCopy = window.getSelection()?.toString() || ""
		}

		if (textToCopy) {
			navigator.clipboard.writeText(textToCopy).catch((err) => {
				console.error("Failed to copy text:", err)
			})
		}
	}
})

document.addEventListener("paste", async (e) => {
	// If user is focused on the prompt input, let default paste happen
	if (document.activeElement === textarea) {
		return
	}
	let pastedText = e.clipboardData?.getData("text")
	if (pastedText) {
		const activeEl = document.activeElement
		const isEngineFocus =
			activeEl &&
			(container?.contains(activeEl) || term.element?.contains(activeEl))

		if (isEngineFocus) {
			let isRunning = false
			try {
				isRunning = await invoke<boolean>("is_engine_running", {
					engine: currentEngine,
					projectPath: activeProject,
				})
			} catch (err) {
				console.error("Failed to check if engine is running:", err)
			}
			if (isRunning) {
				// When pasting directly into an active interactive session, map newlines to Esc+LF (\x1b\n)
				// so the interactive shell buffers the entire pasted block without submitting line-by-line
				pastedText = pastedText.replace(/\r\n/g, "\n").replace(/\n/g, "\x1b\n")
			}
			invoke("write_to_pty", {
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
			if (pastedText.includes("\n")) {
				invoke("write_to_pty", {
					data: "\x1b[200~" + pastedText + "\x1b[201~",
					projectPath: activeProject,
					terminalType: "mini",
				})
			} else {
				invoke("write_to_pty", {
					data: pastedText,
					projectPath: activeProject,
					terminalType: "mini",
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
	"clear-context-checkbox",
) as HTMLInputElement
let autoClearContext = true
const savedAutoClear = localStorage.getItem("ai-os-auto-clear")
if (savedAutoClear !== null) {
	autoClearContext = savedAutoClear === "true"
}

const updatePlaceholder = (isRunning = true) => {
	const contextContainer = document.getElementById("clear-context-container")
	const labelText = document.getElementById("clear-context-label-text")
	if (textarea) {
		if (!isRunning) {
			textarea.placeholder = `Type a prompt... [Will launch ${currentEngine} and send] (Enter to send, Shift+Enter for newline)`
			if (contextContainer) {
				contextContainer.style.display = "none"
			}
		} else {
			if (contextContainer) {
				contextContainer.style.display = "flex"
			}
			if (clearCheckbox && clearCheckbox.checked) {
				textarea.placeholder =
					"Type a prompt... [Runs /clear first] (Enter to send, Shift+Enter for newline)"
				if (contextContainer) {
					contextContainer.className = "context-container-base"
				}
				if (labelText) labelText.textContent = "Auto-Clear: ACTIVE"
			} else {
				textarea.placeholder =
					"Type a prompt... [Continuing thread] (Enter to send, Shift+Enter for newline)"
				if (contextContainer) {
					contextContainer.className = "context-container-active"
				}
				if (labelText) labelText.textContent = "Auto-Clear: OFF"
			}
		}
	}
}

if (clearCheckbox) {
	clearCheckbox.checked = autoClearContext
	clearCheckbox.addEventListener("change", () => {
		autoClearContext = clearCheckbox.checked
		localStorage.setItem("ai-os-auto-clear", String(autoClearContext))
		updatePlaceholder()
	})
	// Call initially
	setTimeout(updatePlaceholder, 100)
}

document.addEventListener("mousedown", (e) => {
	const target = e.target as HTMLElement
	if (target.closest("summary")) {
		e.preventDefault()
	}
})

document.addEventListener("click", (e) => {
	const target = e.target as HTMLElement
	const selection = window.getSelection()

	// Handle summary clicks to prevent browser default toggle scroll-jumping behavior
	const summary = target.closest("summary")
	if (summary) {
		e.preventDefault()
		const details = summary.parentElement as HTMLDetailsElement | null
		if (details) {
			const pane = document.getElementById("markdown-preview-pane")
			const osViewport = getScrollEl(pane)
			const savedHostScroll = pane ? pane.scrollTop : 0
			const savedOsScroll = osViewport ? osViewport.scrollTop : 0

			details.open = !details.open

			if (pane) pane.scrollTop = savedHostScroll
			if (osViewport) osViewport.scrollTop = savedOsScroll

			requestAnimationFrame(() => {
				if (pane) pane.scrollTop = savedHostScroll
				if (osViewport) osViewport.scrollTop = savedOsScroll
				setTimeout(() => {
					if (pane) pane.scrollTop = savedHostScroll
					if (osViewport) osViewport.scrollTop = savedOsScroll
				}, 10)
			})
		}
		return
	}

	// Handle link clicks globally (prevent default and open in system/tauri)
	const anchor = target.closest("a")
	if (anchor) {
		const href = anchor.getAttribute("href")
		if (href && href !== "#") {
			e.preventDefault()
			e.stopPropagation()

			// Check if it's a web link
			if (href.startsWith("http://") || href.startsWith("https://")) {
				open(href).catch((err) =>
					console.error("Failed to open web link:", err),
				)
			} else {
				// Handle file or relative link
				let finalUri = cleanPath(href)
				if (finalUri.startsWith("file://")) {
					finalUri = cleanPath(finalUri.replace("file://", ""))
				}
				// Resolve relative paths against the active project
				if (!finalUri.startsWith("/") && !finalUri.startsWith("~/")) {
					if (finalUri.startsWith("./")) {
						finalUri = finalUri.slice(2)
					}
					if (activeProject) {
						finalUri = `${activeProject}/${finalUri}`
					}
				}
				invoke("open_path", { path: finalUri }).catch((err) =>
					console.error("Failed to open path:", err),
				)
			}
			return
		}
	}

	// Focus appropriate terminal or textarea
	const path = e.composedPath()
	const isEngineTermClick = container && path.includes(container)
	const isMiniTermClick = miniContainer && path.includes(miniContainer)
	const sidebar = document.getElementById("projects-sidebar")
	const isSidebarClick = sidebar && path.includes(sidebar)
	const previewPane = document.getElementById("markdown-preview-pane")
	const isPreviewClick = previewPane && path.includes(previewPane)

	if (isEngineTermClick) {
		term.focus()
	} else if (isMiniTermClick) {
		miniTerm.focus()
	} else if (
		!isSidebarClick &&
		!isPreviewClick &&
		target.tagName !== "INPUT" &&
		target.tagName !== "TEXTAREA" &&
		(!selection || selection.toString() === "")
	) {
		if (isTerminalMode) {
			miniTerm.focus()
		} else {
			textarea?.focus({ preventScroll: true })
			updatePlaceholder()
		}
	}
})

// Initialize workspace session
;(async () => {
	await syncProjectsFromAllThreads()
	try {
		const initialProject = await invoke<string | null>("get_initial_project")
		if (initialProject) {
			const cleanPath = initialProject.trim()
			const existing = projects.find((p) => p.path === cleanPath)
			if (existing) {
				activeProject = cleanPath
			} else {
				const name = cleanPath.split("/").pop() || "unknown-project"
				const newProj: Project = {
					path: cleanPath,
					name,
					color: getRandomProjectColor(),
					lastActive: Date.now(),
					engine: "agy",
					isTerminalMode: false,
				}
				projects.push(newProj)
				saveProjects()
				activeProject = cleanPath
			}
		} else {
			// Sort by recency to get the most recent active project on startup
			const sorted = [...projects].sort((a, b) => b.lastActive - a.lastActive)
			if (sorted.length > 0) {
				activeProject = sorted[0].path
			}
		}
	} catch (e) {
		console.error("Failed to get initial project:", e)
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
		const isRunning = await invoke<boolean>("is_engine_running", {
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
		const quotaJson = await invoke<string>("get_quota")
		const data = JSON.parse(quotaJson)

		let googlePct = "0%"
		let anthropicPct = "0%"

		const googleModels = data.Models.filter(
			(m: any) =>
				m.Provider === "MODEL_PROVIDER_GOOGLE" &&
				!m.ResetTime.startsWith("0001"),
		)
		const anthropicModels = data.Models.filter(
			(m: any) =>
				m.Provider === "MODEL_PROVIDER_ANTHROPIC" &&
				!m.ResetTime.startsWith("0001"),
		)

		if (googleModels.length > 0) {
			const minRem = Math.min(
				...googleModels.map((m: any) => m.RemainingFraction),
			)
			googlePct = (minRem * 100).toFixed(0) + "%"
		}

		if (anthropicModels.length > 0) {
			const minRem = Math.min(
				...anthropicModels.map((m: any) => m.RemainingFraction),
			)
			anthropicPct = (minRem * 100).toFixed(0) + "%"
		}

		const display = document.getElementById("quota-display")
		if (display) {
			display.innerText = `QUOTAS | Google: ${googlePct}, Anthropic: ${anthropicPct}`
			display.classList.remove("hidden")
		}

		const tooltip = document.getElementById("quota-tooltip")
		if (tooltip) {
			tooltip.innerHTML =
				'<div class="><div id="quota-col-google" class="></div><div id="quota-col-anthropic" class="></div></div>'

			const getProviderData = (name: string, pName: string, colId: string) => {
				const allModels = data.Models.filter(
					(m: any) => m.Provider === pName && !m.ResetTime.startsWith("0001"),
				)
				const col = document.getElementById(colId)
				if (!col) return

				col.innerHTML += `<div class=">${name}</div>`

				const highModels = allModels.filter(
					(m: any) =>
						!(
							m.ModelID.includes("-low") ||
							(m.DisplayName && m.DisplayName.includes("(Low)"))
						),
				)
				const lowModels = allModels.filter(
					(m: any) =>
						m.ModelID.includes("-low") ||
						(m.DisplayName && m.DisplayName.includes("(Low)")),
				)

				const renderBucket = (label: string, models: any[]) => {
					if (models.length === 0) return
					const minRem = Math.min(
						...models.map((m: any) => m.RemainingFraction),
					)
					const pct = (minRem * 100).toFixed(0) + "%"

					const rt = models[0].ResetTime
					const d = new Date(rt as string)

					const diffMs = d.getTime() - Date.now()
					let timeStr = "Now"
					if (diffMs > 0) {
						const h = Math.floor(diffMs / 3600000)
						const m = Math.floor((diffMs % 3600000) / 60000)
						let localT = d
							.toLocaleTimeString([], {
								hour: "numeric",
								minute: "2-digit",
							})
							.toLowerCase()
						localT = localT
							.replace(/\s+/g, "")
							.replace("am", "a")
							.replace("pm", "p")
						timeStr = `in ${h}h ${m}m (${localT})`
					}

					const row = document.createElement("div")
					row.className = "quota-row-item"
					row.innerHTML = `<span class=">${label}:</span> <div class="> <span class="${minRem < 0.2 ? "text-red-400" : "text-green-400"} font-bold w-9">${pct}</span> <span class="">resets ${timeStr}</span></div>`
					col.appendChild(row)
				}

				renderBucket("5-hr", highModels)
				renderBucket("Weekly", lowModels)
			}

			getProviderData("Google", "MODEL_PROVIDER_GOOGLE", "quota-col-google")
			getProviderData(
				"Anthropic",
				"MODEL_PROVIDER_ANTHROPIC",
				"quota-col-anthropic",
			)

			tooltip.classList.remove("hidden")
		}
	} catch (e) {
		console.error("Failed to update quota:", e)
	}
}

updateQuotaDisplay()
setInterval(updateQuotaDisplay, 60000)

import("./ActionBar/ActionBar").then(({ ActionBar }) => {
	const actionBar = new ActionBar()
	;(window as any).actionBar = actionBar
	
	const commands = [
		{
			name: "Search active threads...",
			description: "Search project threads using query (Cmd+F)",
			action: () => {
				switchTab("search")
			}
		},
		{
			name: "New Thread",
			description: "Start a new conversation thread in active project (Cmd+N)",
			action: () => {
				const newThreadBtn = document.querySelector(".new-thread-btn") as HTMLButtonElement | null
				if (newThreadBtn) {
					newThreadBtn.click()
				}
			}
		},
		{
			name: "Add Project",
			description: "Open an existing project folder or create a new project",
			action: () => {
				const addProjectBtn = document.getElementById("add-project-btn") as HTMLButtonElement | null
				if (addProjectBtn) {
					addProjectBtn.click()
				}
			}
		},
		{
			name: "Refresh / Redraw Terminal",
			description: "Redraw and fit the active terminal window (Cmd+Shift+R)",
			action: () => {
				try {
					(window as any).refreshActiveTerminal()
				} catch (err) {}
			}
		},
		{
			name: "Toggle Staging Area",
			description: "Pause or resume current background processes",
			action: () => {
				const pauseBtn = document.getElementById("pause-btn") as HTMLButtonElement | null
				if (pauseBtn) {
					pauseBtn.click()
				}
			}
		},
		{
			name: "Toggle Sidebar",
			description: "Toggle visibility of the sidebar",
			action: () => {
				const sidebar = document.getElementById("projects-sidebar")
				if (sidebar) {
					sidebar.classList.toggle("hidden")
				}
			}
		},
		{
			name: "Open Developer Tools",
			description: "Open the developer console window (Cmd+Option+I)",
			action: () => {
				invoke("open_devtools").catch(console.error)
			}
		}
	];
	actionBar.setCommands(commands)
})

// Tab Switching
const tabProjects = document.getElementById("tab-projects")
const tabSearch = document.getElementById("tab-search")
const contentProjects = document.getElementById("tab-content-projects")
const contentSearch = document.getElementById("tab-content-search")

const switchTab = (tab: "projects" | "search") => {
	if (tab === "projects") {
		tabProjects?.classList.add("active")
		tabSearch?.classList.remove("active")
		contentProjects?.classList.add("active")
		contentSearch?.classList.remove("active")
	} else {
		tabProjects?.classList.remove("active")
		tabSearch?.classList.add("active")
		contentProjects?.classList.remove("active")
		contentSearch?.classList.add("active")
		
		const searchInput = document.getElementById("sidebar-search-input") as HTMLInputElement
		if (searchInput) {
			searchInput.focus()
			searchInput.select()
		}
	}
}

tabProjects?.addEventListener("click", () => switchTab("projects"))
tabSearch?.addEventListener("click", () => switchTab("search"))

// Big Search Button
const bigSearchBtn = document.getElementById("sidebar-big-search-btn")
bigSearchBtn?.addEventListener("click", () => {
	switchTab("search")
})

// Cmd+F Keyboard Shortcut
window.addEventListener("keydown", (e) => {
	if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "f") {
		e.preventDefault()
		switchTab("search")
	}
})

// Search input handler
const searchInput = document.getElementById("sidebar-search-input") as HTMLInputElement
const searchResultsContainer = document.getElementById("sidebar-search-results")
if (searchResultsContainer) {
	initOS(searchResultsContainer)
}
let searchDebounce: any = null

const performSidebarSearch = async () => {
	if (!searchInput || !searchResultsContainer) return
	const contentEl = getContentEl(searchResultsContainer) || searchResultsContainer
	const query = searchInput.value.trim()
	if (!query) {
		contentEl.innerHTML = ""
		return
	}

	try {
		interface ThreadSearchResult {
			thread: any
			score: number
			preview: string
			matches: string[]
		}

		const results = await invoke<ThreadSearchResult[]>("search_project_threads", {
			projectPath: activeProject,
			query,
		})

		contentEl.innerHTML = ""
		if (results.length === 0) {
			contentEl.innerHTML = '<div class="no-threads">No results found</div>'
			return
		}

		results.forEach((result) => {
			const el = document.createElement("div")
			const isActive = activeThreadId === result.thread.id
			el.className = `search-result-thread-item${isActive ? " active" : ""}`
			
			const ts = result.thread.mtime > 0 ? result.thread.mtime * 1000 : Date.now()
			const dateStr = getRelativeDateStr(ts)

			let matchesHtml = ""
			if (result.matches && result.matches.length > 0) {
				matchesHtml = `
					<div class="search-result-matches">
						${result.matches.map(match => `<div class="search-result-match-line">${match}</div>`).join("")}
					</div>
				`
			} else {
				matchesHtml = `
					<div class="search-result-matches">
						<div class="search-result-match-line">${result.preview}</div>
					</div>
				`
			}

			el.innerHTML = `
				<div class="search-result-header">
					<div class="search-result-title">${result.thread.title || result.thread.id}</div>
					<div class="search-result-date">${dateStr}</div>
				</div>
				${matchesHtml}
			`

			el.addEventListener("click", () => {
				selectAndLoadThread(result.thread)
			})

			contentEl.appendChild(el)
		})
	} catch (err) {
		console.error("Search failed:", err)
		contentEl.innerHTML = `<div class="no-threads">Error performing search</div>`
	}
}

searchInput?.addEventListener("input", () => {
	clearTimeout(searchDebounce)
	searchDebounce = setTimeout(performSidebarSearch, 250)
})

// Listen for Google account rotation/switch to clear out old tmux PTY sessions and start fresh
listen<string>("account-changed", async (event) => {
	console.log("[ai-os] Account changed to:", event.payload)
	// Clear cached terminal history buffers
	for (const key of Object.keys(claudeBuffers)) delete claudeBuffers[key]
	for (const key of Object.keys(agyBuffers)) delete agyBuffers[key]
	for (const key of Object.keys(hermesBuffers)) delete hermesBuffers[key]
	for (const key of Object.keys(miniTermBuffers)) delete miniTermBuffers[key]

	// Reset standard terminal windows
	term.reset()
	miniTerm.reset()

	// Automatically refresh active project to recreate PTY sessions on the backend
	if (activeProject) {
		await switchToProject(activeProject, true)
	}
})
