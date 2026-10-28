import { expect, test } from 'claude-code/testing'

import { parseActions } from './register'

const BAND = {
  component: 'AbovePrompt',
  props: {
    hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 }, view: {},
  },
} as const

test('parses the Actions line, ignores ordinary lists', async () => {
  expect(parseActions('Done.\n\n1. one\n2. two')).toEqual([])
  expect(parseActions('Done.\n\n**Actions:** 1. Glass TV test · 2. Trim tools\n\nDetails: x')).toEqual([
    { n: '1', label: 'Glass TV test' },
    { n: '2', label: 'Trim tools' },
  ])
})

test('bar shows buttons, a click sends the number, sending clears it', async ($, on) => {
  const sent: string[] = []
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.submit', (_$, e) => { sent.push(e.text); return { text: e.text } })
  await $.turn.complete({ answer: 'ok\nActions: 1. Ship it · 2. Test more', reason: 'answer', durationMs: 1 } as never)
  const ui = await $.ui.mount({ plugin: 'action-bar', surface: 'desktop', ...BAND })
  expect(await ui.find({ key: 'a2' })).toBeDefined()
  expect(await ui.find({ key: 'all' })).toBeDefined()
  await ui.press({ key: 'a2' })
  await new Promise(r => setTimeout(r, 10))
  expect(sent).toContain('2')
  expect(await ui.find({ key: 'a1' })).toBeUndefined()
  await ui.unmount()
})
