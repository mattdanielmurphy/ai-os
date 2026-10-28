import { expect, test } from 'claude-code/testing'

import { hideActions, parseActions } from './register'

const BAND = {
  component: 'AbovePrompt',
  props: {
    hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 }, view: {},
  },
} as const

test('parses the Actions line, ignores ordinary lists', async () => {
  expect(parseActions('Done.\n\n1. one\n2. two')).toEqual([])
  expect(parseActions('Done.\n\n**Actions:** Test Glass TV fix → Yes, run the Glass TV test · Trim tools\n\nDetails: x')).toEqual([
    { label: 'Test Glass TV fix', text: 'Yes, run the Glass TV test' },
    { label: 'Trim tools', text: 'Yes, trim tools' },
  ])
})

test('bar shows buttons, a click sends the number, sending clears it', async ($, on) => {
  const sent: string[] = []
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('prompt.submit', (_$, e) => { sent.push(e.text); return { text: e.text } })
  await $.turn.complete({ answer: 'ok\nActions: Ship it → Yes, ship it · Test more → Yes, test it more first · Docs → Yes, write docs', reason: 'answer', durationMs: 1 } as never)
  const ui = await $.ui.mount({ plugin: 'action-bar', surface: 'desktop', ...BAND })
  expect(await ui.find({ key: 'a2' })).toBeDefined()
  expect(await ui.find({ key: 'all' })).toBeDefined()
  await ui.press({ key: 'a2' })
  await new Promise(r => setTimeout(r, 10))
  expect(sent).toContain('Yes, test it more first')
  expect(await ui.find({ key: 'a1' })).toBeUndefined()
  await ui.unmount()
})

test('either/or items are marked, so no All button', async () => {
  const list = parseActions('Actions: Build it → Yes, build it | Skip it → No, skip it')
  expect(list.every(a => a.either)).toBe(true)
  expect(parseActions('Actions: A · B · C').some(a => a.either)).toBe(false)
})

test('the Actions line is hidden from the drawn reply', async () => {
  expect(hideActions('Done.\n\n**Actions:** Ship it → Yes, ship it\n\nDetails: x')).toBe('Done.\n\nDetails: x')
  expect(hideActions('No actions here.')).toBe('No actions here.')
})
