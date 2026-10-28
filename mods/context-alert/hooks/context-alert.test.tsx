import { expect, mock, test } from 'claude-code/testing'

import { KNOB_DEFAULTS, asksMatt, compactDue, queueCommand } from './register'

const BAND = {
  component: 'AbovePrompt',
  props: {
    hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 }, view: {},
  },
} as const

const measure = (tokens: number) => ({
  context: { tokens, window: 1_000_000, percent: Math.round(tokens / 10_000) },
  rateLimits: [],
  changed: ['context' as const],
})

const MIN = 60_000

// A message sent from the phone, through the Remote Control bridge.
const phone = (text: string) => ({ text, wait: false, origin: { kind: 'bridge' as const } })

const answered = {
  answer: 'done', durationMs: 1000, isAborted: false, turnId: 't1', reason: 'answer' as const,
}

test('band stays hidden under 250k and appears above it', async ($, on) => {
  mock.clock(on)
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  for (const surface of ['terminal', 'desktop'] as const) {
    await $.session.measure(measure(90_000))
    let ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect(await ui.find({ type: 'Text', text: /Context: / })).toBeUndefined()
    await ui.unmount()

    await $.session.measure(measure(262_000))
    ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Context: / }))?.text).toMatch(/262k \/ 1000k/)
    expect(await ui.find({ key: 'handoff' })).toBeDefined()
    expect(await ui.find({ key: 'sonnet' })).toBeDefined()
    expect((await ui.find({ type: 'Text', text: /This agent: best notes/ }))).toBeDefined()
    await ui.unmount()
  }
})

test('cache line counts down after a reply, then says it expired', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  await $.session.measure(measure(80_000))
  await $.turn.complete(answered)

  for (const surface of ['terminal', 'desktop'] as const) {
    let ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect(await ui.find({ type: 'Text', text: /Cache/ })).toBeUndefined()
    await ui.unmount()
  }

  await clock.advance(50 * MIN)
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Cache/ }))?.text).toMatch(/expires in 10 min/)
    expect(await ui.find({ key: 'sonnet' })).toBeDefined()
    await ui.unmount()
  }

  await clock.advance(3 * 60 * MIN)
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Cache/ }))?.text).toMatch(/expired 2h ago.*80k tokens/)
    expect(await ui.find({ type: 'Text', text: /Sonnet reads the saved file/ })).toBeDefined()
    await ui.unmount()
  }
})

test('small threads never get a cache line', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  await $.session.measure(measure(12_000))
  await $.turn.complete(answered)
  await clock.advance(5 * 60 * MIN)
  const ui = await $.ui.mount({ plugin: 'context-alert', surface: 'desktop', ...BAND })
  expect(await ui.find({ type: 'Text', text: /Cache/ })).toBeUndefined()
})

test('a message sent into a cold thread is held once, then goes through', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  const entered: string[] = []
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on("prompt.fill", () => ({ isFilled: true }))
  on('prompt.submit', (_$, e) => { entered.push(e.text); return { text: e.text } })
  await $.session.measure(measure(300_000))
  await $.turn.complete(answered)

  await clock.advance(30 * MIN)
  expect((await $.prompt.submit(phone('warm'))).drop).toBeUndefined()

  await clock.advance(2 * 60 * MIN)
  const held = await $.prompt.submit(phone('cold'))
  expect(held.drop).toMatch(/expired 1h ago.*300k tokens.*\/cold-handoff/)
  expect((await $.prompt.submit(phone('cold'))).drop).toBeUndefined()
  expect(entered).toEqual(['warm', 'cold'])
})

const wake = (body: string, id = 'cmsg_M1') =>
  '<wake reason="mention">\n  <project id="chan_1" type="project">\n    <thread ts="cmsg_T1">\n' +
  `      <message trigger="true" from="human" id="${id}" mention="true">${body}</message>\n` +
  '    </thread>\n  </project>\n</wake>'

const projectSetup = async ($: any, on: any) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  const entered: { text: string; context?: readonly string[] }[] = []
  const calls: Record<string, unknown>[] = []
  on('session.measure', (_$: unknown, e: any) => ({ changed: e.changed }))
  on('turn.complete', (_$: unknown, e: any) => ({ text: e.answer }))
  on('prompt.read', () => ({ value: { text: '', cursor: 0 } }))
  on('session.id', () => ({ value: 's1' }))
  on('prompt.submit', (_$: unknown, e: any) => { entered.push({ text: e.text, context: e.context }); return { text: e.text } })
  on('tool.call', (_$: unknown, e: any) => { calls.push(e); return { result: 'ok' } })
  // The handoff takes about a minute for real; here it waits until the test calls finish().
  let finish = () => {}
  const written = new Promise<void>(r => { finish = r })
  on('process.run', async (_$: unknown, e: any) => {
    if (e.argv.includes('write')) await written
    const stdout = JSON.stringify({ path: '/h.md', prompt: 'Read /h.md and continue. Then: is it done?' })
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false } }
  })
  await $.session.measure(measure(300_000))
  await $.turn.complete(answered)
  await clock.advance(3 * 60 * MIN)
  const settle = async () => { finish(); for (let i = 0; i < 50; i++) await new Promise(r => setTimeout(r, 0)) }
  return { clock, entered, calls, settle }
}

test('a cold project message is held and Matt is asked in the thread; "here" sends it on', async ($, on) => {
  const { entered, calls } = await projectSetup($, on)
  const out = await $.prompt.submit(phone(wake('is it done?')))
  expect(out.drop).toMatch(/Held \(project thread\)/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__hearthbot__reply')
  expect(String(ask?.text)).toMatch(/expired 2h ago, so this moves to a fresh thread.*~300k tokens/s)

  expect((await $.prompt.submit(phone(wake('here', 'cmsg_M2')))).drop).toBeUndefined()
  expect(entered).toHaveLength(1)
  expect(entered[0].context?.join('\n')).toMatch(/Matt said go ahead.*is it done\?/)
})

test('any other reply (the default) asks the coordinator for a new thread from the handoff', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  const pending = $.prompt.submit(phone(wake('sounds good', 'cmsg_M2')))
  await settle()
  const out = await pending
  expect(out.drop).toMatch(/Fresh thread requested/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(ask?.session_id).toBe('@parent')
  expect(String(ask?.message)).toMatch(/message cmsg_M1.*Read \/h\.md and continue.*His held message: is it done\?/s)
})

// Reactions and edits come in as system turns (isMeta), exactly as the app delivers them.
const system = (text: string) => ({ text, wait: false, isMeta: true, origin: { kind: 'sdk' as const } })
const reacted = (emoji: string, reactors = 'user_M') =>
  '<wake reason="reactions" current-time="t">\n  <project id="chan_1" type="project">\n    <thread ts="cmsg_T1"></thread>\n  </project>\n' +
  `  <reactions channel="chan_1" thread_ts="cmsg_T1">\n    <reaction emoji="${emoji}" count="1" message_ts="cmsg_HOLD" message_from="Claude (you)" reactors="${reactors}"></reaction>\n  </reactions>\n</wake>`
const edited = (body: string, id = 'cmsg_M1') => wake(body, id).replace('reason="mention"', 'reason="message-edited"')

test('with no answer, the held message moves to a fresh thread once the handoff is written', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect(calls.some(c => c.tool === 'mcp__claude-code-remote__send_message')).toBe(false)
  await settle()
  const asks = calls.filter(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(asks).toHaveLength(1)
  expect(String(asks[0].message)).toMatch(/His held message: is it done\?.*cmsg_T1.*context-alert handed-off:/s)
  expect(entered).toHaveLength(0)
  // Answered and cleared: a later message is not treated as an answer to it.
  expect((await $.prompt.submit(system(reacted('👍')))).drop).toBeUndefined()
})

test('⏩ before the handoff is written keeps it here; nothing moves', async ($, on) => {
  const { calls, entered, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect((await $.prompt.submit(system(reacted('⏩')))).drop).toBeUndefined()
  await settle()
  expect(calls.some(c => c.tool === 'mcp__claude-code-remote__send_message')).toBe(false)
  expect(entered).toHaveLength(1)
})

test('✋ stops the automatic move until his next message', async ($, on) => {
  const { calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  await $.prompt.submit(system(reacted('✋')))
  await settle()
  expect(calls.some(c => c.tool === 'mcp__claude-code-remote__send_message')).toBe(false)
  expect((await $.prompt.submit(phone(wake('ok go', 'cmsg_M2')))).drop).toMatch(/Fresh thread requested/)
})

test("the coordinator's handed-off note gets the link line, and never reaches the model", async ($, on) => {
  const { calls, entered } = await projectSetup($, on)
  const note = '<relay from="coordinator" session="s" current-time="t" reason="relay">\n  <note>context-alert handed-off: cmsg_NEW1</note>\n</relay>'
  const out = await $.prompt.submit(system(note))
  expect(out.drop).toMatch(/Handed off to cmsg_NEW1/)
  expect(entered).toHaveLength(0)
  const line = calls.find(c => c.tool === 'mcp__hearthbot__reply')
  expect(String(line?.text)).toMatch(/Handed off to \[the new thread\]\(#cmsg_NEW1\) because the cache expired/)
})

// How Remote Control really delivers it (seen 2026-10-22): a task notification, wrapped.
const delivered = (note: string) => ({
  text: `<project_claude_message session="s" thread_id="cmsg_OLD">\n<relay from="coordinator" session="s" current-time="t">\n  <note>\n      ${note}\n  </note>\n</relay>\n</project_claude_message>\n`,
  wait: false, origin: { kind: 'task-notification' as const },
})

test('the wrapped handed-off note posts the forward link and resolves the old thread again', async ($, on) => {
  const { calls, entered } = await projectSetup($, on)
  const out = await $.prompt.submit(delivered('context-alert handed-off: cmsg_NEW2'))
  expect(out.drop).toMatch(/Handed off to cmsg_NEW2/)
  expect(entered).toHaveLength(0)
  expect(String(calls.find(c => c.tool === 'mcp__hearthbot__reply')?.text)).toMatch(/\(#cmsg_NEW2\)/)
  expect(calls.find(c => c.tool === 'mcp__hearthbot__set_thread_resolved')?.resolved).toBe(true)
})

test('the new thread opens on the Mac behind the light pill', async ($, on) => {
  const runs: string[][] = []
  on('tool.call', () => ({ result: 'ok' }))
  on('process.run', (_$: unknown, e: any) => {
    runs.push(e.argv)
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false } }
  })
  const id = 'cmsg_01CUPXyY9oUwKVDFREVDpYDrBzsyKb2XkAhavByAdGw1cD'
  await $.prompt.submit(delivered(`context-alert handed-off: ${id}`))
  for (let i = 0; i < 10; i++) await new Promise(r => setTimeout(r, 0))
  const argv = runs.find(r => r[3] === 'open-thread')
  expect(argv?.[2]).toMatch(/ask .* --light --thread "\$1"\) \|\| exit 0; open "\$2"; .* done/)
  expect(argv?.slice(4)).toEqual([id, `claude://code/project/chan_01CUPXyY9oUwKVDFREVDpYDr?thread=${id}`])
})

test('a fresh thread from a cold handoff opens with a link back, once', async ($, on) => {
  const calls: Record<string, unknown>[] = []
  const entered: string[] = []
  on('prompt.submit', (_$: unknown, e: any) => { entered.push(e.text); return { text: e.text } })
  on('tool.call', (_$: unknown, e: any) => { calls.push(e); return { result: 'ok' } })
  on('process.run', (_$: unknown, e: any) => {
    const stdout = e.argv[0] === 'grep' ? '<!-- context-alert parent-thread: cmsg_OLD9 -->\n' : ''
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false } }
  })
  const brief = 'First: Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-22_mixer-cold_2.md and continue.'
  await $.prompt.submit(delivered(brief))
  await $.prompt.submit(delivered(brief))
  const links = calls.filter(c => c.tool === 'mcp__hearthbot__reply')
  expect(links).toHaveLength(1)
  expect(String(links[0].text)).toMatch(/Continued from \[the old thread\]\(#cmsg_OLD9\)/)
  expect(entered).toHaveLength(2)
})

test('a 👍 reaction on the hold note starts the fresh thread', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  const pending = $.prompt.submit(system(reacted('👍')))
  await settle()
  const out = await pending
  expect(out.drop).toMatch(/Fresh thread requested/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(String(ask?.message)).toMatch(/His held message: is it done\?\n\nLinks:/)
})

test('a ⏩ reaction sends the held message on here', async ($, on) => {
  const { entered } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect((await $.prompt.submit(system(reacted('⏩')))).drop).toBeUndefined()
  expect(entered[0].context?.join('\n')).toMatch(/Matt said go ahead.*is it done\?/)
})

test('❌ drops the held message; ✋ keeps holding', async ($, on) => {
  const { entered, calls } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect((await $.prompt.submit(system(reacted('✋')))).drop).toMatch(/Still held/)
  expect((await $.prompt.submit(system(reacted('❌')))).drop).toMatch(/dropped/)
  expect(entered).toHaveLength(0)
  expect(calls.some(c => c.tool === 'mcp__claude-code-remote__send_message')).toBe(false)
})

test('editing the held message keeps it held with the new text', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect((await $.prompt.submit(system(edited('is it done yet?')))).drop).toMatch(/still held/)
  expect(entered).toHaveLength(0)
  await settle()
  const ask = calls.find(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(String(ask?.message)).toMatch(/His held message: is it done yet\?/)
})

test('a follow-up message while held goes to the fresh thread with the held one', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  const pending = $.prompt.submit(phone(wake('also check the logs', 'cmsg_M2')))
  await settle()
  const out = await pending
  expect(out.drop).toMatch(/Fresh thread requested/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(String(ask?.message)).toMatch(/is it done\?.*He added.*also check the logs/s)
})

test('other system turns still pass while a message is held', async ($, on) => {
  const { entered } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  expect((await $.prompt.submit(system(edited('unrelated', 'cmsg_OTHER')))).drop).toBeUndefined()
  expect((await $.prompt.submit(system(reacted('👍', '')))).drop).toBeUndefined()
  expect(entered).toHaveLength(2)
})

test('in a project thread, a message without the envelope is still held the thread way', async ($, on) => {
  const { entered, calls, settle } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('hi', 'cmsg_M0'))) // held; marks the session as a project thread
  await $.prompt.submit(phone(wake('here', 'cmsg_M1'))) // sends it on
  entered.length = 0
  calls.length = 0
  const out = await $.prompt.submit(phone('Matt · 9:32 PM\nthis is 100% not held'))
  expect(out.drop).toMatch(/Held \(project thread\)/)
  expect(calls.some(c => c.tool === 'mcp__hearthbot__reply')).toBe(true)
  // A second message is his answer, never a "send again" pass-through.
  const pending = $.prompt.submit(phone(wake('(don\'t stop it!)', 'cmsg_M2')))
  await settle()
  expect((await pending).drop).toMatch(/Fresh thread requested/)
  expect(entered).toHaveLength(0)
})

test('a cold project message goes through when the thread reply cannot be posted', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  const entered: string[] = []
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.submit', (_$, e) => { entered.push(e.text); return { text: e.text } })
  on('tool.call', () => { throw new Error('no such tool') })
  await $.session.measure(measure(300_000))
  await $.turn.complete(answered)
  await clock.advance(3 * 60 * MIN)
  expect((await $.prompt.submit(phone(wake('hi')))).drop).toBeUndefined()
  expect(entered).toHaveLength(1)
})

test('/haiku-handoff after a held message carries that message into the new thread', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  const runs: (readonly string[])[] = []
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.fill', () => ({ isFilled: true }))
  on('prompt.read', () => ({ value: { text: '/haiku-handoff', cursor: 14 } }))
  on('session.id', () => ({ value: 's1' }))
  on('command.run', () => ({ text: '' }))
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  on('process.run', (_$, e) => {
    runs.push(e.argv)
    const stdout = JSON.stringify({ path: '/h.md', prompt: 'Read /h.md and continue. Then: fix the bug' })
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false } }
  })
  await $.session.measure(measure(300_000))
  await $.turn.complete(answered)
  await clock.advance(2 * 60 * MIN)

  expect((await $.prompt.submit(phone('fix the bug'))).drop).toMatch(/goes with it/)
  const out = await $.command.run({ command: 'haiku-handoff', args: '', origin: { kind: 'bridge' } })
  const write = runs.find(a => a.includes('write'))
  expect(write?.slice(-2)).toEqual(['--then', 'fix the bug'])
  expect(JSON.stringify(out)).toMatch(/Then: fix the bug/)
})

test('a held message names attachments it could not save', async ($, on) => {
  const clock = mock.clock(on, { now: 1_000_000 })
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.fill', () => ({ isFilled: true }))
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  await $.session.measure(measure(300_000))
  await $.turn.complete(answered)
  await clock.advance(2 * 60 * MIN)

  const out = await $.prompt.submit({ ...phone('look at this'), attachments: [{ type: 'image', filename: 'shot.png' }] })
  expect(out.drop).toMatch(/1 attachment\(s\) can't be carried over/)
})

// A project-chat message, as the server hands it to a new thread: no <thread> element.
const chatWake = (body: string, id: string) =>
  '<wake reason="mention">\n  <project id="chan_1" type="project">\n' +
  `    <message trigger="true" from="human" id="${id}" mention="true">${body}</message>\n` +
  '  </project>\n</wake>'

const replied = (thread: string) => [{ type: 'text', text: JSON.stringify({ message_id: 'cmsg_R1', thread_id: thread }) }]

test("a project-chat message that isn't this thread's root never reaches the model", async ($, on) => {
  const entered: string[] = []
  on('prompt.submit', (_$, e) => { entered.push(e.text); return { text: e.text } })
  on('tool.call', () => ({ result: replied('cmsg_T1') }))
  await $.tool.call({ tool: 'mcp__hearthbot__reply', text: 'done' })

  const out = await $.prompt.submit(system(chatWake('make me a better bar', 'cmsg_OTHER')))
  expect(out.drop).toMatch(/Not this thread's message \(cmsg_OTHER\)/)
  expect(entered).toHaveLength(0)
})

test("the thread's own root and in-thread messages still go through", async ($, on) => {
  const entered: string[] = []
  on('prompt.submit', (_$, e) => { entered.push(e.text); return { text: e.text } })
  on('tool.call', () => ({ result: replied('cmsg_T1') }))
  await $.tool.call({ tool: 'mcp__hearthbot__reply', text: 'done' })

  expect((await $.prompt.submit(system(chatWake('fix it', 'cmsg_T1')))).drop).toBeUndefined()
  expect((await $.prompt.submit(system(wake('and this', 'cmsg_M9')))).drop).toBeUndefined()
  expect(entered).toHaveLength(2)
})

test('before the first reply the thread id is unknown, so nothing is dropped', async ($, on) => {
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  expect((await $.prompt.submit(system(chatWake('hi', 'cmsg_OTHER')))).drop).toBeUndefined()
})

// ── Smart queue ────────────────────────────────────────────────────────────────

const queueSetup = async ($: any, on: any, verdict = 'READY') => {
  const entered: string[] = []
  const calls: Record<string, unknown>[] = []
  const files: string[] = []
  const judged: string[] = []
  mock.clock(on, { now: 1_000_000 })
  on('session.id', () => ({ value: 's1' }))
  on('turn.start', (_$: unknown, e: any) => ({ turnId: e.turnId }))
  on('turn.complete', (_$: unknown, e: any) => ({ text: e.answer }))
  on('prompt.submit', (_$: unknown, e: any) => { entered.push(e.text); return { text: e.text } })
  on('tool.call', (_$: unknown, e: any) => { calls.push(e); return { result: '{"thread_id":"cmsg_T1"}' } })
  on('model.complete', (_$: unknown, e: any) => { judged.push(String(e.prompt)); return { value: { isAnswered: true, text: verdict, usage: { inputTokens: 1, outputTokens: 1 } } } })
  on('process.run', (_$: unknown, e: any) => { if (e.init?.stdin) files.push(e.init.stdin); return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false } } })
  const settle = async () => { for (let i = 0; i < 50; i++) await new Promise(r => setTimeout(r, 0)) }
  const turn = async (reply: string) => {
    await $.turn.start({ turnId: 't', prompt: '' } as any)
    await $.tool.call({ tool: 'mcp__hearthbot__reply', text: reply })
    await $.turn.complete(answered)
    await settle()
  }
  return { entered, calls, files, judged, settle, turn }
}

test('/q while the agent works waits for the turn to end, then goes out', async ($, on) => {
  const { entered, calls, turn, settle } = await queueSetup($, on)
  await $.turn.start({ turnId: 't0', prompt: '' } as any)
  const out = await $.prompt.submit(phone(wake('/q also fix the README', 'cmsg_Q1')))
  expect(out.drop).toMatch(/Queued/)
  expect(entered).toHaveLength(0)
  expect(calls.some(c => c.tool === 'mcp__hearthbot__react' && c.emoji === '⏳' && c.message_id === 'cmsg_Q1')).toBe(true)
  await $.tool.call({ tool: 'mcp__hearthbot__reply', text: 'Done: the build is green.' })
  await $.turn.complete(answered)
  await settle()
  expect(entered).toHaveLength(1)
  expect(entered[0]).toMatch(/\[thread-queue\].*also fix the README/s)
  expect(calls.some(c => c.tool === 'mcp__hearthbot__react' && c.emoji === '📨')).toBe(true)
  void turn
})

test('a reply that asks Matt something keeps the queue until he answers', async ($, on) => {
  const { entered, files, turn } = await queueSetup($, on, 'WAIT')
  await turn('Should I use the blue one or the green one?')
  await $.prompt.submit(phone(wake('/q then update the docs', 'cmsg_Q1')))
  await new Promise(r => setTimeout(r, 0))
  for (let i = 0; i < 50; i++) await new Promise(r => setTimeout(r, 0))
  expect(entered).toHaveLength(0)
  expect(files.at(-1)).toMatch(/"waiting":"the last reply asks you something"/)
  // ⏩ on his queued message sends it anyway.
  const r = '<wake reason="reactions" current-time="t">\n  <project id="chan_1" type="project">\n    <thread ts="cmsg_T1"></thread>\n  </project>\n' +
    '  <reactions channel="chan_1" thread_ts="cmsg_T1">\n    <reaction emoji="⏩" count="1" message_ts="cmsg_Q1" message_from="Matt" reactors="user_M"></reaction>\n  </reactions>\n</wake>'
  expect((await $.prompt.submit(system(r))).drop).toBeUndefined()
  for (let i = 0; i < 50; i++) await new Promise(r => setTimeout(r, 0))
  expect(entered).toHaveLength(1)
  expect(entered[0]).toMatch(/then update the docs/)
})

test('/q while idle after a plain report sends straight away', async ($, on) => {
  const { entered, turn, settle } = await queueSetup($, on, 'READY')
  await turn('Pushed the fix.')
  await $.prompt.submit(phone(wake('/q now do the tests', 'cmsg_Q1')))
  await settle()
  expect(entered).toEqual([expect.stringMatching(/now do the tests/)])
})

test("the coordinator's thread-queue note is queued without waking the model", async ($, on) => {
  const { entered } = await queueSetup($, on)
  await $.turn.start({ turnId: 't0', prompt: '' } as any)
  const out = await $.prompt.submit(delivered('thread-queue add: rename the HUD'))
  expect(out.drop).toMatch(/coordinator note/)
  expect(entered).toHaveLength(0)
})

test('/q drop clears it; a stopped turn never releases the queue', async ($, on) => {
  const { entered, settle } = await queueSetup($, on)
  await $.turn.start({ turnId: 't0', prompt: '' } as any)
  await $.prompt.submit(phone(wake('/q one', 'cmsg_Q1')))
  await $.turn.complete({ ...answered, reason: 'aborted', isAborted: true })
  await settle()
  expect(entered).toHaveLength(0)
  expect((await $.prompt.submit(phone(wake('/q drop', 'cmsg_Q2')))).drop).toMatch(/dropped/)
  await $.turn.start({ turnId: 't1', prompt: '' } as any)
  await $.turn.complete(answered)
  await settle()
  expect(entered).toHaveLength(0)
})

test('keyword fallback spots a question or a 👍 offer', async () => {
  const m = { asksMatt, queueCommand }
  expect(m.asksMatt('Done.\n\nWhich colour do you want?')).toBe(true)
  expect(m.asksMatt('Reply 👍 to ship it.')).toBe(true)
  expect(m.asksMatt('**Shipped.** Tested.\n\nDetails: [x](y#z?)')).toBe(false)
  expect(m.queueCommand('/q fix it')).toEqual({ kind: 'add', text: 'fix it' })
  expect(m.queueCommand('/quick note')).toBeUndefined()
})

test('a cold thread under the hold size just resumes; idle compaction waits for size, idle time and a warm cache', async () => {
  const k = KNOB_DEFAULTS
  const hour = 60 * 60_000
  const c = { lastAt: 0, ttlMs: hour, tokens: 220_000 }
  expect(compactDue(c, 50 * 60_000, k, -1)).toBe(true)
  expect(compactDue(c, 40 * 60_000, k, -1)).toBe(false) // not idle long enough
  expect(compactDue({ ...c, tokens: 150_000 }, 50 * 60_000, k, -1)).toBe(false) // too small
  expect(compactDue(c, 61 * 60_000, k, -1)).toBe(false) // cache already expired
  expect(compactDue(c, 50 * 60_000, k, 0)).toBe(false) // already compacted since the last turn
})
