import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { PromptMedia, PromptSubmitAttachment } from 'claude-code'

import type { Cache, Fill, Handoff } from '../types'

// Band shows from WARN; turns red from ALERT. Toasts once per threshold crossed.
// Set high on purpose: a warm thread re-reads its context at the cache price (a tenth), while a
// new thread pays full price to re-read files plus a minute of ramp-up. Hand off at a stopping
// point, not mid-task; the nudge only needs to land before a long thread gets slow and sloppy.
const WARN = 250_000
const ALERT = 400_000
const TOAST_AT = [250_000, 400_000, 550_000]

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

// The app runs an installed copy from ~/.claude/plugins/cache, so point at the repo itself.
const AIOS = '/Users/matt/projects/ai-os'
const script = (_$: EngineInterface) => `${AIOS}/scripts/cold_handoff.py`
const HELD_DIR = `${AIOS}/tmp/held`

const EXT: Record<string, string> = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/gif': 'gif', 'image/webp': 'webp', 'application/pdf': 'pdf' }

/**
 * Saves a held message's images and files to disk, so the new thread can open them.
 * Reading their bytes is answered only to a managed settings install; otherwise each
 * comes back by name as one to re-attach.
 */
export const saveAttachments = async (
  $: EngineInterface, items: readonly PromptSubmitAttachment[], at: number,
): Promise<{ saved: string[]; missed: string[] }> => {
  const saved: string[] = []
  const missed: string[] = []
  for (const [i, item] of items.entries()) {
    const name = item.filename ?? `${item.type} ${i + 1}`
    let b64 = ''
    let mediaType = item.mediaType ?? ''
    let offset: number | undefined = 0
    while (item.id !== undefined && offset !== undefined) {
      const part: PromptMedia = await $.prompt.media({ id: item.id, offset }).catch(() => ({ deny: 'failed' }))
      if (part.base64 === undefined) { b64 = ''; break }
      b64 += part.base64
      mediaType = part.mediaType
      offset = part.next
    }
    if (!b64) { missed.push(name); continue }
    const ext = EXT[mediaType] ?? mediaType.split('/')[1] ?? 'bin'
    const out = `${HELD_DIR}/${at}-${i + 1}.${ext}`
    await $.process.run(['mkdir', '-p', HELD_DIR])
    const run = await $.process.run(['base64', '-D', '-o', out], { stdin: b64 })
    if (run.exitCode === 0) saved.push(out)
    else missed.push(name)
  }
  return { saved, missed }
}

/** The held message as the new thread should read it: the text, then what came with it. */
export const withFiles = (text: string, files: { saved: string[]; missed: string[] }) => {
  const lines = [text]
  if (files.saved.length) lines.push(`(Attached in the old thread, saved here: ${files.saved.join(', ')})`)
  if (files.missed.length) lines.push(`(Not carried over, ask me to re-attach: ${files.missed.join(', ')})`)
  return lines.join('\n\n')
}

/** Claude project threads deliver each message wrapped in a <wake> envelope. */
export const isProjectMessage = (text: string) => text.trimStart().startsWith('<wake')

/** Context for the thread's model when a project message arrived into a cold cache. */
export const projectColdNote = (expiredMs: number, tokens: number) =>
  `[context-alert] This thread's prompt cache expired ${ago(expiredMs)} ago, so this turn ` +
  `re-sent ~${k(tokens)} tokens at full price (roughly 20 warm messages' worth). Open your reply ` +
  `with one short plain line saying so, and that if Matt replies "fresh" you'll write a /_handoff ` +
  `and he can continue in a new thread. Then answer as usual.`

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
      const { prompt, link } = JSON.parse(run.stdout) as { path: string; prompt: string; link: string }
      result = { status: 'done', text: open ? 'New thread opened with the handoff typed in; press Enter to start it.' : `${prompt}\n\n[Open it in a new thread](${link})` }
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

/** /haiku-handoff (and its old name /fresh). */
const haikuCommand = async ($: EngineInterface) => {
  const result = await coldHandoff($, false)
  if (result.status === 'error') return { text: `Cold handoff failed: ${result.text}` }
  return { text: `Handoff written without reloading this thread. Click the link (press Enter there to start), or paste:\n\n${result.text}` }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'haiku-handoff',
      description: 'Haiku writes the handoff from the saved transcript; this thread is never re-sent',
    })
    await $.command.register({ name: 'fresh', description: 'Old name for /haiku-handoff' })
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
        $.ui.toast(`Context is ${k(tokens)} tokens. At your next stopping point, consider /_handoff.`)
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

    // A Claude project thread: the hold note shows only in the Code tab, never on the project
    // page, and the project re-delivers the message anyway. Let it through and have the reply
    // say what the cold read cost, so Matt can choose a fresh thread next time.
    if (isProjectMessage(e.text)) {
      return next({ ...e, context: [...(e.context ?? []), projectColdNote(-left, tokens)] })
    }

    await update($, sendAnywayUntil, () => at + SEND_ANYWAY_MS)
    const files = await saveAttachments($, e.attachments ?? [], at)
    await update($, held, () => withFiles(e.text, files))
    const extra = files.missed.length
      ? ` ${files.missed.length} attachment(s) can't be carried over; re-attach them there.`
      : ''
    await $.prompt.fill({ text: e.text, mode: 'replace' }).catch(() => undefined)
    return {
      drop:
        `Held: this thread's cache expired ${ago(-left)} ago, so this message would re-send ` +
        `~${k(tokens)} tokens at full price. Send it again to go ahead, or send /haiku-handoff ` +
        `to hand off to a new thread cheaply (this message goes with it).` + extra,
    }
  })

  on('command.run', { command: 'haiku-handoff' }, haikuCommand)
  on('command.run', { command: 'fresh' }, haikuCommand)

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

    const hint = isCold
      ? `This agent would re-read ~${k(tokens)} at full price; Haiku reads the saved file instead.`
      : 'This agent: best notes, cheap while the cache is warm. Haiku: faster, never re-sends the thread.'

    return (
      <Box flexDirection="column">
        {showSize && current !== null && (
          <Text bold color={isAlert ? 'error' : 'warning'}>
            ⚠ Context: {k(current.tokens)} / {k(current.window)} (
            {isAlert ? 'hand off at the next stopping point' : 'getting long'})
          </Text>
        )}
        {showCache && left !== null && (
          <Text bold color={isCold ? 'error' : 'warning'}>
            {isCold
              ? `❄ Cache expired ${ago(-left)} ago: next message re-sends ~${k(tokens)} tokens at full price`
              : `⏳ Cache expires in ${ago(left)}`}
          </Text>
        )}
        {(showSize || showCache) && (
          <Box>
            <Button
              key="handoff"
              label="Handoff by this agent"
              variant={isCold ? 'secondary' : 'primary'}
              onPress={() => $.prompt.fill({ text: '/_handoff', mode: 'replace' })}
            />
            <Text> </Text>
            <Button
              key="haiku"
              label="Handoff by Haiku"
              variant={isCold ? 'primary' : 'secondary'}
              onPress={() => void coldHandoff($, true)}
            />
            <Text dimColor> {hint}</Text>
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
