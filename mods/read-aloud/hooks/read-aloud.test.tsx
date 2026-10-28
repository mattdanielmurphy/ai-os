import { expect, test } from 'claude-code/testing'
import { queueItems, turnTexts } from './register'

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
  on('session.id', () => ({ value: 'abcdef1234' }) as never)
  on('session.messages', () => ({ value: [] }) as never)
  const wrote: string[] = []
  on('fs.write', (_$, e) => { wrote.push((e as { path: string }).path); return { value: undefined } as never })
  await $.command.run({ name: 'read-aloud' } as never)
  ran.length = 0
  await $.turn.complete({ answer: 'old reply', reason: 'aborted', durationMs: 1 } as never)
  expect(ran.some(c => c.includes('replyDone'))).toBe(false)
  await $.turn.complete({ answer: 'new reply', reason: 'answer', durationMs: 1 } as never)
  expect(ran.some(c => c.includes('replyDone'))).toBe(true)
  expect(wrote.length).toBe(1)
  expect(wrote[0].includes('read_aloud_queue/') && wrote[0].endsWith('-abcdef12.json')).toBe(true)
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

test('queue keeps every real reply in order, skips short notes, and cuts before Actions', async () => {
  const long = 'Yes, there is a way around it. ' + 'x'.repeat(200)
  const texts = turnTexts([
    { role: 'user', text: 'hi' },
    { role: 'assistant', text: 'Checking.' },
    { role: 'user', text: '', toolResults: [{}] },
    { role: 'assistant', text: long },
    { role: 'assistant', text: 'Done.\n\n**Actions:** Go → Yes, go' },
  ])
  expect(texts.length).toBe(3)
  const items = queueItems(texts)
  expect(items.length).toBe(2)
  expect(items[0].key.startsWith('yesthereisawayaroundit')).toBe(true)
  expect(items[0].cut).toBe(null)
  expect(items[1].cut).toBe('Done.'.length)
})
