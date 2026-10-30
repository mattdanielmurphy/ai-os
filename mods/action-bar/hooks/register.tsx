import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Action } from '../types'

const actions = atom({ plugin: 'action-bar', key: 'actions' } as const, [] as Action[])

// Knobs live in ~/.hammerspoon/tweaks/action_bar.json (⌃⌥⌘T panel); missing or bad JSON keeps these.
export const KNOB_DEFAULTS = { maxActions: 6 }
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
 * The actions line: the last line of the reply that starts with "Actions:" (bold allowed),
 * items split by " · ", each "Short label → Plain sentence sent on click". Without the
 * arrow the click sends "Yes, <label>". Ordinary numbered lists never raise the bar.
 * Items split by " | " are either/or: those (and any pair of two) get no "All of these".
 */
export const parseActions = (answer: string, k: Knobs = KNOB_DEFAULTS): Action[] => {
  const lines = answer.split('\n').map(strip).filter(Boolean)
  const line = [...lines].reverse().find(l => /^actions\s*:/i.test(l))
  if (!line) return []
  const out: Action[] = []
  const body = line.replace(/^actions\s*:/i, '')
  const either = /\s\|\s/.test(body)
  // New format (2026-10-29): "1, Build our own voice; 2, Try the listening hack". Each item is
  // the prompt sent on click, and the button shows all of it. Read aloud speaks it as written.
  if (/^\s*1,\s/.test(body)) {
    for (const raw of body.split(/\s*[;|]\s*(?=\d{1,2},\s)/)) {
      const said = raw.replace(/^\s*\d{1,2},\s*/, '').replace(/[.;]\s*$/, '').trim()
      if (!said) continue
      out.push({ label: said, text: said, ...(either ? { either } : {}) })
    }
    return out.slice(0, k.maxActions)
  }
  for (const raw of body.split(/\s[·•|]\s/)) {
    const part = raw.replace(/^\s*\d{1,2}[.)]\s+/, '').trim()
    if (!part) continue
    const [head, ...rest] = part.split(/\s*(?:→|->)\s*/)
    const said = rest.join(' ').trim()
    out.push({ label: head, text: said || `Yes, ${head.charAt(0).toLowerCase()}${head.slice(1)}`, ...(either ? { either } : {}) })
  }
  return out.slice(0, k.maxActions)
}

/** The reply without its Actions line: the buttons say it already, and Read aloud shouldn't. */
export const hideActions = (text: string): string =>
  text
    .split('\n')
    .filter(l => !/^\s*actions\s*:/i.test(strip(l)))
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trimEnd()

export const register: Register = on => {
  on('ui.render', { component: 'AssistantMessage' }, async ($, e, next) => {
    const text = hideActions(e.props.text)
    return text === e.props.text ? next(e) : next({ ...e, props: { ...e.props, text } })
  })

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
    const all = `Yes to all: ${list.map(a => a.text.replace(/^yes,?\\s*/i, '').replace(/[.!]$/, '')).join('; ')}.`
    const above = await next(e)
    // One compact row, shared with the other bands (read-aloud's speaker joins it).
    return (
      <Box flexWrap="wrap" rowGap="xs" alignItems="center">
        {above}
        {list.map((a, i) => (
          <Box key={`b${i}`} maxWidth="100%" flexShrink={1}>
            <Button key={`a${i + 1}`} label={a.label} variant="secondary" onPress={() => send(a.text)}>
              <Text wrap="wrap">{a.label}</Text>
            </Button>
            <Text> </Text>
          </Box>
        ))}
        {list.length > 2 && !list.some(a => a.either) && <Button key="all" label="All of these" variant="secondary" onPress={() => send(all)} />}
        <Button key="hide" label="✕" plain dimColor onPress={() => update($, actions, () => [])} />
      </Box>
    )
  })
}
