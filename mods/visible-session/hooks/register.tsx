import type { Register, EngineInterface } from 'claude-code'

// The desktop app only draws the band above the prompt for the thread on screen, so a band
// render means "this thread is visible". On a change we tell Hammerspoon
// (modules/readthrough_float.lua), which shows that thread's Readthrough float and hides others.
const FILE = '/.hammerspoon/tmp/claude_visible_session'

let home = ''
const homeDir = async ($: EngineInterface) => {
  if (!home) home = (await $.process.run(['/bin/sh', '-c', 'printf %s "$HOME"'], { timeoutMs: 2000 })).stdout
  return home
}

export const register: Register = (on) => {
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.surface === 'desktop') {
      void (async () => {
        try {
          const id = await $.session.id()
          const path = (await homeDir($)) + FILE
          let was = ''
          try { was = (await $.fs.read(path)).trim() } catch {}
          if (was === id) return
          await $.fs.write(path, id)
          await $.process.run(['/usr/local/bin/hs', '-c', `require("modules.readthrough_float").visible("${id}")`], { timeoutMs: 3000 })
        } catch {}
      })()
    }
    return next(e)
  })
}
