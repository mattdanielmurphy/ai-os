/** One action the agent's latest reply offered. */
export type Action = { label: string; text: string }

declare module 'claude-code' {
  interface PluginState {
    'action-bar': {
      /** Actions from the latest main-thread reply; [] hides the bar. */
      actions: Action[]
    }
  }
}
