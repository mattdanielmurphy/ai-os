declare module 'claude-code' {
  interface PluginState {
    'read-aloud': {
      /** This session's choice; null = default (on in the Coordinator, off elsewhere). */
      choice: boolean | null
      speaking: boolean
    }
  }
}
export type ReadAloud = true
