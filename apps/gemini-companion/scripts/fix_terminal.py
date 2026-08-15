import re

with open('src/main.ts', 'r') as f:
    content = f.read()

# 1. Fix handleLink to check e.metaKey
content = content.replace(
    'const handleLink = (_e: MouseEvent, uri: string) => {\n    if (true) {',
    'const handleLink = (e: MouseEvent, uri: string) => {\n    if (e.metaKey) {'
)

# 2. Fix pasting in custom key handler
custom_key_handler_search = """term.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {"""
custom_key_handler_replace = """term.attachCustomKeyEventHandler((e) => {
    if (e.key === 'v' && e.metaKey && e.type === 'keydown') {
        navigator.clipboard.readText().then((text) => {
            invoke('write_to_pty', {
                data: text,
                projectPath: activeProject,
                terminalType: currentEngine,
            }).catch(console.error)
        })
        return false
    }
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {"""
content = content.replace(custom_key_handler_search, custom_key_handler_replace)

mini_key_handler_search = """miniTerm.attachCustomKeyEventHandler((e) => {
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {"""
mini_key_handler_replace = """miniTerm.attachCustomKeyEventHandler((e) => {
    if (e.key === 'v' && e.metaKey && e.type === 'keydown') {
        navigator.clipboard.readText().then((text) => {
            invoke('write_to_pty', {
                data: text,
                projectPath: activeProject,
                terminalType: 'mini',
            }).catch(console.error)
        })
        return false
    }
    if (e.key === 'Enter' && e.shiftKey && e.type === 'keydown') {"""
content = content.replace(mini_key_handler_search, mini_key_handler_replace)

# 3. Fix resizePty to force a refresh of the WebGL/DOM renderer
resize_pty_search = """const resizePty = () => {
    fitAddon.fit()
    miniFitAddon.fit()"""
resize_pty_replace = """const resizePty = () => {
    try {
        fitAddon.fit()
        if (term.element && term.element.clientHeight > 0) {
            // Force redraw to fix disappearing terminal issue
            const r = term.rows;
            term.resize(term.cols, r);
        }
    } catch(e) {}
    try {
        miniFitAddon.fit()
    } catch(e) {}"""
content = content.replace(resize_pty_search, resize_pty_replace)

with open('src/main.ts', 'w') as f:
    f.write(content)
print("Done")
