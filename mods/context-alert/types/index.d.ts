export type Fill = { tokens: number; window: number }

declare module 'claude-code' {
  interface PluginState {
    'context-alert': { fill: Fill | null; lastToast: number }
  }
}
