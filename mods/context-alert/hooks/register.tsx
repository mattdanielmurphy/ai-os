import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Cache, Fill, Handoff } from '../types'

// Band shows from WARN; turns red from ALERT. Toasts once per threshold crossed.
const WARN = 150_000
const ALERT = 200_000
const TOAST_AT = [150_000, 200_000, 250_000, 300_000]

// Cache line: only worth showing when a reload would cost something.
const CACHE_MIN_TOKENS = 30_000
const CACHE_SOON_MS = 15 * 60_000 // start the countdown this long before expiry
const DEFAULT_TTL_MS = 60 * 60_000 // every request on this Mac so far used the 1-hour cache
const SEND_ANYWAY_MS = 10 * 60_000 // after a held message, sends go through this long

const fill = atom({ plugin: 'context-alert', key: 'fill' } as const, null)
const lastToast = atom({ plugin: 'context-alert', key: 'lastToast' } as const, 0)
const cache = atom({ plugin: 'context-alert', key: 'cache' } as const, null)
const now = atom({ plugin: 'context-alert', key: 'now' } as const, 0)
const handoff = atom({ plugin: 'context-alert', key: 'handoff' } as const, null)
const sendAnywayUntil = atom({ plugin: 'context-alert', key: 'sendAnywayUntil' } as const, 0)
const held = atom({ plugin: 'context-alert', key: 'held' } as const, '')

export const k = (n: number) => `${Math.round(n / 1000)}k`

export const ago = (ms: number) => {
  const min = Math.round(ms / 60_000)
  if (min < 60) return `${min} min`
  const h = Math.floor(min / 60)
  return h < 48 ? `${h}h` : `${Math.floor(h / 24)} days`
}

/** Minutes left on the cache (negative once expired), or null when it isn't worth a word. */
export const cacheLeft = (c: Cache | null, at: number, tokens: number) => {
  if (c === null || tokens < CACHE_MIN_TOKENS) return null
  return c.lastAt + c.ttlMs - at
}

const script = ($: EngineInterface) => `${$.plugin.root}/../../scripts/cold_handoff.py`

/** Writes a handoff from the transcript file with Haiku; the thread itself is never re-sent. */
const coldHandoff = async ($: EngineInterface, open: boolean): Promise<Handoff> => {
  await update($, handoff, () => ({ status: 'writing', text: 'Writing handoff with Haiku (about a minute)…' }))
  const sid = await $.session.id()
  // Carry the message the person meant to send: the one held, else the draft in the box.
  const draft = (await $.prompt.read()).text.trim()
  const carry = (await read($, held)) || (draft.startsWith('/') ? '' : draft)
  const argv = ['python3', script($), 'write', sid, ...(open ? ['--open'] : []), ...(carry ? ['--then', carry] : [])]
  let result: Handoff
  try {
    const run = await $.process.run(argv, { timeoutMs: 600_000 })
    if (run.exitCode === 0) {
      const { prompt } = JSON.parse(run.stdout) as { path: string; prompt: string }
      result = { status: 'done', text: open ? `New thread opened; paste prompt copied: ${prompt}` : prompt }
      await update($, held, () => '')
    } else {
      result = { status: 'error', text: (run.stderr || run.stdout).trim().slice(0, 300) }
    }
  } catch (err) {
    result = { status: 'error', text: String(err).slice(0, 300) }
  }
  await update($, handoff, () => result)
  return result
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'fresh',
      description: 'Hand this thread off to a new one without reloading it (for a cold cache)',
    })
    $.clock.every(60_000, () => {
      void $.clock.now().then(t => update($, now, () => t))
    })
    // A resumed thread: read when it last answered, and its cache lifetime, from its file.
    void (async () => {
      const t = await $.clock.now()
      await update($, now, () => t)
      const run = await $.process.run(['python3', script($), 'status', await $.session.id()])
      if (run.exitCode !== 0) return
      const s = JSON.parse(run.stdout) as { lastAt: number | null; ttlSec: number; tokens: number }
      if (s.lastAt === null) return
      const fromFile: Cache = { lastAt: s.lastAt, ttlMs: s.ttlSec * 1000, tokens: s.tokens }
      await update($, cache, c => c ?? fromFile)
    })().catch(() => undefined)
    return started
  })

  on('session.measure', async ($, e, next) => {
    const { tokens, window } = e.context
    if (e.changed.includes('context') && tokens !== undefined) {
      const current: Fill = { tokens, window }
      await update($, fill, () => current)

      const crossed = TOAST_AT.filter(t => tokens >= t).pop() ?? 0
      const shown = await read($, lastToast)
      if (crossed > shown) {
        $.ui.toast(`Context is ${k(tokens)} tokens. Time for /_handoff?`)
      }
      if (crossed !== shown) await update($, lastToast, () => crossed)
    }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) {
      const at = await $.clock.now()
      const tokens = (await read($, fill))?.tokens ?? 0
      await update($, cache, c => ({ lastAt: at, ttlMs: c?.ttlMs ?? DEFAULT_TTL_MS, tokens }))
      await update($, now, () => at)
    }
    return next(e)
  })

  // Phone fallback: the band doesn't draw on mobile, so hold the first message sent into a
  // cold thread and say what it would cost. Sending again within 10 min goes through.
  on('prompt.submit', async ($, e, next) => {
    const isPerson = ['composer', 'bridge', 'sdk'].includes(e.origin.kind)
    if (e.command !== undefined || e.isMeta || !isPerson) return next(e)
    const at = await $.clock.now()
    const c = await read($, cache)
    const tokens = Math.max((await read($, fill))?.tokens ?? 0, c?.tokens ?? 0)
    const left = cacheLeft(c, at, tokens)
    if (left === null || left > 0 || at < (await read($, sendAnywayUntil))) return next(e)

    await update($, sendAnywayUntil, () => at + SEND_ANYWAY_MS)
    await update($, held, () => e.text)
    await $.prompt.fill({ text: e.text, mode: 'replace' }).catch(() => undefined)
    return {
      drop:
        `Held: this thread's cache expired ${ago(-left)} ago, so this message would re-send ` +
        `~${k(tokens)} tokens at full price. Send it again to go ahead, or send /fresh to ` +
        `hand off to a new thread cheaply (this message goes with it).`,
    }
  })

  on('command.run', { command: 'fresh' }, async $ => {
    const result = await coldHandoff($, false)
    if (result.status === 'error') return { text: `Cold handoff failed: ${result.text}` }
    return { text: `Handoff written without reloading this thread. Start a new thread with:\n\n${result.text}` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const current = await read($, fill)
    const c = await read($, cache)
    await read($, now) // subscribes the band to the minute tick
    const at = await $.clock.now()
    const job = await read($, handoff)
    const tokens = Math.max(current?.tokens ?? 0, c?.tokens ?? 0)
    const left = cacheLeft(c, at, tokens)
    const showCache = left !== null && left <= CACHE_SOON_MS
    const showSize = current !== null && current.tokens >= WARN
    if (!showCache && !showSize && job === null) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const isAlert = current !== null && current.tokens >= ALERT
    const isCold = left !== null && left <= 0

    return (
      <Box flexDirection="column">
        {showSize && current !== null && (
          <Box>
            <Text bold color={isAlert ? 'error' : 'warning'}>
              ⚠ Current context size: {k(current.tokens)} / {k(current.window)} (
              {isAlert ? 'hand off now' : 'getting long'}){' '}
            </Text>
            <Button
              key="handoff"
              label="Write handoff"
              onPress={() => $.prompt.fill({ text: '/_handoff', mode: 'replace' })}
            />
          </Box>
        )}
        {showCache && left !== null && (
          <Box>
            <Text bold color={isCold ? 'error' : 'warning'}>
              {isCold
                ? `❄ Cache expired ${ago(-left)} ago: next message re-sends ~${k(tokens)} tokens at full price `
                : `⏳ Cache expires in ${ago(left)} `}
            </Text>
            <Button
              key="fresh"
              label="Fresh thread"
              variant={isCold ? 'primary' : 'secondary'}
              onPress={() => void coldHandoff($, true)}
            />
          </Box>
        )}
        {job !== null && (
          <Box>
            <Text color={job.status === 'error' ? 'error' : undefined} dimColor={job.status === 'writing'}>
              {job.status === 'done' ? `✓ ${job.text} ` : `${job.text} `}
            </Text>
            {job.status !== 'writing' && (
              <Button key="dismiss" label="OK" onPress={() => update($, handoff, () => null)} />
            )}
          </Box>
        )}
      </Box>
    )
  })
}
