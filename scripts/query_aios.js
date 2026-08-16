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

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--provider' || args[i] === '-p') {
            provider = (args[++i] || 'perplexity').toLowerCase();
        } else if (args[i] === '--model' || args[i] === '-m') {
            rawModel = (args[++i] || 'sonnet').toLowerCase();
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
        console.error('Usage: node query_aios.js "<prompt>" [--provider perplexity|gemini] [--model sonnet|sonar] [--input <file>] [--output <file>] [--timeout <sec>] [--ui]');
        process.exit(1);
    }

    const resolvedModel = PPLX_MODEL_MAP[rawModel] || rawModel;
    const baseUrl = 'http://127.0.0.1:3031';

    try {
        if (uiOnly || provider === 'gemini') {
            const endpoint = provider === 'perplexity' ? `${baseUrl}/api/perplexity/prompt` : `${baseUrl}/api/gemini/prompt`;
            console.error(`[query_aios] Dispatching UI prompt to ${provider} window...`);
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message, model: resolvedModel }),
                signal: AbortSignal.timeout(timeoutSec * 1000)
            });

            if (!res.ok) {
                const text = await res.text();
                throw new Error(`Server returned ${res.status}: ${text}`);
            }

            console.error(`[query_aios] Prompt successfully dispatched to ${provider} webview.`);
            process.exit(0);
        }

        // Synchronous query evaluation for Perplexity
        console.error(`[query_aios] Querying Perplexity in ai-os (model: ${rawModel}, timeout: ${timeoutSec}s)...`);
        const res = await fetch(`${baseUrl}/api/perplexity/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: message,
                model: resolvedModel
            }),
            signal: AbortSignal.timeout(timeoutSec * 1000)
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Server error (${res.status}): ${errText}`);
        }

        const data = await res.json();
        const answer = data.response || '';

        if (!answer) {
            throw new Error('Received empty response from Perplexity');
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
