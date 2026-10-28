/** One action the agent's latest reply offered. */
export type Action = { label: string; text: string; /** Part of an either/or set (" | "): no "All of these". */ either?: boolean }

declare module 'claude-code' {
  interface PluginState {
    'action-bar': {
      /** Actions from the latest main-thread reply; [] hides the bar. */
      actions: Action[]
    }
  }
}
