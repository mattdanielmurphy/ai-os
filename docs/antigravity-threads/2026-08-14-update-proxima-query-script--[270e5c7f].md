---
title: "Update Proxima Query Script"
date: "2026-08-14"
conversation_id: "270e5c7f-74d2-4f0f-b1b4-0786bec0e914"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/projects/ai-os/scripts/query_proxima.js:
Add support for:
1. `--recover` or `--wait-active`: If an MCP tool call times out in Antigravity, Proxima is still generating the response in its webview. This flag polls the provider's active webview / cache until generation completes and outputs the final result.
2. Standard query execution with `--input`, `--output`, `--timeout`, and `--provider`.

```javascript

#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const PROXIMA_PATH = '/Users/matt/projects/external/Proxima';
const { IPCClient, AIProvider } = await import(path.join(PROXIMA_PATH, 'src/mcp/ipc-bridge.js'));

async function main() {
    const args = process.argv.slice(2);
    let providerName = 'perplexity';
    let message = '';
    let filePath = null;
    let outputPath = null;
    let inputFile = null;
    let timeoutMs = 600000; // 10 minutes default
    let recoverMode = false;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--provider' || args[i] === '-p') {
            providerName = args[++i];
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
        console.error('Usage: node query_proxima.js "<message>" [--provider <name>] [--input <file>] [--output <file>] [--timeout <sec>] [--recover]');
        process.exit(1);
    }

    const client 
<truncated 474 bytes>
ry {
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
                response = await provider.chat(message, true, filePath);
            }
        } else {
            response = await provider.chat(message, true, filePath);
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

Make sure it is saved and marked executable.

</span>



<span title="Responded at 1:41am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Completed successfully. `/Users/matt/projects/ai-os/scripts/query_proxima.js` has been updated and marked as executable.

</span>



</span>

</span>