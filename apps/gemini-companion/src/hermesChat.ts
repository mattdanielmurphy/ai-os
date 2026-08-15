// Hermes WebSocket Chat Client — JSON-RPC 2.0 over WebSocket
// Replaces xterm.js/PTY for the Hermes engine only

const HERMES_WS_PORT = 9119
const WS_URL = `ws://127.0.0.1:${HERMES_WS_PORT}/api/ws?token=ai_os_secret_token_123456`
const REQUEST_TIMEOUT = 120_000

type ConnectionState = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

function log(...args: unknown[]) {
	console.log('[HermesChat]', ...args)
}

export class HermesChatClient {
	private ws: WebSocket | null = null
	private _sessionId: string | null = null
	private _cwd: string | null = null
	private _state: ConnectionState = 'idle'
	private nextId = 1
	private pending = new Map<string, { resolve: (v: unknown) => void; reject: (e: Error) => void; timer: ReturnType<typeof setTimeout> }>()
	private onStateChange: ((state: ConnectionState) => void) | null = null
	private _connectPromise: Promise<void> | null = null
	private _initPromise: Promise<void> | null = null

	// Message callbacks
	onMessageStart: ((messageId: string) => void) | null = null
	onMessageDelta: ((messageId: string, text: string) => void) | null = null
	onMessageComplete: ((messageId: string) => void) | null = null
	onThinkingDelta: ((messageId: string, text: string) => void) | null = null
	onReasoningDelta: ((messageId: string, text: string) => void) | null = null
	onToolStart: ((messageId: string, toolId: string, name: string) => void) | null = null
	onToolComplete: ((messageId: string, toolId: string, name: string, result: string) => void) | null = null
	onError: ((error: string) => void) | null = null

	get connectionState() { return this._state }
	get sessionId() { return this._sessionId }
	get cwd() { return this._cwd }

	setStateChangeHandler(handler: (state: ConnectionState) => void) {
		this.onStateChange = handler
	}

	async connect(): Promise<void> {
		// If already connected, return immediately
		if (this.ws?.readyState === WebSocket.OPEN) {
			log('connect(): already open, skipping')
			return
		}
		// If already connecting, return the existing promise (deduplicate)
		if (this._connectPromise) {
			log('connect(): connection already in progress, reusing promise')
			return this._connectPromise
		}
		this._connectPromise = this._doConnect()
		try {
			await this._connectPromise
		} finally {
			this._connectPromise = null
		}
	}

	private _doConnect(): Promise<void> {
		this.setState('connecting')
		log('connect(): opening WebSocket to', WS_URL)

		return new Promise((resolve, reject) => {
			try {
				this.ws = new WebSocket(WS_URL)
			} catch (e) {
				log('connect(): WebSocket constructor threw:', e)
				this.setState('error')
				reject(e)
				return
			}

			const ws = this.ws
			let settled = false
			const timer = setTimeout(() => {
				if (!settled) {
					settled = true
					log('connect(): timed out after 15s')
					ws.close()
					this.setState('error')
					reject(new Error('WebSocket connection timed out'))
				}
			}, 15000)

			ws.onopen = () => {
				if (settled) return
				settled = true
				clearTimeout(timer)
				log('connect(): WebSocket OPEN')
				this.setState('connected')
				resolve()
			}

			ws.onerror = (ev) => {
				log('connect(): WebSocket error event', ev)
				if (settled) return
				settled = true
				clearTimeout(timer)
				this.setState('error')
				reject(new Error('WebSocket connection failed'))
			}

			ws.onclose = (ev) => {
				log('connect(): WebSocket closed, code=', ev.code, 'reason=', ev.reason)
				this.ws = null
				this.setState('disconnected')
				this.rejectAllPending(new Error('WebSocket closed'))
			}

			ws.onmessage = (event) => {
				const lines = event.data.split('\n').filter((l: string) => l.trim())
				for (const line of lines) {
					try {
						const frame = JSON.parse(line)
						this.handleFrame(frame)
					} catch {
						log('onmessage: failed to parse frame:', line.substring(0, 200))
					}
				}
			}
		})
	}

	disconnect() {
		log('disconnect()')
		if (this.ws) {
			try { this.ws.close() } catch {}
			this.ws = null
		}
		this._sessionId = null
		this._cwd = null
		this._connectPromise = null
		this._initPromise = null
		this.setState('disconnected')
	}

	async createSession(cwd?: string): Promise<void> {
		const params: Record<string, unknown> = { cols: 96, source: 'ai-os' }
		if (cwd) {
			params.cwd = cwd
		}
		log('createSession(): cwd=', cwd)
		const result = await this.request('session.create', params) as any
		this._sessionId = result.session_id as string
		this._cwd = cwd || null
		log('createSession(): got session_id=', this._sessionId)
	}

	async submitPrompt(text: string): Promise<void> {
		if (!this._sessionId) {
			log('submitPrompt(): ERROR - no active session')
			throw new Error('No active session')
		}
		log('submitPrompt(): session=', this._sessionId, 'text=', text.substring(0, 50))
		// Fire-and-forget: response comes via events
		this.request('prompt.submit', { session_id: this._sessionId, text }).catch((e) => {
			log('submitPrompt(): request failed:', e.message)
			this.onError?.(`Prompt submit failed: ${e.message}`)
		})
	}

	async closeSession(): Promise<void> {
		if (!this._sessionId) return
		log('closeSession(): session=', this._sessionId)
		try {
			await this.request('session.close', { session_id: this._sessionId })
		} catch {}
		this._sessionId = null
		this._cwd = null
	}

	async interrupt(): Promise<void> {
		if (!this._sessionId) return
		log('interrupt(): session=', this._sessionId)
		try {
			await this.request('session.interrupt', { session_id: this._sessionId })
		} catch {}
	}

	/**
	 * Full init: ensure daemon → connect → create session.
	 * Deduplicates concurrent calls so only one init runs at a time.
	 */
	async init(cwd: string | undefined, ensureDaemon: () => Promise<void>): Promise<void> {
		// If already fully initialized for this cwd, skip
		if (this._state === 'connected' && this._sessionId && this._cwd === cwd) {
			log('init(): already connected with session for cwd=', cwd, ', skipping')
			return
		}
		// Deduplicate concurrent init calls
		if (this._initPromise) {
			log('init(): already in progress, reusing promise')
			return this._initPromise
		}
		this._initPromise = this._doInit(cwd, ensureDaemon)
		try {
			await this._initPromise
		} finally {
			this._initPromise = null
		}
	}

	private async _doInit(cwd: string | undefined, ensureDaemon: () => Promise<void>): Promise<void> {
		log('init(): starting full init, cwd=', cwd)
		// If session exists for different cwd, close it
		if (this._sessionId && this._cwd !== cwd) {
			log('init(): closing existing session for different cwd')
			await this.closeSession().catch(() => {})
		}
		// Ensure daemon is running
		log('init(): ensuring daemon...')
		await ensureDaemon()
		// Connect WebSocket
		log('init(): connecting...')
		await this.connect()
		// Create session if needed
		if (!this._sessionId) {
			log('init(): creating session...')
			await this.createSession(cwd)
		}
		log('init(): READY, session=', this._sessionId, 'state=', this._state)
	}

	private request(method: string, params: Record<string, unknown>): Promise<unknown> {
		return new Promise((resolve, reject) => {
			if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
				log('request(): NOT connected, rejecting', method)
				reject(new Error('Not connected'))
				return
			}

			const id = `r${this.nextId++}`
			const timer = setTimeout(() => {
				this.pending.delete(id)
				log('request(): TIMEOUT for', method, 'id=', id)
				reject(new Error(`Request timed out: ${method}`))
			}, REQUEST_TIMEOUT)

			this.pending.set(id, { resolve, reject, timer })

			const msg = JSON.stringify({
				jsonrpc: '2.0',
				id,
				method,
				params,
			})
			this.ws.send(msg)
		})
	}

	private handleFrame(frame: any) {
		// Response to a pending request
		if (frame.id && this.pending.has(String(frame.id))) {
			const pending = this.pending.get(String(frame.id))!
			clearTimeout(pending.timer)
			this.pending.delete(String(frame.id))
			if (frame.error) {
				log('handleFrame: RPC error for id=', frame.id, frame.error)
				pending.reject(new Error(frame.error.message || 'RPC error'))
			} else {
				pending.resolve(frame.result)
			}
			return
		}

		// Server event (method === 'event')
		if (frame.method === 'event' && frame.params) {
			this.handleEvent(frame.params)
		}
	}

	private handleEvent(event: any) {
		const type = event.type as string
		const payload = event.payload as any
		const sid = event.session_id as string | undefined

		switch (type) {
			case 'gateway.ready':
			case 'session.info':
				log('handleEvent:', type)
				break

			case 'message.start': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
				log('handleEvent: message.start msgId=', msgId)
				this.onMessageStart?.(msgId)
				break
			}

			case 'message.delta': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
				this.onMessageDelta?.(msgId, payload?.text || '')
				break
			}

			case 'message.complete': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
				log('handleEvent: message.complete msgId=', msgId)
				this.onMessageComplete?.(msgId)
				break
			}

			case 'thinking.delta': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
				this.onThinkingDelta?.(msgId, payload?.text || '')
				break
			}

			case 'reasoning.delta': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
				this.onReasoningDelta?.(msgId, payload?.text || '')
				break
			}

			case 'tool.start': {
				const msgId = sid || 'msg-' + Date.now()
				const toolId = payload?.tool_call_id || payload?.id || 'tool-' + Date.now()
				const name = payload?.name || payload?.tool || 'unknown'
				log('handleEvent: tool.start', name)
				this.onToolStart?.(msgId, toolId, name)
				break
			}

			case 'tool.complete': {
				const msgId = sid || 'msg-' + Date.now()
				const toolId = payload?.tool_call_id || payload?.id || 'tool-' + Date.now()
				const name = payload?.name || payload?.tool || 'unknown'
				const result = typeof payload?.result === 'string' ? payload.result : JSON.stringify(payload?.result || '')
				log('handleEvent: tool.complete', name)
				this.onToolComplete?.(msgId, toolId, name, result)
				break
			}

			case 'error':
				log('handleEvent: error', payload?.message)
				this.onError?.(payload?.message || 'Unknown error')
				break

			default:
				log('handleEvent: unhandled type=', type)
		}
	}

	private rejectAllPending(error: Error) {
		for (const [, pending] of this.pending) {
			clearTimeout(pending.timer)
			pending.reject(error)
		}
		this.pending.clear()
	}

	private setState(state: ConnectionState) {
		const prev = this._state
		this._state = state
		if (prev !== state) {
			log('state:', prev, '->', state)
		}
		this.onStateChange?.(state)
	}
}