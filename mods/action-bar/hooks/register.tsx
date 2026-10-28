import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Action } from '../types'

const actions = atom({ plugin: 'action-bar', key: 'actions' } as const, [] as Action[])

// Knobs live in ~/.hammerspoon/tweaks/action_bar.json (⌃⌥⌘T panel); missing or bad JSON keeps these.
export const KNOB_DEFAULTS = { maxActions: 6, labelChars: 32 }
type Knobs = typeof KNOB_DEFAULTS

const knobs = async ($: EngineInterface): Promise<Knobs> => {
  try {
    const home = (await $.process.run(['sh', '-c', 'printf %s "$HOME"'])).stdout
    const file = JSON.parse(await $.fs.read(`${home}/.hammerspoon/tweaks/action_bar.json`))
    const out = { ...KNOB_DEFAULTS }
    for (const k of Object.keys(out) as (keyof Knobs)[]) {
      const v = file?.tweaks?.[k]?.value
      if (typeof v === 'number') out[k] = v
    }
    return out
  } catch {
    return KNOB_DEFAULTS
  }
}

const strip = (s: string) => s.replace(/\*\*|__|`/g, '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').trim()

/**
 * The actions line: the last non-empty line of the reply that starts with "Actions:"
 * (bold allowed) and holds "1. X · 2. Y". Nothing else counts, so ordinary numbered
 * lists never raise the bar.
 */
export const parseActions = (answer: string, k: Knobs = KNOB_DEFAULTS): Action[] => {
  const lines = answer.split('\n').map(strip).filter(Boolean)
  const line = [...lines].reverse().find(l => /^actions\s*:/i.test(l))
  if (!line) return []
  const body = line.replace(/^actions\s*:/i, '')
  const out: Action[] = []
  for (const part of body.split(/\s[·•|]\s/)) {
    const m = /^\s*(\d{1,2})[.)]\s+(.+?)\s*$/.exec(part)
    if (!m) continue
    const label = m[2].length > k.labelChars ? `${m[2].slice(0, k.labelChars - 1)}…` : m[2]
    out.push({ n: m[1], label })
  }
  return out.slice(0, k.maxActions)
}

export const register: Register = on => {
  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) {
      const found = parseActions(e.answer, await knobs($))
      await update($, actions, () => found)
    }
    return next(e)
  })

  // Anything Matt sends answers the offer, so the bar clears.
  on('prompt.submit', async ($, e, next) => {
    if ((await read($, actions)).length) await update($, actions, () => [])
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const list = await read($, actions)
    if (e.props.hasSurvey || e.props.isWorking || list.length === 0) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    const send = (text: string) => {
      void update($, actions, () => [])
      void $.prompt.submit({ text, asUser: true, wait: false })
    }
    const all = list.map(a => a.n).join(' ')
    const above = await next(e)
    return (
      <Box flexDirection="column">
        {above}
        <Box flexWrap="wrap">
          <Text dimColor>Reply: </Text>
          {list.map((a, i) => (
            <Box key={a.n}>
              <Button
                key={`a${a.n}`}
                label={`${a.n} · ${a.label}`}
                variant={i === 0 ? 'primary' : 'secondary'}
                onPress={() => send(a.n)}
              />
              <Text> </Text>
            </Box>
          ))}
          {list.length > 1 && <Button key="all" label={`All (${all})`} variant="secondary" onPress={() => send(all)} />}
          <Button key="hide" label="✕" variant="secondary" onPress={() => update($, actions, () => [])} />
        </Box>
        <Text dimColor>Each button sends its number as your reply, same as typing "{list[0].n}" + Enter. Type anything else to answer in words.</Text>
      </Box>
    )
  })
}
