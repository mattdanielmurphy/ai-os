import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { PromptMedia, PromptSubmitAttachment, PromptSubmitInput, PromptSubmitResult } from 'claude-code'

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
const projectHeld = atom({ plugin: 'context-alert', key: 'projectHeld' } as const, '')
const inProject = atom({ plugin: 'context-alert', key: 'inProject' } as const, false)

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

const unescape = (t: string) =>
  t.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;|&#34;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')

/** What Matt wrote, and where, out of a project <wake> envelope. */
export const wakeParts = (text: string) => {
  const body = /<message trigger="true"[^>]*>([\s\S]*?)<\/message>/.exec(text)?.[1]
  const id = /<message trigger="true"[^>]*\bid="(cmsg_[A-Za-z0-9]+)"/.exec(text)?.[1]
  const thread = /<thread\b[^>]*\b(?:ts|id)="(cmsg_[A-Za-z0-9]+)"/.exec(text)?.[1]
  return { body: unescape((body ?? text).trim()), id, thread }
}

/** The coordinator's note, after it started the fresh thread, naming that thread. The mod answers
 *  it itself so this cold thread's model never runs. */
export const handedOff = (text: string) =>
  /^\s*<relay from="coordinator"/.test(text)
    ? /context-alert handed-off:\s*(cmsg_[A-Za-z0-9]+)/.exec(text)?.[1]
    : undefined

/** Which project wake this is: mention, reactions, message-edited, ... */
export const wakeReason = (text: string) => /^\s*<wake\b[^>]*\breason="([^"]+)"/.exec(text)?.[1] ?? ''

/** Emoji a person (not an agent) put on a message, from a reactions wake. Reactions and edits
 *  arrive as system turns (isMeta), not as Matt typing, so the person-only gate never saw them. */
export const reactionEmoji = (text: string) =>
  [...text.matchAll(/<reaction\b[^>]*\bemoji="([^"]+)"[^>]*\breactors="(user_[^"]*)"/g)].map(m => m[1])

/** What a wake means for a held message: Matt's answer, an edit of the held text, or neither. */
export const heldWake = (text: string, heldId?: string): 'answer' | 'edit' | 'other' => {
  const reason = wakeReason(text)
  if (reason === 'reactions') return reactionEmoji(text).length ? 'answer' : 'other'
  if (reason === 'message-edited') return heldId !== undefined && wakeParts(text).id === heldId ? 'edit' : 'other'
  return 'other'
}

/** A reply that only picks an option, so it adds nothing for the new thread to act on. */
const bareAnswer = (body: string) =>
  /^\W*(fresh|new( thread)?|yes|yep|yeah|ok(ay)?|sure|do it|go for it|sounds good|👍|fresh thread)?\W*$/iu.test(body)

/** Matt's answer to a held message. A fresh thread from the handoff is the default (it starts on
 *  its own once the handoff is written, Matt 2026-10-22; 👍, "fresh" or any other reply sends it
 *  sooner); only ⏩ or "here"/"go" continues in this cold thread. */
export const wantsFresh = (text: string) =>
  !(/⏩|fast_forward/.test(text) || /^\W*(here|go)\W*$/i.test(wakeParts(text).body))

/** ❌ on the hold note: drop the held message. ✋ (wait, typing more) or 👀: keep holding. */
export const heldReaction = (text: string): 'cancel' | 'wait' | null => {
  const emoji = reactionEmoji(text).join('')
  if (/❌|✖/.test(emoji) && !/⏩|👍/.test(emoji)) return 'cancel'
  if (/✋|👀/.test(emoji) && !/⏩|👍/.test(emoji)) return 'wait'
  return null
}

/** The thread reply that tells Matt his message is moving to a fresh thread. */
export const heldReply = (expiredMs: number, tokens: number) =>
  `❄️ **Cache expired ${ago(expiredMs)} ago, so this moves to a fresh thread.** Nothing sent here; ` +
  `Sonnet is writing the handoff.\n\n⏩ continue here instead (re-reads ~${k(tokens)} tokens)\n\n❌ drop it`

/** The line the old thread ends on, once the coordinator says where the work went. */
export const handedOffReply = (thread: string) =>
  `➡️ **Handed off to [the new thread](#${thread}) because the cache expired.**`

/** What the coordinator gets when a held message moves to a fresh thread. */
export const freshAsk = (held: string, heldId: string, prompt: string, followUp = '', parent = '') =>
  `Matt chose a fresh thread for a message he wrote into a cold thread (context-alert held it and ` +
  `moved it by default; that thread never ran). Please start a new thread on his message ` +
  `${heldId || '(no id)'} with a brief that says: first do this, then answer him: ${prompt}\n\n` +
  `His held message: ${held}` +
  (followUp ? `\n\nHe added, in the same thread while it was held: ${followUp}` : '') +
  (parent
    ? `\n\nLinks: make the new thread's ack "Continued from [the old thread](#${parent}) because its ` +
      `cache expired." Then message_thread the old thread (${parent}) with exactly: ` +
      `context-alert handed-off: <the new thread's id>. The mod there posts the link without waking its model.`
    : '')

/** Writes a handoff from the transcript file with Sonnet; the thread itself is never re-sent. */
const coldHandoff = async ($: EngineInterface, open: boolean): Promise<Handoff> => {
  await update($, handoff, () => ({ status: 'writing', text: 'Writing handoff with Sonnet (about a minute)…' }))
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
      result = { status: 'done', prompt, text: open ? 'New thread opened with the handoff typed in; press Enter to start it.' : `${prompt}\n\n[Open it in a new thread](${link})` }
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

/** /cold-handoff (and its old names /haiku-handoff and /fresh). */
const coldCommand = async ($: EngineInterface) => {
  const result = await coldHandoff($, false)
  if (result.status === 'error') return { text: `Cold handoff failed: ${result.text}` }
  return { text: `Handoff written without reloading this thread. Click the link (press Enter there to start), or paste:\n\n${result.text}` }
}

type Held = { body: string; id?: string; thread?: string }

/** The handoff Sonnet starts writing as soon as a project message is held. */
let backgroundHandoff: Promise<Handoff> | null = null
/** Bumped on every hold and every answer, so the automatic move only fires for its own hold. */
let holdSeq = 0
/** ✋ on the hold note: don't move it on its own, wait for Matt's next message. */
let holdWaiting = false

const startHandoff = ($: EngineInterface) => {
  backgroundHandoff = coldHandoff($, false).catch((err): Handoff => ({ status: 'error', text: String(err) }))
}

/** Asks the coordinator for a fresh thread from the handoff. The old thread's last line, with the
 *  link, comes when the coordinator answers (see handedOff). */
const sendFresh = async ($: EngineInterface, h: Held, added = ''): Promise<boolean> => {
  let job = await (backgroundHandoff ?? coldHandoff($, false))
  backgroundHandoff = null
  if (job.status !== 'done') job = await coldHandoff($, false)
  if (job.status !== 'done') {
    await $.tool.call({ tool: 'mcp__hearthbot__reply', text: `⚠️ **Handoff failed:** ${job.text}\n\n⏩ continue here, or send anything to retry.` })
      .catch(() => undefined)
    return false
  }
  await $.tool.call({
    tool: 'mcp__claude-code-remote__send_message',
    session_id: '@parent', visibility: 'sent_to_shared_agent',
    message: freshAsk(h.body, h.id ?? '', job.prompt ?? job.text, added, h.thread ?? ''),
  }).catch(() => undefined)
  return true
}

/** The default: once the handoff is written, move the held message on its own (Matt, 2026-10-22:
 *  no 👍 needed). Skipped if Matt answered, edited or said ✋ meanwhile. */
const autoFresh = async ($: EngineInterface, seq: number) => {
  await backgroundHandoff
  if (seq !== holdSeq || holdWaiting) return
  const pending = await read($, projectHeld)
  if (!pending || seq !== holdSeq) return
  holdSeq++
  if (await sendFresh($, JSON.parse(pending) as Held)) await update($, projectHeld, () => '')
  else holdSeq-- // keep it held so ⏩ or a retry still works
}

/** Matt answered a held project message: send it on here, or hand off to a fresh thread now. */
const answerHeld = async (
  $: EngineInterface, e: PromptSubmitInput, next: (e: PromptSubmitInput) => Promise<PromptSubmitResult>,
  w: Held,
): Promise<PromptSubmitResult> => {
  const reaction = wakeReason(e.text) === 'reactions' ? heldReaction(e.text) : null
  if (reaction === 'wait') {
    holdWaiting = true
    return { drop: 'Still held: Matt reacted ✋/👀, waiting for his next message.' }
  }
  holdSeq++
  holdWaiting = false
  await update($, projectHeld, () => '')
  if (reaction === 'cancel') {
    await update($, held, () => '')
    backgroundHandoff = null
    await $.tool.call({ tool: 'mcp__hearthbot__reply', text: 'Dropped. Your held message was never sent.' }).catch(() => undefined)
    return { drop: 'Held message dropped (Matt reacted ❌).' }
  }
  if (!wantsFresh(e.text)) {
    await update($, held, () => '')
    return next({ ...e, context: [...(e.context ?? []), `[context-alert] Matt said go ahead. His message held while this thread was cold: ${w.body}`] })
  }
  const added = wakeReason(e.text) === 'reactions' ? '' : wakeParts(e.text).body
  if (!(await sendFresh($, w, bareAnswer(added) ? '' : added))) {
    await update($, projectHeld, () => JSON.stringify(w))
    return { drop: 'Handoff failed; message still held.' }
  }
  return { drop: 'Fresh thread requested from the coordinator; this thread stays cold.' }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'cold-handoff',
      description: 'Sonnet writes the handoff from the saved transcript; this thread is never re-sent',
    })
    await $.command.register({ name: 'haiku-handoff', description: 'Old name for /cold-handoff' })
    await $.command.register({ name: 'fresh', description: 'Old name for /cold-handoff' })
    $.clock.every(60_000, () => {
      void $.clock.now().then(t => update($, now, () => t))
    })
    // A resumed thread: read when it last answered, and its cache lifetime, from its file.
    void (async () => {
      const t = await $.clock.now()
      await update($, now, () => t)
      const run = await $.process.run(['python3', script($), 'status', await $.session.id()])
      if (run.exitCode !== 0) return
      const s = JSON.parse(run.stdout) as { lastAt: number | null; ttlSec: number; tokens: number; project?: boolean }
      if (s.project) await update($, inProject, () => true)
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
    if (e.command !== undefined) return next(e)
    const moved = handedOff(e.text)
    if (moved !== undefined) {
      await $.tool.call({ tool: 'mcp__hearthbot__reply', text: handedOffReply(moved) }).catch(() => undefined)
      return { drop: `Handed off to ${moved}; the coordinator's note was answered by the mod.` }
    }
    const isPerson = ['composer', 'bridge', 'sdk'].includes(e.origin.kind) && !e.isMeta
    // A project thread is known by any earlier <wake>, not only this message's: after the Mac
    // reconnects, a queued message can arrive without the envelope and was held the Code-tab
    // way, so a second message slipped through as "send again" (2026-10-22).
    if (isProjectMessage(e.text)) await update($, inProject, () => true)
    const project = isProjectMessage(e.text) || (await read($, inProject))
    const pending = project ? await read($, projectHeld) : ''
    if (pending) {
      const h = JSON.parse(pending) as Held
      const kind = isPerson ? 'answer' : heldWake(e.text, h.id)
      if (kind === 'answer') return answerHeld($, e, next, h)
      if (kind === 'edit') {
        // Matt edited the held message: hold the new text instead and rewrite the handoff.
        const edited = { ...h, body: wakeParts(e.text).body }
        await update($, projectHeld, () => JSON.stringify(edited))
        await update($, held, () => edited.body)
        startHandoff($)
        void autoFresh($, ++holdSeq)
        return { drop: 'Held message edited; still held with the new text.' }
      }
    }
    if (!isPerson) return next(e)

    const at = await $.clock.now()
    const c = await read($, cache)
    const tokens = Math.max((await read($, fill))?.tokens ?? 0, c?.tokens ?? 0)
    const left = cacheLeft(c, at, tokens)
    if (left === null || left > 0 || at < (await read($, sendAnywayUntil))) return next(e)

    // A Claude project thread: the Code tab's hold note never shows on the project page, so the
    // mod says it in the thread itself and moves the message to a fresh thread unless Matt says ⏩.
    if (project) {
      await $.process.run(['mkdir', '-p', HELD_DIR]).catch(() => undefined)
      await $.process.run(['sh', '-c', `cat >> ${HELD_DIR}/holds.log`], { stdin: `${new Date(at).toISOString()} ${JSON.stringify(e.text.slice(0, 300))}\n` })
        .catch(() => undefined)
      const w = wakeParts(e.text)
      const posted = await $.tool.call({ tool: 'mcp__hearthbot__reply', text: heldReply(-left, tokens) })
        .then(() => true, () => false)
      if (!posted) return next(e)
      await update($, projectHeld, () => JSON.stringify(w))
      await update($, held, () => w.body)
      holdWaiting = false
      startHandoff($)
      void autoFresh($, ++holdSeq)
      return { drop: `Held (project thread): cache expired ${ago(-left)} ago, ~${k(tokens)} tokens. Moving it to a fresh thread.` }
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
        `~${k(tokens)} tokens at full price. Send it again to go ahead, or send /cold-handoff ` +
        `to hand off to a new thread cheaply (this message goes with it).` + extra,
    }
  })

  on('command.run', { command: 'cold-handoff' }, coldCommand)
  on('command.run', { command: 'haiku-handoff' }, coldCommand)
  on('command.run', { command: 'fresh' }, coldCommand)

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
      ? `This agent would re-read ~${k(tokens)} at full price; Sonnet reads the saved file instead.`
      : 'This agent: best notes, cheap while the cache is warm. Sonnet: never re-sends the thread.'

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
              key="sonnet"
              label="Handoff by Sonnet"
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
