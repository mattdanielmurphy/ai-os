import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

const choice = atom({ plugin: 'read-aloud', key: 'choice' } as const, null as boolean | null)
const speaking = atom({ plugin: 'read-aloud', key: 'speaking' } as const, false)

// Knobs live in ~/.hammerspoon/tweaks/read_aloud.json (⌃⌥⌘T panel); missing or bad JSON keeps these.
export const KNOB_DEFAULTS = { rate: 200, volume: 0.7, maxChars: 1500, voice: '' }
type Knobs = typeof KNOB_DEFAULTS

const home = async ($: EngineInterface) => (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout

const knobs = async ($: EngineInterface): Promise<Knobs> => {
  try {
    const file = JSON.parse(await $.fs.read(`${await home($)}/.hammerspoon/tweaks/read_aloud.json`))
    const out: Knobs = { ...KNOB_DEFAULTS }
    for (const k of Object.keys(out) as (keyof Knobs)[]) {
      const v = file?.tweaks?.[k]?.value
      if (typeof v === typeof out[k]) (out as Record<string, unknown>)[k] = v
    }
    return out
  } catch {
    return KNOB_DEFAULTS
  }
}

/** Reply text as it should sound: no code, links, paths, markup or Actions/Details lines. */
export const speakable = (answer: string, maxChars = KNOB_DEFAULTS.maxChars): string => {
  let t = answer
    .replace(/```[\s\S]*?(```|$)/g, ' ')
    .split('\n')
    .filter(l => !/^\s*\**\s*(actions|details)\s*:/i.test(l.replace(/\*\*/g, '')))
    .join('\n')
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/`[^`]*`/g, ' ')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/(^|\s)~?\/[\w.~%-]+(\/[\w.~%-]+)+\/?/g, '$1')
    .replace(/^\s*(#+|>|[-*+]|\d+[.)])\s+/gm, '')
    .replace(/[*_~#|]+/g, '')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()
  if (t.length > maxChars) t = `${t.slice(0, maxChars).replace(/\s\S*$/, '')}. The rest is on screen.`
  return t
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

const onCall = async ($: EngineInterface) =>
  (await $.process.run(['sh', '-c', 'kill -0 "$(cat "$HOME/calls/.transcript.pid" 2>/dev/null)" 2>/dev/null'])).exitCode === 0

let current: { return?: () => unknown } | undefined

const stop = async ($: EngineInterface) => {
  const c = current
  current = undefined
  if (c) await c.return?.()
  if (await read($, speaking)) await update($, speaking, () => false)
}

const say = async ($: EngineInterface, text: string) => {
  await stop($)
  const k = await knobs($)
  const argv = ['say', '-r', String(Math.round(k.rate)), '-f', '-']
  if (k.voice) argv.splice(1, 0, '-v', k.voice)
  const vol = Math.min(1, Math.max(0, k.volume))
  const stream = $.process.spawn({ argv, input: `[[volm ${vol.toFixed(2)}]] ${text}` })
  current = stream as { return?: () => unknown }
  await update($, speaking, () => true)
  void (async () => {
    try {
      for await (const _ of stream) void _
    } catch {}
    if (current === stream) {
      current = undefined
      await update($, speaking, () => false)
    }
  })()
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
    if (!now) await stop($)
    return { text: now ? 'Replies will be read aloud in this session.' : 'Read-aloud is off in this session.' }
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (e.agentId === undefined && (await isOn($))) {
      // A live call stays quiet unless Matt turned it on in this session himself.
      if ((await read($, choice)) !== true && (await onCall($))) return r
      const text = speakable(e.answer, (await knobs($)).maxChars)
      if (text) await say($, text)
    }
    return r
  })

  // Typing, dictating or sending cuts the voice off.
  on('prompt.change', async ($, e, next) => {
    if (current && e.origin.kind !== 'clear' && e.text.length > 0) await stop($)
    return next(e)
  })
  on('prompt.submit', async ($, e, next) => {
    if (current) await stop($)
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const above = await next(e)
    const on_ = await isOn($)
    const talking = await read($, speaking)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="column">
        {above}
        <Box flexWrap="wrap">
          <Text dimColor>{talking ? '🔊 Reading the reply aloud ' : on_ ? '🔊 Replies are read aloud ' : '🔈 Read-aloud off '}</Text>
          {talking && <Button key="stop" label="Stop" variant="secondary" onPress={() => stop($)} />}
          <Button
            key="toggle"
            label={on_ ? 'Turn off' : 'Turn on'}
            variant="secondary"
            onPress={async () => {
              await update($, choice, () => !on_)
              if (on_) await stop($)
            }}
          />
          <Text dimColor> · /read-aloud toggles · typing stops it</Text>
        </Box>
      </Box>
    )
  })
}
