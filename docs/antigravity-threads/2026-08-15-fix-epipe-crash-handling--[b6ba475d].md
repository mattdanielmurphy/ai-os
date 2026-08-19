---
title: "Fix EPIPE Crash Handling"
date: "2026-08-15"
conversation_id: "b6ba475d-6508-4e59-a7b1-99281e04ac2e"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please make the following edits to fix EPIPE / broken pipe crashes across Proxima:

1. Target File: `/Users/matt/projects/external/Proxima/electron/main-v2.cjs`
Instruction: Add stdio EPIPE safety handlers, safe console wrapper, and uncaughtException/unhandledRejection suppression at the top of the file right under `// Proxima — Electron Main Process.`.
Replace:
```javascript

// Proxima — Electron Main Process.

const { app, BrowserWindow, ipcMain, shell, session, clipboard, safeStorage } = require('electron');
```

With:
```javascript

// Proxima — Electron Main Process.

// Prevent EPIPE / broken pipe crashes when running headless, daemonized, or when stdio is closed
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

process.on('uncaughtException', (err) => {
    if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED' || (typeof err.message === 'string' && err.message.includes('EPIPE')))) {
        return;
    }
    try {
        console.error('[Main Process] Uncaught exception:', err);
    } catch (_) {}
});

process.on('unhandledRejection', (reason) => {
    if (reason && (reason.code === 'EPIPE' || reason.code === 'ERR_STREAM_DESTROYED' || (typeof reason?.message === 'string' && reason.message.includes('EPIPE')))) {
        return;
    }
    try {
        console.error('[Main Process] Unhandled rejection:', reason);
    } catch (_) {}
});

const { app, BrowserWindow, ipcMain, shell, session, clipboard, safeStorage } = require('electron');
```

2. Target File: `/Users/matt/projects/external/Proxima/electron/providers/api.cjs`
Instruction: Add stdio stream error listeners at the top, and wrap response/error logging in sendViaAPI to protect against EPIPE.
Replace:
```javascript

// Proxima — Provider API Manager.
// Loads engine scripts into BrowserViews.

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

const fs = require('fs');
```

And replace:
```javascript

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        const charCount = result ? result.length : 0;
        console.log(`[ProviderAPI] [OK] ${provider} API response: ${charCount} chars in ${elapsed}s`);

        return result || null;
    } catch (e) {
        console.error(`[ProviderAPI] [FAIL] ${provider} API error:`, e.message);
        throw e;
    }
```

With:
```javascript

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        const charCount = result ? result.length : 0;
        try {
            console.log(`[ProviderAPI] [OK] ${provider} API response: ${charCount} chars in ${elapsed}s`);
        } catch (_) {}

        return result || null;
    } catch (e) {
        try {
            console.error(`[ProviderAPI] [FAIL] ${provider} API error:`, e.message);
        } catch (_) {}
        throw e;
    }
```

3. Target File: `/Users/matt/projects/external/Proxima/src/mcp/index.js`
Instruction: Add stdio error listeners and uncaughtException handler for EPIPE.
Replace:
```javascript

for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
    try { process.once(sig, () => shutdown(0)); } catch (e) { /* signal unsupported here */ }
}
// stdin EOF/close == the MCP client closed the pipe → we're orphaned → exit.
try {
    process.stdin.on('end', () => shutdown(0));
    process.stdin.on('close', () => shutdown(0));
} catch (e) { /* ignore */ }
```

With:
```javascript

for (const stream of [process.stdout, process.stderr]) {
    if (stream && typeof stream.on === 'function') {
        stream.on('error', (err) => {
            if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED')) {
                shutdown(0);
            }
        });
    }
}

process.on('uncaughtException', (err) => {
    if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED' || (typeof err.message === 'string' && err.message.includes('EPIPE')))) {
        shutdown(0);
        return;
    }
    try { console.error('[MCP] Uncaught exception:', err); } catch (_) {}
});

for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
    try { process.once(sig, () => shutdown(0)); } catch (e) { /* signal unsupported here */ }
}
// stdin EOF/close == the MCP client closed the pipe → we're orphaned → exit.
try {
    process.stdin.on('end', () => shutdown(0));
    process.stdin.on('close', () => shutdown(0));
} catch (e) { /* ignore */ }
```

4. Target File: `/Users/matt/projects/external/Proxima/cli/proxima-cli.cjs`
Instruction: Add EPIPE suppression on stdout and stderr in the CLI.
Replace:
```javascript

const http = require('http');
const fs = require('fs');
const path = require('path');
```

With:
```javascript

for (const stream of [process.stdout, process.stderr]) {
    if (stream && typeof stream.on === 'function') {
        stream.on('error', (err) => {
            if (err && (err.code === 'EPIPE' || err.code === 'ERR_STREAM_DESTROYED')) {
                process.exit(0);
            }
        });
    }
}

const http = require('http');
const fs = require('fs');
const path = require('path');
```

</span>



<span title="Responded at 7:30am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested edits to fix EPIPE / broken pipe crashes across the Proxima codebase have been successfully applied:

*   **Electron Main Process**: Updated [`main-v2.cjs`](file:///Users/matt/projects/external/Proxima/electron/main-v2.cjs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/electron/main-v2.cjs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/electron/main-v2.cjs) to include comprehensive EPIPE safety handlers, a safe console wrapper, and suppression of uncaught exceptions and unhandled rejections related to broken pipes.
*   **Provider API Manager**: Updated [`api.cjs`](file:///Users/matt/projects/external/Proxima/electron/providers/api.cjs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/electron/providers/api.cjs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/electron/providers/api.cjs) to add stdio stream error listeners and protected logging calls against EPIPE errors.
*   **MCP Index**: Updated [`index.js`](file:///Users/matt/projects/external/Proxima/src/mcp/index.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/src/mcp/index.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/src/mcp/index.js) to include stdio error listeners and a handler for uncaught exceptions, triggering a clean shutdown if a broken pipe is detected.
*   **CLI**: Updated [`proxima-cli.cjs`](file:///Users/matt/projects/external/Proxima/cli/proxima-cli.cjs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/external/Proxima/cli/proxima-cli.cjs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/external/Proxima/cli/proxima-cli.cjs) to add EPIPE error suppression on `stdout` and `stderr`.

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~36k | 2:30am 🔴 (expired) | ~36k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>