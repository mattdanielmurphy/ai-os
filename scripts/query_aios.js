#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const PPLX_MODEL_MAP = {
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
    'auto': 'auto',
};

async function main() {
    const args = process.argv.slice(2);
    let provider = 'perplexity';
    let rawModel = 'sonnet';
    let message = '';
    let inputFile = null;
    let outputPath = null;
    let timeoutSec = 180;
    let uiOnly = false;
    let sessionId = null;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--provider' || args[i] === '-p') {
            provider = (args[++i] || 'perplexity').toLowerCase();
        } else if (args[i] === '--model' || args[i] === '-m') {
            rawModel = (args[++i] || 'sonnet').toLowerCase();
        } else if (args[i] === '--thread' || args[i] === '--session' || args[i] === '-s') {
            sessionId = args[++i];
        } else if (args[i] === '--input' || args[i] === '-i') {
            inputFile = args[++i];
        } else if (args[i] === '--output' || args[i] === '-o') {
            outputPath = args[++i];
        } else if (args[i] === '--timeout' || args[i] === '-t') {
            timeoutSec = parseInt(args[++i], 10) || 180;
        } else if (args[i] === '--ui' || args[i] === '--prompt-only') {
            uiOnly = true;
        } else if (!message && !args[i].startsWith('-')) {
            message = args[i];
        }
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (!message) {
        console.error('Usage: node query_aios.js "<prompt>" [--provider perplexity|gemini] [--model sonnet|sonar|gemini|gpt|grok|kimi|glm] [--thread <id>] [--input <file>] [--output <file>] [--timeout <sec>] [--ui]');
        process.exit(1);
    }

    const resolvedModel = PPLX_MODEL_MAP[rawModel] || rawModel;
    const baseUrl = 'http://127.0.0.1:3031';

    try {
        if (uiOnly) {
            const endpoint = provider === 'perplexity' ? `${baseUrl}/api/perplexity/prompt` : `${baseUrl}/api/gemini/prompt`;
            console.error(`[query_aios] Dispatching UI prompt to ${provider} window...`);
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message, model: resolvedModel, session_id: sessionId }),
                signal: AbortSignal.timeout(timeoutSec * 1000)
            });

            if (!res.ok) {
                const text = await res.text();
                throw new Error(`Server returned ${res.status}: ${text}`);
            }

            console.error(`[query_aios] Prompt successfully dispatched to ${provider} webview.`);
            process.exit(0);
        }

        let answer = '';

        if (provider === 'perplexity') {
            const modelDisplay = rawModel || 'sonnet';
            console.error(`[query_aios] Querying perplexity in ai-os (model: ${modelDisplay}, timeout: ${timeoutSec}s)...`);
            
            try {
                const PROXIMA_PATH = '/Users/matt/projects/external/Proxima';
                const { IPCClient, AIProvider } = await import(path.join(PROXIMA_PATH, 'src/mcp/ipc-bridge.js'));
                const { getAgentHubToken, getAgentHubPort } = await import(path.join(PROXIMA_PATH, 'src/mcp/helpers.js'));
                
                const port = getAgentHubPort() || 19222;
                const token = getAgentHubToken();
                const client = new IPCClient(port, token);
                const pplxProvider = new AIProvider('perplexity', client, () => true);
                
                const threadId = sessionId || crypto.randomUUID();
                answer = await pplxProvider.chat(message, true, null, resolvedModel, threadId);
            } catch (ipcErr) {
                console.error(`[query_aios] IPC direct error (${ipcErr.message}), falling back to HTTP 3031...`);
                const queryEndpoint = `${baseUrl}/api/perplexity/query`;
                const res = await fetch(queryEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: message,
                        model: resolvedModel,
                        session_id: sessionId
                    }),
                    signal: AbortSignal.timeout(timeoutSec * 1000)
                });
                if (!res.ok) {
                    const errText = await res.text();
                    throw new Error(`Server error (${res.status}): ${errText}`);
                }
                const data = await res.json();
                answer = data.response || '';
            }
        } else {
            // Gemini query via companion HTTP
            const queryEndpoint = `${baseUrl}/api/gemini/query`;
            const modelDisplay = rawModel || 'auto';
            console.error(`[query_aios] Querying ${provider} in ai-os (model: ${modelDisplay}, timeout: ${timeoutSec}s)...`);
            
            const res = await fetch(queryEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: message,
                    model: resolvedModel,
                    session_id: sessionId
                }),
                signal: AbortSignal.timeout(timeoutSec * 1000)
            });

            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`Server error (${res.status}): ${errText}`);
            }

            const data = await res.json();
            answer = data.response || '';
        }

        if (!answer) {
            throw new Error(`Received empty response from ${provider}`);
        }

        if (outputPath) {
            fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
            fs.writeFileSync(outputPath, answer, 'utf8');
            console.error(`[query_aios] Response written to ${outputPath}`);
        } else {
            console.log(answer);
        }

        process.exit(0);
    } catch (err) {
        console.error(`[query_aios] Error: ${err.message}`);
        process.exit(1);
    }
}

main();
