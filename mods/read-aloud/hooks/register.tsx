import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

const choice = atom({ plugin: 'read-aloud', key: 'choice' } as const, null as boolean | null)
const dictate = atom({ plugin: 'read-aloud', key: 'dictate' } as const, true)
const speaking = atom({ plugin: 'read-aloud', key: 'speaking' } as const, false)

const home = async ($: EngineInterface) => (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout

// The pressing, waiting and dictation live in Hammerspoon (modules/claude_read_aloud.lua):
// it presses Claude's own Read aloud button through accessibility, never the system voice.
const hs = async ($: EngineInterface, call: string): Promise<string> => {
  try {
    const r = await $.process.run(['/usr/local/bin/hs', '-c', `return require("modules.claude_read_aloud").${call}`], { timeoutMs: 5000 })
    return r.stdout.trim()
  } catch {
    return ''
  }
}

// "Dictate after" lives in Hammerspoon's tweaks file (saved, shared by every session).
const setDictate = async ($: EngineInterface, on: boolean) => {
  await update($, dictate, () => on)
  await hs($, `dictateAfter("${on ? 'on' : 'off'}")`)
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

// Every text the assistant wrote since Matt's last real message (tool results are user rows too).
export const turnTexts = (msgs: { role: string; text: string; toolResults?: unknown[] }[]) => {
  let i = msgs.length - 1
  while (i >= 0 && !(msgs[i].role === 'user' && msgs[i].text.trim() && !(msgs[i].toolResults?.length))) i--
  return msgs.slice(i + 1).filter(m => m.role === 'assistant' && m.text.trim()).map(m => m.text)
}

// What gets spoken: markdown and links flattened, as Claude's Read aloud says it.
export const plain = (md: string) =>
  md.replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/[*_`#>]/g, '').replace(/\s+/g, ' ').trim()

// Lines only mods read (hidden by the action bar), never meant to be heard.
const MOD_LINE = /^\s*(\*\*)?Actions:(\*\*)?/

// Queue items, oldest first. key: the reply's opening words, to find its own Read aloud button.
// cut: spoken characters before the first mod-only line (null = read it all).
// Short progress notes before the real reply are skipped; the turn's last text always stays.
export const queueItems = (texts: string[], minChars = 160) =>
  texts
    .filter((t, i) => i === texts.length - 1 || plain(t).length >= minChars)
    .map(t => {
      const lines = t.split('\n')
      const at = lines.findIndex(l => MOD_LINE.test(l))
      const spoken = plain(at < 0 ? t : lines.slice(0, at).join('\n'))
      return { key: plain(t).toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 40), cut: at < 0 ? null : spoken.length, chars: spoken.length }
    })
    .filter(x => x.key.length > 0)

// Keeps `speaking` true only while Claude is really reading (or paused for an Interrupt),
// so the Interrupt button shows only then. Gives up after 15 min of waiting.
let stopWatch: (() => void) | null = null
const watchSpeaking = ($: EngineInterface) => {
  stopWatch?.()
  let seen = false, ticks = 0
  const t = $.clock.every(1000, async () => {
    ticks++
    const now = (await hs($, 'isReading()')) === 'true'
    if (now !== (await read($, speaking))) await update($, speaking, () => now)
    if (now) seen = true
    if ((seen && !now && (await hs($, 'isPending()')) !== 'true') || ticks > 900) stopWatch?.()
  })
  stopWatch = () => { t.cancel(); stopWatch = null }
}

// Claude's listening-mic tint: its blue at low opacity, so it works in light and dark.
const TINT = 'rgba(37, 99, 235, 0.14)'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    await $.command.register({ name: 'read-aloud', description: 'Turn spoken replies on or off in this session' })
    await $.command.register({ name: 'dictate-after', description: 'Turn dictation after read-aloud on or off (saved)' })
    const now = await hs($, 'dictateAfter()')
    if (now === 'on' || now === 'off') await update($, dictate, () => now === 'on')
    return r
  })

  on('command.run', { name: 'read-aloud' }, async ($, e, next) => {
    const now = !(await isOn($))
    await update($, choice, () => now)
    if (!now) await hs($, `cancel("${(await $.session.id()).slice(0, 8)}")`)
    return { text: now ? 'Replies will be read aloud in this session.' : 'Read-aloud is off in this session.' }
  })

  on('command.run', { name: 'dictate-after' }, async ($, e, next) => {
    const now = !(await read($, dictate))
    await setDictate($, now)
    return { text: now ? 'Dictation starts after each read-aloud.' : 'No dictation after read-aloud.' }
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (e.agentId === undefined && e.reason === 'answer' && e.answer.trim() && (await isOn($))) {
      // A live call stays quiet unless Matt turned it on in this session himself.
      if ((await read($, choice)) !== true && (await onCall($))) return r
      let texts: string[] = [e.answer]
      try { texts = turnTexts(await $.session.messages()) } catch {}
      const session = (await $.session.id()).slice(0, 8)
      const dir = `${await home($)}/.hammerspoon/tmp/read_aloud_queue`
      await $.process.run(['mkdir', '-p', dir])
      let n = 0
      for (const item of queueItems(texts.length ? texts : [e.answer])) {
        await $.fs.write(`${dir}/${Date.now()}-${n++}-${session}.json`, JSON.stringify({ ...item, session }))
      }
      await update($, speaking, () => true)
      await hs($, 'replyDone()')
      watchSpeaking($)
    }
    return r
  })

  // Typing, dictating or sending cuts the voice off.
  // (Not while it's paused for an Interrupt: that dictation is meant to land in the prompt.)
  on('prompt.change', async ($, e, next) => {
    if ((await read($, speaking)) && e.origin.kind !== 'clear' && e.text.length > 0 && (await hs($, 'isPaused()')) !== 'true') {
      await update($, speaking, () => false)
      await hs($, `cancel("${(await $.session.id()).slice(0, 8)}")`)
    }
    return next(e)
  })
  on('prompt.submit', async ($, e, next) => {
    if (await read($, speaking)) {
      await update($, speaking, () => false)
      await hs($, `cancel("${(await $.session.id()).slice(0, 8)}")`)
    }
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const above = await next(e)
    const on_ = await isOn($)
    const dict = await read($, dictate)
    const talking = on_ && (await read($, speaking))
    const { Box, Button, Text } = $.ui.resolve(e)
    // This mod's controls sit first; on = tinted rounded chip with a blue glyph, like Claude's own
    // mic button when it's listening; off = the same size, no tint, dim glyph (so nothing shifts).
    // Interrupt sits after the reply buttons, so showing or hiding it never moves them.
    const chip = (key: string, lit: boolean, glyph: string, press: () => unknown) => (
      <Box key={`c-${key}`} borderStyle="round" borderColor={lit ? TINT : 'transparent'} backgroundColor={lit ? TINT : 'transparent'} marginRight="xs">
        <Button key={key} plain onPress={press}>
          <Text color={lit ? 'suggestion' : 'inactive'}>{glyph}</Text>
        </Button>
      </Box>
    )
    const stopHere = async () => { await update($, choice, () => !on_); if (on_) await hs($, `cancel("${(await $.session.id()).slice(0, 8)}")`) }
    return (
      <Box flexWrap="wrap" alignItems="center">
        {chip('toggle', on_, on_ ? '🕪' : '🕨', stopHere)}
        {chip('dictate', dict, '🎙\uFE0E', () => setDictate($, !dict))}
        {above}
        {talking && chip('interrupt', true, '⏸\uFE0E', () => hs($, 'interrupt()'))}
      </Box>
    )
  })
}
