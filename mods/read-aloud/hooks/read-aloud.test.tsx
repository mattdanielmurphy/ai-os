import { expect, test } from 'claude-code/testing'

import { speakable } from './register'

test('drops code, links, paths and the Actions/Details lines', async () => {
  const out = speakable(
    '**Read-aloud is live.** See [the file](http://do.test/open/x) at /Users/matt/projects/ai-os/x.md.\n\n```bash\nrm -rf\n```\n\n- run `say hi`\n\n**Actions:** Ship → Yes\n\nDetails: [d](x#y)',
  )
  expect(out).toBe('Read-aloud is live. See the file at \nrun')
})

test('long replies are cut on a word', async () => {
  expect(speakable('word '.repeat(100), 22)).toBe('word word word word. The rest is on screen.')
})
