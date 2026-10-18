import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Fill } from '../types'

// Band shows from WARN; turns red from ALERT. Toasts once per threshold crossed.
const WARN = 150_000
const ALERT = 200_000
const TOAST_AT = [150_000, 200_000, 250_000, 300_000]

const fill = atom({ plugin: 'context-alert', key: 'fill' } as const, null)
const lastToast = atom({ plugin: 'context-alert', key: 'lastToast' } as const, 0)

export const k = (n: number) => `${Math.round(n / 1000)}k`

export const register: Register = on => {
  on('session.measure', async ($, e, next) => {
    const { tokens, window } = e.context
    if (e.changed.includes('context') && tokens !== undefined) {
      const current: Fill = { tokens, window }
      await update($, fill, () => current)

      const crossed = TOAST_AT.filter(t => tokens >= t).pop() ?? 0
      const shown = await read($, lastToast)
      if (crossed > shown) {
        $.ui.toast(`Context is ${k(tokens)} tokens. Time for /_handoff?`)
      }
      if (crossed !== shown) await update($, lastToast, () => crossed)
    }
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, fill)
    if (e.props.hasSurvey || current === null || current.tokens < WARN) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const isAlert = current.tokens >= ALERT

    return (
      <Box>
        <Text bold color={isAlert ? 'error' : 'warning'}>
          ⚠ Current context size: {k(current.tokens)} / {k(current.window)} (
          {isAlert ? 'hand off now' : 'getting long'}){' '}
        </Text>
        <Button
          key="handoff"
          label="Write handoff"
          onPress={() => $.prompt.fill({ text: '/_handoff', mode: 'replace' })}
        />
      </Box>
    )
  })
}
