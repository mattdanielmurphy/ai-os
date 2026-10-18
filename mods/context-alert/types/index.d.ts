export type Fill = { tokens: number; window: number }

/** When the main thread last got a model response, and how long its prompt cache lives. */
export type Cache = { lastAt: number; ttlMs: number; tokens: number }

/** The cold handoff the band's button or /fresh started. */
export type Handoff = { status: 'writing' | 'done' | 'error'; text: string }

declare module 'claude-code' {
  interface PluginState {
    'context-alert': {
      fill: Fill | null
      lastToast: number
      cache: Cache | null
      now: number
      handoff: Handoff | null
      sendAnywayUntil: number
    }
  }
}
