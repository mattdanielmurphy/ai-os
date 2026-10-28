import { expect, test } from 'claude-code/testing'

const BAND = {
  component: 'AbovePrompt',
  props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 80, scroll: { offset: 0, bodyRows: 10 }, view: {} },
} as const

test('band shows a toggle that flips the session setting', async ($, on) => {
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  const ui = await $.ui.mount({ plugin: 'read-aloud', surface: 'desktop', ...BAND })
  expect(await ui.find({ key: 'toggle' })).toBeDefined()
  await ui.press({ key: 'toggle' })
  await new Promise(r => setTimeout(r, 10))
  expect(await ui.find({ key: 'toggle' })).toBeDefined()
  await ui.unmount()
})

test('a stopped turn reads nothing', async ($, on) => {
  const ran: string[] = []
  on('process.run', (_$, e) => { ran.push(e.argv.join(' ')); return { value: { exitCode: 0, stdout: '', stderr: '' } } as never })
  on('command.run', () => ({ text: '' }) as never)
  on('turn.complete', (_$, e) => ({ text: e.answer }) as never)
  await $.command.run({ name: 'read-aloud' } as never)
  ran.length = 0
  await $.turn.complete({ answer: 'old reply', reason: 'aborted', durationMs: 1 } as never)
  expect(ran.some(c => c.includes('replyDone'))).toBe(false)
  await $.turn.complete({ answer: 'new reply', reason: 'answer', durationMs: 1 } as never)
  expect(ran.some(c => c.includes('replyDone'))).toBe(true)
})

test('band has a Dictate after toggle', async ($, on) => {
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'on', stderr: '' } }) as never)
  on('ui.render', ($$, e) => { const { Box } = $$.ui.resolve(e); return <Box /> })
  const ui = await $.ui.mount({ plugin: 'read-aloud', surface: 'desktop', ...BAND })
  const b = await ui.find({ key: 'dictate' })
  expect(b).toBeDefined()
  await ui.press({ key: 'dictate' })
  await ui.unmount()
})
