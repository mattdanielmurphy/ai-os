import re

with open('src/main.ts', 'r') as f:
    content = f.read()

# Fix buildTimelineHtml
# Replace user_input rendering
old_user_render = """        if (block.type === 'user_input' && block.content) {
            if (block.historicalContext) {
                const escapedThreadId = block.threadId || ''
                html += `
                <div class="ts-html-element-7">
                    <div class="ts-html-element-8">
                        <details class="group">
                            <summary class="ts-html-element-9">
                                <span class="ts-html-element-10">
                                    <span class="">📜</span>
                                    <span>Historical Context of active thread ${escapedThreadId ? `(${escapedThreadId.substring(0, 8)}...)` : ''}</span>
                                </span>
                                <span class="ts-html-element-11">▶</span>
                            </summary>
                            <div class="ts-html-element-12">
${block.historicalContext}
                            </div>
                        </details>
                    </div>
                </div>
                `
            }
            html += `
            <div class="ts-html-element-13">
                <div class="ts-html-element-14 group">
                    <button class="ts-html-element-15" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    ${block.content}
                </div>
            </div>
            `
        } else if (block.type === 'planner_response' && block.content) {
            html += `
            <div class="ts-html-element-16">
                <div class="ts-html-element-17 group prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border">
                    <button class="ts-html-element-18" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    ${marked.parse(block.content)}
                </div>
            </div>
            `
        }"""

new_user_render = """        if (block.type === 'user_input' && block.content) {
            if (block.historicalContext) {
                const escapedThreadId = block.threadId || ''
                html += `
                <div class="chat-message agent historical">
                    <div class="message-content">
                        <details class="group">
                            <summary class="historical-summary">
                                <span>📜 Historical Context of active thread ${escapedThreadId ? `(${escapedThreadId.substring(0, 8)}...)` : ''}</span>
                                <span class="toggle-icon">▶</span>
                            </summary>
                            <div class="historical-details">
${block.historicalContext}
                            </div>
                        </details>
                    </div>
                </div>
                `
            }
            html += `
            <div class="chat-message user">
                <div class="message-content group">
                    <button class="copy-btn" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    <div class="text-content">${block.content}</div>
                </div>
            </div>
            `
        } else if (block.type === 'planner_response' && block.content) {
            html += `
            <div class="chat-message agent">
                <div class="message-content group prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border">
                    <button class="copy-btn" data-content="${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    <div class="text-content">${marked.parse(block.content)}</div>
                </div>
            </div>
            `
        }"""

if old_user_render in content:
    content = content.replace(old_user_render, new_user_render)
else:
    print("Failed to find old user render block")


# Replace project threads rendering
old_thread_render = """            el.className = isActive
                ? 'group p-1.5 rounded border border-blue-500/30 dark:border-blue-500/40 bg-blue-50/50 dark:bg-blue-500/10 hover:bg-blue-100/50 dark:hover:bg-blue-500/20 cursor-pointer transition-all space-y-0.5'
                : 'group p-1.5 rounded border border-gray-200 dark:border-gray-855 bg-white dark:bg-gray-900/40 hover:bg-gray-100 dark:hover:bg-gray-850 cursor-pointer transition-all space-y-0.5'

            const dateStr =
                thread.mtime > 0
                    ? new Date(thread.mtime * 1000).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                      })
                    : 'Unknown Date'

            el.innerHTML = `
                <div class="ts-html-element-53">
                    <div class="ts-html-element-54">
                        <div class="ts-html-element-55">
                            <span class="ts-html-element-56">#${thread.id.substring(0, 8)}</span>
                            <span class="ts-html-element-57">${dateStr}</span>
                        </div>
                        <div class="ts-html-element-58" title="${thread.title}">${thread.title}</div>
                        <div class="ts-html-element-59" title="${thread.snippet}">${thread.snippet}</div>
                    </div>
                    <button class="ts-html-element-60 delete-thread-btn" title="Delete Thread">✕</button>
                </div>
            `"""

new_thread_render = """            el.className = isActive ? 'thread-history-item active group' : 'thread-history-item group'

            const dateStr =
                thread.mtime > 0
                    ? new Date(thread.mtime * 1000).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                      })
                    : 'Unknown Date'

            el.innerHTML = `
                <div class="thread-info">
                    <div class="thread-header">
                        <span class="thread-id">#${thread.id.substring(0, 8)}</span>
                        <span class="thread-date">${dateStr}</span>
                    </div>
                    <div class="thread-title" title="${thread.title}">${thread.title}</div>
                    <div class="thread-snippet" title="${thread.snippet}">${thread.snippet}</div>
                </div>
                <button class="delete-thread-btn" title="Delete Thread">✕</button>
            `"""

if old_thread_render in content:
    content = content.replace(old_thread_render, new_thread_render)
else:
    print("Failed to find old thread render block")


# Replace older steps collapse section
old_tool_render = """                html += `
                <details class="ts-html-element-19 group">
                    <summary class="ts-html-element-20">
                        <span class="ts-html-element-21">Show older steps (${collapsedCalls.length})</span>
                        <span class="ts-html-element-22">▶</span>
                    </summary>
                    <div class="">
                        ${collapsedCalls.map(renderToolCallHtml).join('')}
                    </div>
                </details>
                `"""

new_tool_render = """                html += `
                <div class="chat-message agent tool-call-group">
                    <div class="message-content">
                        <details class="group">
                            <summary class="historical-summary">
                                <span>Show older steps (${collapsedCalls.length})</span>
                                <span class="toggle-icon">▶</span>
                            </summary>
                            <div class="historical-details">
                                ${collapsedCalls.map(renderToolCallHtml).join('')}
                            </div>
                        </details>
                    </div>
                </div>
                `"""

if old_tool_render in content:
    content = content.replace(old_tool_render, new_tool_render)
else:
    print("Failed to find old tool render block")


# Replace single tool call render
old_single_tool_render = """        return `
            <div class="ts-html-element-4">
                <div class="ts-html-element-5">
                    <span>${call.icon}</span>
                    <span class="ts-html-element-6">${call.actionSummary}</span>${pathHtml}
                </div>
            </div>
        `"""

new_single_tool_render = """        return `
            <div class="chat-message agent tool-call">
                <div class="message-content">
                    <div class="tool-call-info">
                        <span>${call.icon}</span>
                        <span class="tool-summary">${call.actionSummary}</span>${pathHtml}
                    </div>
                </div>
            </div>
        `"""

if old_single_tool_render in content:
    content = content.replace(old_single_tool_render, new_single_tool_render)
else:
    print("Failed to find single tool render block")

with open('src/main.ts', 'w') as f:
    f.write(content)
print("Updated src/main.ts")
