#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

const PPLX_MODEL_MAP = {
    'grok': 'grok46medium',
    'grok-thinking': 'grok46medium',
    'grok_thinking': 'grok46medium',
    'grok-2': 'grok46medium',
    'grok46medium': 'grok46medium',
    'sonnet': 'claude50sonnetthinking',
    'sonar': 'turbo',
    'turbo': 'turbo',
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

function buildPlannerPrompt(userRequest, imageDesc = null) {
    let gitRoot = null;
    let repoName = null;
    try {
        const isGit = execSync('git rev-parse --is-inside-work-tree', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
        if (isGit === 'true') {
            gitRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
            const remoteUrl = execSync('git config --get remote.origin.url', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
            const m = remoteUrl.match(/github\.com[:\/]([^\/]+\/[^\/.]+)/);
            if (m) repoName = m[1].replace(/\.git$/, '');
        }
    } catch (e) {
        // Non-git or error
    }

    // 1. Keyword match agent logs
    let logContext = '';
    const logDirs = [path.resolve('./agent-logs'), gitRoot ? path.join(gitRoot, 'agent-logs') : null].filter(Boolean);
    const keywords = (userRequest.toLowerCase().match(/\w+/g) || []).filter(w => w.length > 3);
    const matchingLogs = [];

    for (const dir of logDirs) {
        if (fs.existsSync(dir)) {
            try {
                const files = fs.readdirSync(dir).filter(f => f.endsWith('.log') || f.endsWith('.md'));
                for (const file of files) {
                    const filePath = path.join(dir, file);
                    try {
                        const content = fs.readFileSync(filePath, 'utf8');
                        const lowerContent = content.toLowerCase();
                        if (keywords.some(k => lowerContent.includes(k))) {
                            matchingLogs.push({ name: file, path: filePath });
                            if (matchingLogs.length >= 3) break;
                        }
                    } catch (e) {}
                }
            } catch (e) {}
        }
        if (matchingLogs.length >= 3) break;
    }

    if (matchingLogs.length > 0) {
        logContext = '\n--- Relevant Agent Logs ---\n';
        for (const log of matchingLogs) {
            try {
                const lines = fs.readFileSync(log.path, 'utf8').split('\n');
                const summary = lines.slice(-10).join('\n');
                logContext += `\nFile: ${log.name}\n${summary}\n`;
            } catch (e) {}
        }
    }

    // 2. AG_CONTEXT.md
    let agContextStr = '';
    const agPaths = [path.resolve('./AG_CONTEXT.md'), gitRoot ? path.join(gitRoot, 'AG_CONTEXT.md') : null].filter(Boolean);
    for (const p of agPaths) {
        if (fs.existsSync(p)) {
            try {
                agContextStr = '\n--- AG_CONTEXT.md ---\n' + fs.readFileSync(p, 'utf8') + '\n';
                break;
            } catch (e) {}
        }
    }

    // 3. GitHub Connector info
    let repoInfo = '';
    if (repoName) {
        repoInfo = (
            `\n--- GitHub Connector Context ---\n` +
            `Target Private Repository: '${repoName}'\n` +
            `IMPORTANT: You have access to my authenticated GitHub account via your GitHub connector. ` +
            `Please use your GitHub connector to directly read, search, and inspect the codebase, files, and documentation ` +
            `in my repository '${repoName}' (including private files and configs) as needed to construct this plan.\n`
        );
    }

    const imageContext = imageDesc ? `\n--- Visual Context & Image Description ---\n${imageDesc}\n` : '';

    return `User Request: ${userRequest}
${imageContext}${agContextStr}${repoInfo}${logContext}

Please act as a senior architect and systems planner. Analyze the request and output a detailed, actionable implementation plan for the orchestrator.

The plan MUST include:
1. Architectural Strategy: High-level overview of the proposed approach.
2. Data Structures & State Management: Define new data structures or changes to existing state.
3. API/Interface Contracts: Define function signatures, classes, and expected interface contracts.
4. Logic Flow & Algorithms: Step-by-step pseudo-code or logic description for the main execution flow.
5. Error Handling & Edge Cases: Identify potential failure points and mitigation strategies.
6. Implementation Steps: A list of specific files to modify and the required changes in each, ordered for execution.

DO NOT provide full code implementations. Focus on structural details, signatures, and clear instructions so that downstream agents can implement the changes efficiently without guessing. Ensure all decisions are concrete and leave no gaps in requirements.`;
}

async function main() {
    const args = process.argv.slice(2);
    let provider = 'perplexity';
    let rawModel = 'grok';
    let message = '';
    let inputFile = null;
    let outputPath = null;
    let timeoutSec = null;
    let uiOnly = false;
    let sessionId = crypto.randomUUID();
    let isPlanMode = false;
    let imageDesc = null;
    let recoverMode = false;
    let filePath = null;

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--provider' || arg === '-p') {
            provider = (args[++i] || 'perplexity').toLowerCase();
        } else if (arg === '--model' || arg === '-m') {
            rawModel = (args[++i] || 'sonnet').toLowerCase();
        } else if (arg === '--plan' || arg === '--planner') {
            isPlanMode = true;
            const nextArg = args[i + 1];
            if (nextArg && !nextArg.startsWith('-')) {
                message = args[++i];
            }
        } else if (arg === '--image-desc') {
            imageDesc = args[++i];
        } else if (arg === '--file' || arg === '-f') {
            filePath = args[++i];
        } else if (arg === '--thread' || arg === '--session' || arg === '-s' || arg === '-c' || arg === '--continue') {
            const nextArg = args[i + 1];
            if (nextArg && !nextArg.startsWith('-')) {
                sessionId = args[++i];
            }
        } else if (arg === '--new' || arg === '-n') {
            sessionId = crypto.randomUUID();
        } else if (arg === '--input' || arg === '-i') {
            inputFile = args[++i];
        } else if (arg === '--output' || arg === '-o') {
            outputPath = args[++i];
        } else if (arg === '--timeout' || arg === '-t') {
            timeoutSec = parseInt(args[++i], 10);
        } else if (arg === '--recover' || arg === '--wait-active') {
            recoverMode = true;
        } else if (arg === '--ui' || arg === '--prompt-only') {
            uiOnly = true;
        } else if (!message && !arg.startsWith('-')) {
            message = arg;
        }
    }

    if (isPlanMode) {
        if (!timeoutSec) timeoutSec = 600;
        if (!outputPath) outputPath = './tmp/planner_output.txt';
        if (message) {
            const generatedPrompt = buildPlannerPrompt(message, imageDesc);
            fs.mkdirSync('./tmp', { recursive: true });
            fs.writeFileSync('./tmp/planner_prompt.txt', generatedPrompt, 'utf8');
            console.error(`[query_aios] Planner prompt generated at ./tmp/planner_prompt.txt`);
            message = generatedPrompt;
        }
    } else {
        if (!timeoutSec) timeoutSec = 180;
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (!message && !recoverMode) {
        console.error('Usage: node query_aios.js "<prompt>" [--plan "<request>"] [--provider perplexity|gemini] [--model sonnet|sonar|gemini|gpt|grok|kimi|glm] [--thread <id>] [--input <file>] [--output <file>] [--timeout <sec>] [--recover] [--ui]');
        process.exit(1);
    }

    let resolvedModel = null;
    const baseProvider = (provider || '').split(':')[0].toLowerCase();
    if (baseProvider === 'perplexity') {
        const requestedModel = (rawModel || 'grok').toLowerCase();
        resolvedModel = PPLX_MODEL_MAP[requestedModel] || requestedModel;
    } else {
        resolvedModel = rawModel || null;
    }

    const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'grok' : 'default');
    console.error(`[query_aios] Querying ${provider} (model: ${modelDisplay}, thread: ${sessionId}, timeout: ${timeoutSec}s, plan: ${isPlanMode}, recover: ${recoverMode})...`);

    const baseUrl = 'http://127.0.0.1:3031';

    try {
        if (uiOnly) {
            const endpoint = baseProvider === 'perplexity' ? `${baseUrl}/api/perplexity/prompt` : `${baseUrl}/api/gemini/prompt`;
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

        // 1. Try querying native Tauri AI-OS server directly (port 3031)
        try {
            const pingController = new AbortController();
            const pingTimeout = setTimeout(() => pingController.abort(), 1000);
            const pingRes = await fetch(`${baseUrl}/v1/models`, { signal: pingController.signal }).catch(() => null);
            clearTimeout(pingTimeout);

            if (pingRes && pingRes.ok && !recoverMode) {
                console.error(`[query_aios] Connected to native Tauri AI-OS server on 127.0.0.1:3031`);
                const endpoint = baseProvider === 'gemini'
                    ? `${baseUrl}/api/gemini/query`
                    : `${baseUrl}/api/perplexity/query`;

                const queryRes = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: message,
                        model: resolvedModel,
                        session_id: sessionId,
                        file_path: filePath ? path.resolve(filePath) : null,
                    }),
                    signal: AbortSignal.timeout(timeoutSec * 1000)
                });

                if (queryRes.ok) {
                    const data = await queryRes.json();
                    answer = data.response || '';
                } else {
                    const errText = await queryRes.text();
                    console.error(`[query_aios] Tauri returned error (${queryRes.status}): ${errText}. Falling back to Proxima IPC...`);
                }
            }
        } catch (tauriErr) {
            // Fall back to Proxima IPC
        }

        // 2. Fallback to Proxima Electron IPC if answer is still empty
        if (!answer) {
            const PROXIMA_PATH = '/Users/matt/projects/external/Proxima';
            const { IPCClient, AIProvider } = await import(path.join(PROXIMA_PATH, 'src/mcp/ipc-bridge.js'));
            const { getAgentHubToken, getAgentHubPort } = await import(path.join(PROXIMA_PATH, 'src/mcp/helpers.js'));

            const port = getAgentHubPort() || 19222;
            const token = getAgentHubToken();
            const client = new IPCClient(port, token);
            const aiProvider = new AIProvider(baseProvider, client, () => true);

            if (recoverMode) {
                const startTime = Date.now();
                const timeoutMs = timeoutSec * 1000;
                while (Date.now() - startTime < timeoutMs) {
                    try {
                        const result = await aiProvider.executeScript(`
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
                            answer = result.text;
                            break;
                        }
                    } catch (e) {}
                    await new Promise(r => setTimeout(r, 2000));
                }
                if (!answer && message) {
                    answer = await aiProvider.chat(message, true, filePath, resolvedModel, sessionId);
                }
            } else {
                answer = await aiProvider.chat(message, true, filePath, resolvedModel, sessionId);
            }
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
