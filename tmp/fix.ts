import { readFileSync, writeFileSync } from 'fs';

const path = 'src/main.ts';
let content = readFileSync(path, 'utf8');

const targetStr = `
    let lastToolCallsBlock = null;
    for (let i = blocks.length - 1; i >= 0; i--) {
        if (blocks[i].type === 'tool_calls') {
            lastToolCallsBlock = blocks[i];
            break;
        }
    }

    blocks.forEach((block) => {
        if (block.type === 'user_input' && block.content) {
            if (block.historicalContext) {
                const escapedThreadId = block.threadId || ''
                html += \`
                <div class="chat-message agent historical">
                    <div class="message-content">
                        <details class="group">
                            <summary class="historical-summary">
                                <span>📜 Historical Context of active thread \${escapedThreadId ? \`(\${escapedThreadId.substring(0, 8)}...)\` : ''}</span>
                                <span class="toggle-icon">▶</span>
                            </summary>
                            <div class="historical-details">
\${block.historicalContext}
                            </div>
                        </details>
                    </div>
                </div>
                \`
            }
            html += \`
            <div class="chat-message user">
                <div class="message-content group">
                    <button class="copy-btn" data-content="\${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    <div class="text-content">\${block.content}</div>
                </div>
            </div>
            \`
        } else if (block.type === 'planner_response' && block.content) {
            const cleanedContent = block.content.replace(/<THREAD_NAME>[\\s\\S]*?<\\/THREAD_NAME>/g, '').trim()
            html += \`
            <div class="chat-message agent">
                <div class="message-content group prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border">
                    <button class="copy-btn" data-content="\${encodeURIComponent(cleanedContent)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    <div class="text-content">\${marked.parse(cleanedContent)}</div>
                </div>
            </div>
            \`
        } else if (block.type === 'tool_calls' && (block.calls?.length || block.thought)) {
            const isLast = block === lastToolCallsBlock;
            const shouldOpen = isLast && isThinking;
            const boxId = isLast ? 'unified-tool-calls-box' : \`tool-calls-box-\${Math.random().toString(36).substr(2, 9)}\`;
            const listId = isLast ? 'unified-tool-calls-list' : \`tool-calls-list-\${Math.random().toString(36).substr(2, 9)}\`;
            
            let callsHtml = '';
            if (block.calls && block.calls.length > 0) {
                callsHtml = block.calls.map(renderToolCallHtml).join('');
            }
            
            let thoughtHtml = '';
            if (block.thought) {
                const escapedThought = block.thought.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                thoughtHtml = \`<div class="agent-thought" style="padding: 8px; font-size: 0.8rem; color: var(--text-muted); background: rgba(0,0,0,0.05); border-left: 2px solid var(--primary, #5645c5); margin-bottom: 8px; white-space: pre-wrap;">\${escapedThought}</div>\`;
            }

            const headerText = (block.calls && block.calls.length > 0) ? \`Tool Calls (\${block.calls.length})\` : \`Agent Thinking...\`;

            html += \`
            <div class="chat-message agent tool-call-group" style="margin-top: 16px;">
                <div class="message-content" style="width: 100%;">
                    <details class="group tool-calls-box" id="\${boxId}" \${shouldOpen ? 'open' : ''}>
                        <summary class="historical-summary">
                            <span>\${headerText}</span>
                            <span class="toggle-icon">▶</span>
                        </summary>
                        <div class="historical-details unified-tool-calls-list" id="\${listId}" style="max-height: 50vh; overflow-y: auto;">
                            \${thoughtHtml}
                            \${callsHtml}
                        </div>
                    </details>
                </div>
            </div>
            \`
        }
    })
`;

const replaceStr = `
    interface Turn {
        userInput: RenderBlock | null;
        agentBlocks: RenderBlock[];
    }
    const turns: Turn[] = [];
    let currentTurn: Turn = { userInput: null, agentBlocks: [] };
    
    blocks.forEach((block) => {
        if (block.type === 'user_input') {
            if (currentTurn.userInput || currentTurn.agentBlocks.length > 0) {
                turns.push(currentTurn);
            }
            currentTurn = { userInput: block, agentBlocks: [] };
        } else {
            currentTurn.agentBlocks.push(block);
        }
    });
    if (currentTurn.userInput || currentTurn.agentBlocks.length > 0) {
        turns.push(currentTurn);
    }

    turns.forEach((turn, index) => {
        const isLastTurn = index === turns.length - 1;

        if (turn.userInput && turn.userInput.content) {
            const block = turn.userInput;
            if (block.historicalContext) {
                const escapedThreadId = block.threadId || ''
                html += \`
                <div class="chat-message agent historical">
                    <div class="message-content">
                        <details class="group">
                            <summary class="historical-summary">
                                <span>📜 Historical Context of active thread \${escapedThreadId ? \`(\${escapedThreadId.substring(0, 8)}...)\` : ''}</span>
                                <span class="toggle-icon">▶</span>
                            </summary>
                            <div class="historical-details">
\${block.historicalContext}
                            </div>
                        </details>
                    </div>
                </div>
                \`
            }
            html += \`
            <div class="chat-message user">
                <div class="message-content group">
                    <button class="copy-btn" data-content="\${encodeURIComponent(block.content)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                    <div class="text-content">\${block.content}</div>
                </div>
            </div>
            \`
        }

        const allCalls: ToolCallItem[] = [];
        const allThoughts: string[] = [];
        const textResponses: string[] = [];

        turn.agentBlocks.forEach(b => {
            if (b.type === 'tool_calls') {
                if (b.calls) allCalls.push(...b.calls);
                if (b.thought) allThoughts.push(b.thought);
            } else if (b.type === 'planner_response' && b.content) {
                textResponses.push(b.content);
            }
        });

        if (allCalls.length > 0 || allThoughts.length > 0) {
            const shouldOpen = isLastTurn && isThinking;
            const boxId = isLastTurn ? 'unified-tool-calls-box' : \`tool-calls-box-\${Math.random().toString(36).substr(2, 9)}\`;
            const listId = isLastTurn ? 'unified-tool-calls-list' : \`tool-calls-list-\${Math.random().toString(36).substr(2, 9)}\`;

            let callsHtml = '';
            if (allCalls.length > 0) {
                callsHtml = allCalls.map(renderToolCallHtml).join('');
            }
            
            let thoughtHtml = '';
            if (allThoughts.length > 0) {
                const combinedThought = allThoughts.join('\\n\\n').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                thoughtHtml = \`<div class="agent-thought" style="padding: 8px; font-size: 0.8rem; color: var(--text-muted); background: rgba(0,0,0,0.05); border-left: 2px solid var(--primary, #5645c5); margin-bottom: 8px; white-space: pre-wrap;">\${combinedThought}</div>\`;
            }

            const headerText = (allCalls.length > 0) ? \`Tool Calls (\${allCalls.length})\` : \`Agent Thinking...\`;

            html += \`
            <div class="chat-message agent tool-call-group" style="margin-top: 16px;">
                <div class="message-content" style="width: 100%;">
                    <details class="group tool-calls-box" id="\${boxId}" \${shouldOpen ? 'open' : ''}>
                        <summary class="historical-summary">
                            <span>\${headerText}</span>
                            <span class="toggle-icon">▶</span>
                        </summary>
                        <div class="historical-details unified-tool-calls-list" id="\${listId}" style="max-height: 50vh; overflow-y: auto;">
                            \${thoughtHtml}
                            \${callsHtml}
                        </div>
                    </details>
                </div>
            </div>
            \`
        }

        textResponses.forEach(r => {
            const cleanedContent = r.replace(/<THREAD_NAME>[\\s\\S]*?<\\/THREAD_NAME>/g, '').trim()
            if (cleanedContent) {
                html += \`
                <div class="chat-message agent">
                    <div class="message-content group prose prose-sm prose-headings:text-gray-950 prose-pre:bg-gray-100 prose-pre:border">
                        <button class="copy-btn" data-content="\${encodeURIComponent(cleanedContent)}" onclick="navigator.clipboard.writeText(decodeURIComponent(this.getAttribute('data-content'))); this.textContent='Copied!'; setTimeout(() => this.textContent='Copy', 2000)">Copy</button>
                        <div class="text-content">\${marked.parse(cleanedContent)}</div>
                    </div>
                </div>
                \`
            }
        });
    });
`;

if (content.includes(targetStr)) {
    content = content.replace(targetStr, replaceStr);
    writeFileSync(path, content, 'utf8');
    console.log("Success");
} else {
    console.log("Target string not found.");
    // Write out actual to see why it failed
    writeFileSync('./tmp/actual.txt', content.substring(content.indexOf('let lastToolCallsBlock = null;')), 'utf8');
}
