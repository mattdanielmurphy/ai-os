declare module 'claude-code' {
  interface PluginState {
    'read-aloud': {
      /** This session's choice; null = default (on in the Coordinator, off elsewhere). */
      choice: boolean | null
      speaking: boolean
      /** Start dictation when reading ends (mirrors Hammerspoon's saved setting). */
      dictate: boolean
    }
  }
}
export type ReadAloud = true
