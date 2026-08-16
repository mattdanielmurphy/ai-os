#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const PROXIMA_PATH = '/Users/matt/projects/external/Proxima';
const { IPCClient, AIProvider } = await import(path.join(PROXIMA_PATH, 'src/mcp/ipc-bridge.js'));
const { getAgentHubToken, getAgentHubPort } = await import(path.join(PROXIMA_PATH, 'src/mcp/helpers.js'));

const PERPLEXITY_MODEL_MAP = {
    'sonnet': 'claude50sonnetthinking',
    'sonar': 'turbo',
    'turbo': 'turbo',
    'grok': 'grok46medium',
    'grok-2': 'grok46medium',
    'grok46medium': 'grok46medium',
    'kimi': 'kimik3thinking',
    'k3': 'kimik3thinking',
    'kimik3thinking': 'kimik3thinking',
    'gpt': 'gpt56_terra_thinking',
    'gpt5': 'gpt56_terra_thinking',
    'terra': 'gpt56_terra_thinking',
    'gpt56_terra_thinking': 'gpt56_terra_thinking',
    'gemini': 'gemini37flashthinking',
    'gemini-3.7': 'gemini37flashthinking',
    'flash-thinking': 'gemini37flashthinking',
    'gemini37flashthinking': 'gemini37flashthinking',
    'glm': 'glm_5_2',
    'glm-5': 'glm_5_2',
    'glm5': 'glm_5_2',
    'glm_5_2': 'glm_5_2',
};

async function main() {
    const args = process.argv.slice(2);
    let providerName = 'perplexity';
    let rawModel = null;
    let message = '';
    let filePath = null;
    let outputPath = null;
    let inputFile = null;
    let timeoutMs = 600000;
    let recoverMode = false;
    let conversationId = crypto.randomUUID();

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
        } else if (args[i] === '--thread' || args[i] === '-c' || args[i] === '--continue') {
            const nextArg = args[i + 1];
            if (nextArg && !nextArg.startsWith('-')) {
                conversationId = args[++i];
            }
        } else if (args[i] === '--new' || args[i] === '-n') {
            // conversationId already defaults to randomUUID()
        } else if (!message) {
            message = args[i];
        }
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (!message && !recoverMode) {
        console.error('Usage: node query_proxima.js "<message>" [--provider <name>] [--model <model>] [--input <file>] [--output <file>] [--timeout <sec>] [--recover] [--thread <id> | --continue [id]] [--new]');
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

    const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'sonnet' : 'default');
    console.error(`[query_proxima] Querying ${providerName} (model: ${modelDisplay}, thread: ${conversationId}, timeout: ${timeoutMs / 1000}s, recover: ${recoverMode})...`);

    // 1. Try querying native Tauri AI-OS server directly (port 3031)
    try {
        const pingController = new AbortController();
        const pingTimeout = setTimeout(() => pingController.abort(), 1000);
        const pingRes = await fetch('http://127.0.0.1:3031/v1/models', { signal: pingController.signal }).catch(() => null);
        clearTimeout(pingTimeout);

        if (pingRes && pingRes.ok) {
            console.error(`[query_proxima] Connected to native Tauri AI-OS server on 127.0.0.1:3031`);
            const endpoint = baseProvider === 'gemini' 
                ? 'http://127.0.0.1:3031/api/gemini/query' 
                : 'http://127.0.0.1:3031/api/perplexity/query';

            const queryController = new AbortController();
            const queryTimeout = setTimeout(() => queryController.abort(), timeoutMs);

            const payload = {
                prompt: message,
                model: resolvedEngine,
                session_id: conversationId,
                file_path: filePath ? path.resolve(filePath) : null,
            };

            const queryRes = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: queryController.signal,
            });
            clearTimeout(queryTimeout);

            if (queryRes.ok) {
                const data = await queryRes.json();
                const response = data.response;
                if (response) {
                    if (outputPath) {
                        fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
                        fs.writeFileSync(outputPath, response, 'utf8');
                        console.error(`[query_proxima] Output written to ${outputPath}`);
                    } else {
                        console.log(response);
                    }
                    process.exit(0);
                }
            } else {
                const errText = await queryRes.text();
                console.error(`[query_proxima] Tauri returned error (${queryRes.status}): ${errText}. Falling back to Proxima IPC...`);
            }
        }
    } catch (e) {
        // Fall back to Proxima IPC
    }

    // 2. Fallback to Proxima Electron IPC
    try {
        const port = getAgentHubPort() || 19222;
        const token = getAgentHubToken();
        const client = new IPCClient(port, token);
        const provider = new AIProvider(providerName, client, () => true);

        let response = '';
        if (recoverMode) {
            const startTime = Date.now();
            while (Date.now() - startTime < timeoutMs) {
                try {
                    const result = await provider.executeScript(`
                        (function() {
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
                response = await provider.chat(message, true, filePath, resolvedEngine, conversationId);
            }
        } else {
            response = await provider.chat(message, true, filePath, resolvedEngine, conversationId);
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

