#!/usr/bin/env node
import fs from 'fs';
import http from 'http';
import path from 'path';
import crypto from 'crypto';
import { execSync, spawn } from 'child_process';

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

const MAX_PROMPT_CHARS = 35000; // Perplexity character limit is ~40k; 35k ensures safe ceiling including formatting

function extractAndInlineReferencedFiles(text, availableBudget = MAX_PROMPT_CHARS) {
    if (!text) return { inlinedText: '', attachedFilePath: null };

    const pathRegex = /(?:file:\/\/)?(\/(?:Users|Volumes|private|tmp|var)[^\s"'`<>]+)/g;
    const matches = new Set();
    let m;
    while ((m = pathRegex.exec(text)) !== null) {
        let rawPath = m[1];
        try {
            rawPath = decodeURIComponent(rawPath);
        } catch (e) {}
        rawPath = rawPath.replace(/[.,:;!?\)]+$/, '');
        matches.add(rawPath);
    }

    let inlinedSections = [];
    let candidateAttachment = null;
    let currentInlinedChars = 0;

    for (const filePath of matches) {
        try {
            if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
                const stat = fs.statSync(filePath);
                const content = fs.readFileSync(filePath, 'utf8');
                const fileHeader = `\n--- Referenced File Context: ${filePath} ---\n`;
                const fileFooter = `\n--- End of ${path.basename(filePath)} ---\n`;
                const formattedSection = `${fileHeader}${content}${fileFooter}`;

                if (currentInlinedChars + formattedSection.length <= availableBudget) {
                    inlinedSections.push(formattedSection);
                    currentInlinedChars += formattedSection.length;
                    console.error(`[query_aios] 📎 Automatically inlined referenced file: ${filePath} (${stat.size} bytes, fits in prompt budget)`);
                } else if (!candidateAttachment) {
                    candidateAttachment = filePath;
                    console.error(`[query_aios] ⚠️ File ${filePath} (${stat.size} bytes / ${content.length} chars) exceeds available prompt budget (${availableBudget} chars). Selected as attachment.`);
                }
            }
        } catch (e) {
            // Ignore unreadable or non-existent file paths
        }
    }

    return {
        inlinedText: inlinedSections.join('\n'),
        attachedFilePath: candidateAttachment
    };
}

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

    // 1. Base instructions template length calculation
    const baseInstructions = `\n\nPlease act as a senior architect and systems planner. Analyze the request and output a detailed, actionable implementation plan for the orchestrator.

The plan MUST include:
1. Architectural Strategy: High-level overview of the proposed approach.
2. Data Structures & State Management: Define new data structures or changes to existing state.
3. API/Interface Contracts: Define function signatures, classes, and expected interface contracts.
4. Logic Flow & Algorithms: Step-by-step pseudo-code or logic description for the main execution flow.
5. Error Handling & Edge Cases: Identify potential failure points and mitigation strategies.
6. Implementation Steps: A list of specific files to modify and the required changes in each, ordered for execution.

DO NOT provide full code implementations. Focus on structural details, signatures, and clear instructions so that downstream agents can implement the changes efficiently without guessing. Ensure all decisions are concrete and leave no gaps in requirements.`;

    const imageContext = imageDesc ? `\n--- Visual Context & Image Description ---\n${imageDesc}\n` : '';

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

    // 4. Keyword match agent logs
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

    // 5. Thread History Summary
    let historyContext = '';
    const tmpDir = path.resolve('./tmp');
    if (fs.existsSync(tmpDir)) {
        try {
            const files = fs.readdirSync(tmpDir).filter(f => f.endsWith('.txt') && !f.includes('prompt') && !f.includes('output'));
            if (files.length > 0) {
                const latest = files.sort((a, b) => fs.statSync(path.join(tmpDir, b)).mtime - fs.statSync(path.join(tmpDir, a)).mtime)[0];
                const content = fs.readFileSync(path.join(tmpDir, latest), 'utf8');
                historyContext = `\n--- Recent Thread History Summary ---\n${content.slice(-1000)}\n`;
            }
        } catch (e) {}
    }

    // Calculate fixed overhead chars
    const fixedOverhead = userRequest.length + imageContext.length + agContextStr.length + repoInfo.length + logContext.length + historyContext.length + baseInstructions.length;
    const remainingBudget = Math.max(0, MAX_PROMPT_CHARS - fixedOverhead);

    // Auto-resolve referenced files in userRequest respecting remaining budget
    const { inlinedText, attachedFilePath } = extractAndInlineReferencedFiles(userRequest, remainingBudget);

    const fullPrompt = `User Request: ${userRequest}
${inlinedText}${imageContext}${agContextStr}${repoInfo}${logContext}${historyContext}${baseInstructions}`;

    return {
        prompt: fullPrompt,
        attachedFilePath: attachedFilePath
    };
}

async function pingAios(baseUrl) {
    return new Promise((resolve) => {
        const url = `${baseUrl}/v1/models`;
        const req = http.get(url, (res) => {
            resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.on('timeout', () => { req.destroy(); resolve(false); });
        req.setTimeout(2000);
    });
}

function sendAiosRequest(url, payload, timeoutSec) {
    return new Promise((resolve, reject) => {
        const u = new URL(url);
        const data = JSON.stringify(payload);
        const options = {
            hostname: u.hostname,
            port: u.port,
            path: u.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data),
            },
            timeout: timeoutSec * 1000,
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try { resolve(JSON.parse(body)); } catch (e) { resolve(body); }
                } else {
                    reject(new Error(`Server returned ${res.statusCode}: ${body}`));
                }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Request timed out')); });
        req.write(data);
        req.end();
    });
}

async function main() {
    const args = process.argv.slice(2);
    let provider = 'perplexity';
    let rawModel = 'gemini';
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

    const THINKING_MODELS = ['grok', 'grok-thinking', 'grok_thinking', 'grok-2', 'grok46medium', 'sonnet', 'claude50sonnetthinking', 'gemini', 'gemini-3.7', 'flash-thinking', 'gemini37flashthinking', 'kimi', 'k3', 'kimik3thinking', 'gpt', 'gpt5', 'terra', 'gpt56_terra_thinking', 'glm', 'glm-5', 'glm5', 'glm_5_2'];
    const isThinkingModel = THINKING_MODELS.includes(rawModel) || isPlanMode;
    const minAllowedTimeout = isThinkingModel ? 300 : 120;
    const defaultTimeout = isThinkingModel ? 600 : 300;

    if (timeoutSec !== null && timeoutSec < minAllowedTimeout) {
        const userTimeout = timeoutSec;
        timeoutSec = minAllowedTimeout;
        const modelDisplay = rawModel || (provider === 'perplexity' ? 'gemini' : 'default');
        console.error(`[query_aios] Note: Requested timeout of ${userTimeout}s is too short for ${modelDisplay} (thinking models require adequate reasoning time). Enforcing minimum timeout floor of ${minAllowedTimeout}s.`);
    }

    if (isPlanMode) {
        if (!timeoutSec) timeoutSec = defaultTimeout;
        if (!outputPath) outputPath = './tmp/planner_output.txt';
        if (message) {
            const { prompt: generatedPrompt, attachedFilePath } = buildPlannerPrompt(message, imageDesc);
            fs.mkdirSync('./tmp', { recursive: true });
            fs.writeFileSync('./tmp/planner_prompt.txt', generatedPrompt, 'utf8');
            console.error(`[query_aios] Planner prompt generated at ./tmp/planner_prompt.txt (${generatedPrompt.length} chars)`);
            message = generatedPrompt;
            if (!filePath && attachedFilePath) {
                filePath = attachedFilePath;
                console.error(`[query_aios] 📎 Attached file parameter set: ${filePath}`);
            }
        }
    } else {
        if (!timeoutSec) timeoutSec = defaultTimeout;
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (message && !isPlanMode) {
        const { inlinedText, attachedFilePath } = extractAndInlineReferencedFiles(message);
        if (inlinedText) {
            message = `${message}\n${inlinedText}`;
        }
        if (!filePath && attachedFilePath) {
            filePath = attachedFilePath;
        }
    }

    if (!message && !recoverMode) {
        console.error('Usage: node query_aios.js "<prompt>" [--plan "<request>"] [--provider perplexity|gemini] [--model sonnet|sonar|gemini|gpt|grok|kimi|glm] [--thread <id>] [--input <file>] [--output <file>] [--timeout <sec>] [--recover] [--ui]');
        process.exit(1);
    }

    let resolvedModel = null;
    const baseProvider = (provider || '').split(':')[0].toLowerCase();
    if (baseProvider === 'perplexity') {
        const requestedModel = (rawModel || 'gemini').toLowerCase();
        resolvedModel = PPLX_MODEL_MAP[requestedModel] || requestedModel;
    } else {
        resolvedModel = rawModel || null;
    }

    const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'gemini' : 'default');
    const startTime = Date.now();
    console.error(`[query_aios] Querying ${provider} via AI-OS (model: ${modelDisplay}, thread: ${sessionId}, timeout: ${timeoutSec}s)... (waiting for response)`);

    const baseUrl = 'http://127.0.0.1:3031';

    let serverReady = await pingAios(baseUrl);
    if (!serverReady) {
        console.error(`[query_aios] 🔄 AI-OS server at http://127.0.0.1:3031 is not responding. Starting via launch agent...`);
        try {
            execSync('la start aios-server 2>/dev/null', { stdio: 'ignore' });
        } catch (e) {}

        for (let i = 0; i < 60; i++) {
            await new Promise(r => setTimeout(r, 1000));
            serverReady = await pingAios(baseUrl);
            if (serverReady) {
                console.error(`[query_aios] ✅ AI-OS server is online.`);
                break;
            }
        }
    }

    if (!serverReady) {
        console.error(`\n[query_aios] ERROR: AI-OS server is unreachable (http://127.0.0.1:3031).`);
        console.error(`Check status with: la status aios-server or tail logs at ~/.ai-os/logs/companion_server.error.log\n`);
        process.exit(1);
    }

    try {
        if (uiOnly) {
            const endpoint = baseProvider === 'perplexity' ? `${baseUrl}/api/perplexity/prompt` : `${baseUrl}/api/gemini/prompt`;
            console.error(`[query_aios] Dispatching UI prompt to ${provider} window...`);
            await sendAiosRequest(endpoint, { prompt: message, model: resolvedModel, session_id: sessionId }, timeoutSec);
            console.error(`[query_aios] Prompt successfully dispatched to ${provider} webview.`);
            process.exit(0);
        }

        const endpoint = baseProvider === 'gemini'
            ? `${baseUrl}/api/gemini/query`
            : `${baseUrl}/api/perplexity/query`;

        const data = await sendAiosRequest(endpoint, {
            prompt: message,
            model: resolvedModel,
            session_id: sessionId,
            file_path: filePath ? path.resolve(filePath) : null,
        }, timeoutSec);
        const answer = data.response || '';

        if (!answer) {
            throw new Error(`Received empty response from AI-OS for ${provider}`);
        }

        const endTime = Date.now();
        const elapsed = ((endTime - startTime) / 1000).toFixed(2);
        const chars = answer.length;
        const words = answer.split(/\s+/).length;
        const lines = answer.split('\n').length;

        if (outputPath) {
            fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
            fs.writeFileSync(outputPath, answer, 'utf8');
            console.error(`[query_aios] ✅ Final output received (${chars} chars, ${elapsed}s) and saved to ${outputPath}`);
        }

        console.log('================================================================================');
        console.log('🎉 [AI-OS QUERY COMPLETE — FINAL OUTPUT RECEIVED]');
        console.log(`Provider: ${provider}`);
        console.log(`Model: ${modelDisplay}`);
        console.log(`Session / Thread ID: ${sessionId}`);
        console.log(`Elapsed time: ${elapsed}s`);
        console.log(`Character count: ${chars}`);
        console.log(`Word count: ${words}`);
        console.log(`Line count: ${lines}`);
        if (outputPath) console.log(`Saved To: ${outputPath}`);
        console.log('--------------------------------------------------------------------------------');
        console.log(answer);
        console.log('================================================================================');
        console.log('🏁 [END OF AI-OS FINAL OUTPUT]');
        console.log('================================================================================');

        process.exit(0);
    } catch (err) {
        console.error(`[query_aios] Error: ${err.message}`);
        process.exit(1);
    }
}

main();
