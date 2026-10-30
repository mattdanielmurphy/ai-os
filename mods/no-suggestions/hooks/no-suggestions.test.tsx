import { expect, test } from 'claude-code/testing'

import { startsPractice } from './register'

test('practice prompts match, ordinary ones do not', async () => {
  expect(startsPractice("let's do logic practice")).toBe(true)
  expect(startsPractice('quiz me on natural deduction')).toBe(true)
  expect(startsPractice('fix the logic in this function')).toBe(false)
})
