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

