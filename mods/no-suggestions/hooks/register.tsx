import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

const isOn = atom({ plugin: 'no-suggestions', key: 'isOn' } as const, false)

// One empty file per thread, so an agent or script can switch a thread on from outside:
// touch ~/.claude/no-suggestions/<session id>
const flag = 'dir="$HOME/.claude/no-suggestions"; f="$dir/$1";'

const isFlagged = async ($: EngineInterface): Promise<boolean> => {
  const id = await $.session.id()
  const out = await $.process.run(['sh', '-c', `${flag} [ -f "$f" ] && echo on`, 'sh', id])
  return out.stdout.trim() === 'on'
}

const setFlag = async ($: EngineInterface, on: boolean) => {
  const id = await $.session.id()
  const script = on ? `${flag} mkdir -p "$dir" && : > "$f"` : `${flag} rm -f "$f"`
  await $.process.run(['sh', '-c', script, 'sh', id])
  await update($, isOn, () => on)
}

/** A prompt that starts logic practice switches the thread on by itself. */
export const startsPractice = (text: string) =>
  /\b(logic|deduction|proofs?)\b.{0,30}\b(practice|quiz|drill)|\b(practice|quiz|drill)\b.{0,30}\b(logic|deduction|proofs?)\b/i.test(text)

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await $.command.register({ name: 'no-suggestions', description: 'Hide or show the grey suggestions in this thread only' })
    await update($, isOn, () => false)
    if (await isFlagged($)) await update($, isOn, () => true)
    return result
  })

  // Read the file every time, so a switch from outside works without a restart.
  on('prompt.suggest', async ($, e, next) => {
    if (e.origin.kind !== 'suggestion') return next(e)
    const hidden = await isFlagged($).catch(() => false)
    if (hidden !== (await read($, isOn))) await update($, isOn, () => hidden)
    return hidden ? { isShown: false } : next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    if (startsPractice(e.text)) await setFlag($, true)
    return next(e)
  })

  on('command.run', { command: 'no-suggestions' }, async $ => {
    const next = !(await isFlagged($))
    await setFlag($, next)
    return { text: next ? 'Grey suggestions are hidden in this thread.' : 'Grey suggestions are back in this thread.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await read($, isOn))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    const above = await next(e)
    return (
      <Box flexWrap="wrap" rowGap="xs" alignItems="center">
        {above}
        <Text dimColor>Suggestions hidden in this thread </Text>
        <Button key="show" label="Show" plain dimColor onPress={() => setFlag($, false)} />
      </Box>
    )
  })
}
