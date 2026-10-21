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
    expect(await ui.find({ key: 'haiku' })).toBeDefined()
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
    expect(await ui.find({ key: 'haiku' })).toBeDefined()
    await ui.unmount()
  }

  await clock.advance(3 * 60 * MIN)
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Cache/ }))?.text).toMatch(/expired 2h ago.*80k tokens/)
    expect(await ui.find({ type: 'Text', text: /Haiku reads the saved file/ })).toBeDefined()
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
  expect(held.drop).toMatch(/expired 1h ago.*180k tokens.*\/haiku-handoff/)
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
  on('process.run', () => {
    const stdout = JSON.stringify({ path: '/h.md', prompt: 'Read /h.md and continue. Then: is it done?' })
    return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false } }
  })
  await $.session.measure(measure(180_000))
  await $.turn.complete(answered)
  await clock.advance(3 * 60 * MIN)
  return { clock, entered, calls }
}

test('a cold project message is held and Matt is asked in the thread; "here" sends it on', async ($, on) => {
  const { entered, calls } = await projectSetup($, on)
  const out = await $.prompt.submit(phone(wake('is it done?')))
  expect(out.drop).toMatch(/Held \(project thread\)/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__hearthbot__reply')
  expect(String(ask?.text)).toMatch(/Held, nothing sent yet.*expired 2h ago.*~180k tokens/s)

  expect((await $.prompt.submit(phone(wake('here', 'cmsg_M2')))).drop).toBeUndefined()
  expect(entered).toHaveLength(1)
  expect(entered[0].context?.join('\n')).toMatch(/Matt said go ahead.*is it done\?/)
})

test('any other reply (the default) asks the coordinator for a new thread from the Haiku handoff', async ($, on) => {
  const { entered, calls } = await projectSetup($, on)
  await $.prompt.submit(phone(wake('is it done?')))
  const out = await $.prompt.submit(phone(wake('sounds good', 'cmsg_M2')))
  expect(out.drop).toMatch(/Fresh thread requested/)
  expect(entered).toHaveLength(0)
  const ask = calls.find(c => c.tool === 'mcp__claude-code-remote__send_message')
  expect(ask?.session_id).toBe('@parent')
  expect(String(ask?.message)).toMatch(/message cmsg_M1.*Read \/h\.md and continue.*His held message: is it done\?/s)
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
