import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

const choice = atom({ plugin: 'read-aloud', key: 'choice' } as const, null as boolean | null)
const speaking = atom({ plugin: 'read-aloud', key: 'speaking' } as const, false)

const home = async ($: EngineInterface) => (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout

// The pressing, waiting and dictation live in Hammerspoon (modules/claude_read_aloud.lua):
// it presses Claude's own Read aloud button through accessibility, never the system voice.
const hs = async ($: EngineInterface, fn: 'replyDone' | 'cancel') => {
  try {
    await $.process.run(['/usr/local/bin/hs', '-c', `return require("modules.claude_read_aloud").${fn}()`], { timeoutMs: 5000 })
  } catch {}
}

// Defaults on for the Coordinator (its id is in ai-os coordinator/session.txt).
const isCoordinator = async ($: EngineInterface) => {
  try {
    const want = (await $.fs.read(`${await home($)}/projects/ai-os/coordinator/session.txt`)).trim()
    const id = await $.session.id()
    return want.length > 0 && (id.includes(want) || want.includes(id))
  } catch {
    return false
  }
}

const isOn = async ($: EngineInterface) => (await read($, choice)) ?? (await isCoordinator($))

// Same test as the live-call hook: a call is live only while its transcript is still growing.
const onCall = async ($: EngineInterface) => {
  try {
    const r = await $.process.run(['python3', `${await home($)}/projects/ai-os/scripts/hooks/live_call.py`])
    return r.stdout.startsWith('LIVE CALL')
  } catch {
    return false
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    await $.command.register({ name: 'read-aloud', description: 'Turn spoken replies on or off in this session' })
    return r
  })

  on('command.run', { name: 'read-aloud' }, async ($, e, next) => {
    const now = !(await isOn($))
    await update($, choice, () => now)
    if (!now) await hs($, 'cancel')
    return { text: now ? 'Replies will be read aloud in this session.' : 'Read-aloud is off in this session.' }
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (e.agentId === undefined && (await isOn($))) {
      // A live call stays quiet unless Matt turned it on in this session himself.
      if ((await read($, choice)) !== true && (await onCall($))) return r
      await update($, speaking, () => true)
      await hs($, 'replyDone')
    }
    return r
  })

  // Typing, dictating or sending cuts the voice off.
  on('prompt.change', async ($, e, next) => {
    if ((await read($, speaking)) && e.origin.kind !== 'clear' && e.text.length > 0) {
      await update($, speaking, () => false)
      await hs($, 'cancel')
    }
    return next(e)
  })
  on('prompt.submit', async ($, e, next) => {
    if (await read($, speaking)) {
      await update($, speaking, () => false)
      await hs($, 'cancel')
    }
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const above = await next(e)
    const on_ = await isOn($)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="column">
        {above}
        <Box flexWrap="wrap">
          <Text dimColor>{on_ ? '🔊 Replies are read aloud ' : '🔈 Read-aloud off '}</Text>
          <Button
            key="toggle"
            label={on_ ? 'Turn off' : 'Turn on'}
            variant="secondary"
            onPress={async () => {
              await update($, choice, () => !on_)
              if (on_) await hs($, 'cancel')
            }}
          />
          <Text dimColor> · /read-aloud toggles · typing stops it · dictation starts after</Text>
        </Box>
      </Box>
    )
  })
}
