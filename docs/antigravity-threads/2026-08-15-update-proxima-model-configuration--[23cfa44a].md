---
title: "Update Proxima Model Configuration"
date: "2026-08-15"
conversation_id: "23cfa44a-d8e9-437d-8620-32f2017a9996"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please perform the following file updates:

1. Target File: `/Users/matt/projects/ai-os/scripts/query_proxima.js`
Instruction: Add `--model` / `-m` argument parsing, enforce `sonnet` (default) and `sonar` for Perplexity with friendly validation error for invalid models, and pass the resolved model engine to `provider.chat`.
Replace the entire content of `/Users/matt/projects/ai-os/scripts/query_proxima.js` with:
```javascript

#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const PROXIMA_PATH = '/Users/matt/projects/external/Proxima';
const { IPCClient, AIProvider } = await import(path.join(PROXIMA_PATH, 'src/mcp/ipc-bridge.js'));
const { getAgentHubToken, getAgentHubPort } = await import(path.join(PROXIMA_PATH, 'src/mcp/helpers.js'));

const PERPLEXITY_MODEL_MAP = {
    'sonnet': 'claude50sonnetthinking',
    'sonar': 'turbo',
};

async function main() {
    const args = process.argv.slice(2);
    let providerName = 'perplexity';
    let rawModel = null;
    let message = '';
    let filePath = null;
    let outputPath = null;
    let inputFile = null;
    let timeoutMs = 600000; // 10 minutes default
    let recoverMode = false;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--provider' || args[i] === '-p') {
            providerName = args[++i];
        } else if (args[i] === '--model' || args[i] === '-m') {
            rawModel = args[++i];
        } else if (args[i] === '--file' || args[i] === '-f') {
            filePath = args[++i];
        } else if (args[i] === '--input' || args[i] === '-i') {
            inputFile = args[++i];
        } else if (args[i] === '--output' || args[i] === '-o') {
            outputPath = args[++i];
        } else if (args[i] === '--timeout' || args[i] === '-t') {
            timeoutMs = parseInt(args[++i], 10) * 1000;
        } else if (args[i] === '--recover' || args[i] === '--wait-active') {
            recoverMode = true;
        } else if (!message) {
            message = args[i];
        }
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (!message && !recoverMode) {
        console.error('Usage: node query_proxima.js "<message>" [--provider <name>] [--model <model>] [--input <file>] [--output <file>] [--timeout <sec>] [--recover]');
        process.exit(1);
    }

    let resolvedEngine = null;
    const baseProvider = (providerName || '').split(':')[0].toLowerCase();
    if (baseProvider === 'perplexity') {
        const requestedModel = (rawModel || 'sonnet').toLowerCase();
        if (!PERPLEXITY_MODEL_MAP[requestedModel]) {
            console.error(`Error: Invalid model "${rawModel}" for provider "perplexity".`);
            console.error(`Available model params: 'sonnet' (default), 'sonar'.`);
            process.exit(1);
        }
        resolvedEngine = PERPLEXITY_MODEL_MAP[requestedModel];
    } else {
        resolvedEngine = rawModel || null;
    }

    const port = getAgentHubPort() || 19222;
    const token = getAgentHubToken();
    const client = new IPCClient(port, token);
    const provider = new AIProvider(providerName, client, () => true);

    try {
        const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'sonnet' : 'default');
        console.error(`[query_proxima] Querying ${providerName} (model: ${modelDisplay}, timeout: ${timeoutMs / 1000}s, recover: ${recoverMode})...`);
        
        let response = '';
        if (recoverMode) {
            // Wait for active generation in webview or cache
            const startTime = Date.now();
            while (Date.now() - startTime < timeoutMs) {
                try {
                    const result = await provider.executeScript(`
                        (function() {
                            // Check if page is currently streaming or has completed answer
                            var isStreaming = document.querySelector('.animate-pulse') || document.querySelector('[data-testid="loading"]');
                            var markdownEl = document.querySelector('.prose') || document.querySelector('[data-testid="answer-content"]');
                            return {
                                streaming: !!isStreaming,
                                text: markdownEl ? markdownEl.innerText : ''
                            };
                        })()
                    `);
                    if (result && result.text && !result.streaming) {
                        response = result.text;
                        break;
                    }
                } catch (e) { }
                await new Promise(r => setTimeout(r, 2000));
            }
            if (!response && message) {
                // Fallback to sending if recovery didn't find active text
                response = await provider.chat(message, true, filePath, resolvedEngine);
            }
        } else {
            response = await provider.chat(message, true, filePath, resolvedEngine);
        }

        if (!response) {
            throw new Error('Empty response received from provider');
        }

        if (outputPath) {
            fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
            fs.writeFileSync(outputPath, response, 'utf8');
            console.error(`[query_proxima] Output written to ${outputPath}`);
        } else {
            console.log(response);
        }
        process.exit(0);
    } catch (err) {
        console.error(`[query_proxima] Error: ${err.message}`);
        process.exit(1);
    }
}

main();
```

2. Target File: `/Users/matt/projects/external/Proxima/electron/providers/api.cjs`
Instruction: Add safe console wrappers at the top of `api.cjs` so no console call can ever throw EPIPE.
Replace lines 1-12:
```javascript

// Proxima — Provider API Manager.
// Loads engine scripts into BrowserViews.

for (const stream of [process.stdout, process.stderr]) {
    if (stream && typeof stream.on === 'function') {
        stream.on('error', (err) => {
            if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED')) return;
        });
    }
}

const fs = require('fs');
```

With:
```javascript

// Proxima — Provider API Manager.
// Loads engine scripts into BrowserViews.

for (const stream of [process.stdout, process.stderr]) {
    if (stream && typeof stream.on === 'function') {
        stream.on('error', (err) => {
            if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED')) return;
        });
    }
}

const safeWrapConsole = (fn) => {
    return (...args) => {
        try {
            fn.apply(console, args);
        } catch (err) {
            if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED' || (typeof err.message === 'string' && err.message.includes('EPIPE')))) {
                return;
            }
        }
    };
};
console.log = safeWrapConsole(console.log);
console.error = safeWrapConsole(console.error);
console.warn = safeWrapConsole(console.warn);
console.info = safeWrapConsole(console.info);
console.debug = safeWrapConsole(console.debug);

const fs = require('fs');
```

3. Target File: `/Users/matt/projects/external/Proxima/electron/providers/engines/perplexity-engine.js`
Instruction: Update `send()` in `perplexity-engine.js` to default to `claude50sonnetthinking` ('sonnet') and map 'sonar'/'turbo' to 'turbo'.
Replace lines 301-325:
```javascript

    async function send(message, engine, attachments, sessionId) {
        // Isolate this conversation's follow-up thread before building params.
        activateSession(sessionId);

        var sessionToken = _getSessionToken();
        var frontendUuid = _uuid();

        var params = {
            last_backend_uuid: _lastBackendUuid || _uuid(),
            read_write_token: sessionToken || '',
            attachments: (attachments && attachments.imageToken) ? [attachments.imageToken] : [],
            language: navigator.language || 'en-US',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
            search_focus: 'internet',
            sources: ['web'],
            frontend_uuid: frontendUuid,
            mode: 'copilot',
            model_preference: engine || 'turbo',
```

With:
```javascript

    async function send(message, engine, attachments, sessionId) {
        // Isolate this conversation's follow-up thread before building params.
        activateSession(sessionId);

        var sessionToken = _getSessionToken();
        var frontendUuid = _uuid();

        var modelPref = 'claude50sonnetthinking';
        if (engine === 'sonar' || engine === 'turbo') {
            modelPref = 'turbo';
        } else if (engine === 'sonnet' || engine === 'claude50sonnetthinking') {
            modelPref = 'claude50sonnetthinking';
        } else if (engine && engine !== 'auto') {
            modelPref = engine;
        }

        var params = {
            last_backend_uuid: _lastBackendUuid || _uuid(),
            read_write_token: sessionToken || '',
            attachments: (attachments && attachments.imageToken) ? [attachments.imageToken] : [],
            language: navigator.language || 'en-US',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
            search_focus: 'internet',
            sources: ['web'],
            frontend_uuid: frontendUuid,
            mode: 'copilot',
            model_preference: modelPref,
```

</span>



<span title="Responded at 7:38am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested file updates have been completed successfully:

1.  Added `--model` / `-m` argument parsing and validation to [`query_proxima.js`](file:///Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_proxima.js).
2.  Added safe console wrappers to prevent EPIPE errors in [`api.cjs`](file:///Users/matt/projects/external/Proxima/electron/providers/api.cjs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/electron/providers/api.cjs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/electron/providers/api.cjs).
3.  Updated model preference logic in [`perplexity-engine.js`](file:///Users/matt/projects/external/Proxima/electron/providers/engines/perplexity-engine.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/electron/providers/engines/perplexity-engine.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/electron/providers/engines/perplexity-engine.js) to default to `claude50sonnetthinking` ('sonnet') and map 'sonar'/'turbo' to 'turbo'.

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~37k | 2:40am 🔴 (expired) | ~37k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>