/** One numbered action the agent's latest reply offered. */
export type Action = { n: string; label: string }

declare module 'claude-code' {
  interface PluginState {
    'action-bar': {
      /** Actions from the latest main-thread reply; [] hides the bar. */
      actions: Action[]
    }
  }
}
