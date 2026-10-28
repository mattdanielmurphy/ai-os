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
