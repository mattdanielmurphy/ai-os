import { expect, test } from 'claude-code/testing'

const BAND = {
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80 },
} as const

const measure = (tokens: number) => ({
  context: { tokens, window: 1_000_000, percent: Math.round(tokens / 10_000) },
  rateLimits: [],
  changed: ['context' as const],
})

test('band stays hidden under 150k and appears above it', async ($, on) => {
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
