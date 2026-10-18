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

test('band stays hidden under 150k and appears above it', async ($, on) => {
  mock.clock(on)
  on('session.measure', (_$, e) => ({ changed: e.changed }))
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  for (const surface of ['terminal', 'desktop'] as const) {
    await $.session.measure(measure(90_000))
    let ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect(await ui.find({ type: 'Text', text: /Current context size/ })).toBeUndefined()
    await ui.unmount()

    await $.session.measure(measure(212_000))
    ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Current context size/ }))?.text).toMatch(/212k \/ 1000k/)
    expect(await ui.find({ key: 'handoff' })).toBeDefined()
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
    expect(await ui.find({ key: 'fresh' })).toBeDefined()
    await ui.unmount()
  }

  await clock.advance(3 * 60 * MIN)
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'context-alert', surface, ...BAND })
    expect((await ui.find({ type: 'Text', text: /Cache/ }))?.text).toMatch(/expired 2h ago.*80k tokens/)
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
  expect(held.drop).toMatch(/expired 1h ago.*180k tokens.*\/fresh/)
  expect((await $.prompt.submit(phone('cold'))).drop).toBeUndefined()
  expect(entered).toEqual(['warm', 'cold'])
})
