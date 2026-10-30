declare module 'claude-code' {
  interface PluginState {
    'no-suggestions': {
      /** This thread hides the grey suggestions; drives the band. */
      isOn: boolean
    }
  }
}
