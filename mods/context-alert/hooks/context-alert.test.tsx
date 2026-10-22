import { expect, mock, test } from 'claude-code/testing'

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
  await $.session.measure(measure(180_000))
  await $.turn.complete(answered)

  await clock.advance(30 * MIN)
  expect((await $.prompt.submit(phone('warm'))).drop).toBeUndefined()

  await clock.advance(2 * 60 * MIN)
  const held = await $.prompt.submit(phone('cold'))
  expect(held.drop).toMatch(/expired 1h ago.*180k tokens.*\/cold-handoff/)
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
  await $.session.measure(measure(180_000))
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
  expect(String(ask?.text)).toMatch(/expired 2h ago, so this moves to a fresh thread.*~180k tokens/s)

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
  expect(String(asks[0].message)).toMatch(/His held message: is it done\?.*#cmsg_T1.*context-alert handed-off:/s)
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
  await $.session.measure(measure(180_000))
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
  await $.session.measure(measure(180_000))
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
  await $.session.measure(measure(180_000))
  await $.turn.complete(answered)
  await clock.advance(2 * 60 * MIN)

  const out = await $.prompt.submit({ ...phone('look at this'), attachments: [{ type: 'image', filename: 'shot.png' }] })
  expect(out.drop).toMatch(/1 attachment\(s\) can't be carried over/)
})
