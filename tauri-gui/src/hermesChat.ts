// Hermes WebSocket Chat Client — JSON-RPC 2.0 over WebSocket
// Replaces xterm.js/PTY for the Hermes engine only

const HERMES_WS_PORT = 9119
const WS_URL = `ws://127.0.0.1:${HERMES_WS_PORT}/api/ws?token=ai_os_secret_token_123456`
const REQUEST_TIMEOUT = 120_000

type ConnectionState = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'

export class HermesChatClient {
	private ws: WebSocket | null = null
	private _sessionId: string | null = null
	private _cwd: string | null = null
	private _state: ConnectionState = 'idle'
	private nextId = 1
	private pending = new Map<string, { resolve: (v: unknown) => void; reject: (e: Error) => void; timer: ReturnType<typeof setTimeout> }>()
	private onStateChange: ((state: ConnectionState) => void) | null = null

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
		if (this.ws?.readyState === WebSocket.OPEN) return
		this.setState('connecting')

		return new Promise((resolve, reject) => {
			try {
				this.ws = new WebSocket(WS_URL)
			} catch (e) {
				this.setState('error')
				reject(e)
				return
			}

			const ws = this.ws
			let settled = false
			const timer = setTimeout(() => {
				if (!settled) {
					settled = true
					ws.close()
					this.setState('error')
					reject(new Error('WebSocket connection timed out'))
				}
			}, 15000)

			ws.onopen = () => {
				if (settled) return
				settled = true
				clearTimeout(timer)
				this.setState('connected')
				resolve()
			}

			ws.onerror = () => {
				if (settled) return
				settled = true
				clearTimeout(timer)
				this.setState('error')
				reject(new Error('WebSocket connection failed'))
			}

			ws.onclose = () => {
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
						// skip malformed frames
					}
				}
			}
		})
	}

	disconnect() {
		if (this.ws) {
			try { this.ws.close() } catch {}
			this.ws = null
		}
		this._sessionId = null
		this._cwd = null
		this.setState('disconnected')
	}

	async createSession(cwd?: string): Promise<void> {
		const params: Record<string, unknown> = { cols: 96, source: 'ai-os' }
		if (cwd) {
			params.cwd = cwd
		}
		const result = await this.request('session.create', params) as any
		this._sessionId = result.session_id as string
		this._cwd = cwd || null
	}

	async submitPrompt(text: string): Promise<void> {
		if (!this._sessionId) throw new Error('No active session')
		// Fire-and-forget: response comes via events
		this.request('prompt.submit', { session_id: this._sessionId, text }).catch((e) => {
			this.onError?.(`Prompt submit failed: ${e.message}`)
		})
	}

	async closeSession(): Promise<void> {
		if (!this._sessionId) return
		try {
			await this.request('session.close', { session_id: this._sessionId })
		} catch {}
		this._sessionId = null
		this._cwd = null
	}

	async interrupt(): Promise<void> {
		if (!this._sessionId) return
		try {
			await this.request('session.interrupt', { session_id: this._sessionId })
		} catch {}
	}

	private request(method: string, params: Record<string, unknown>): Promise<unknown> {
		return new Promise((resolve, reject) => {
			if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
				reject(new Error('Not connected'))
				return
			}

			const id = `r${this.nextId++}`
			const timer = setTimeout(() => {
				this.pending.delete(id)
				reject(new Error(`Request timed out: ${method}`))
			}, REQUEST_TIMEOUT)

			this.pending.set(id, { resolve, reject, timer })

			this.ws.send(JSON.stringify({
				jsonrpc: '2.0',
				id,
				method,
				params,
			}))
		})
	}

	private handleFrame(frame: any) {
		// Response to a pending request
		if (frame.id && this.pending.has(String(frame.id))) {
			const pending = this.pending.get(String(frame.id))!
			clearTimeout(pending.timer)
			this.pending.delete(String(frame.id))
			if (frame.error) {
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
				break

			case 'message.start': {
				const msgId = payload?.message_id || sid || 'msg-' + Date.now()
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
				this.onToolStart?.(msgId, toolId, name)
				break
			}

			case 'tool.complete': {
				const msgId = sid || 'msg-' + Date.now()
				const toolId = payload?.tool_call_id || payload?.id || 'tool-' + Date.now()
				const name = payload?.name || payload?.tool || 'unknown'
				const result = typeof payload?.result === 'string' ? payload.result : JSON.stringify(payload?.result || '')
				this.onToolComplete?.(msgId, toolId, name, result)
				break
			}

			case 'error':
				this.onError?.(payload?.message || 'Unknown error')
				break
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
		this._state = state
		this.onStateChange?.(state)
	}
}