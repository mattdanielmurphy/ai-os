#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

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
        } else if (!message) {
            message = args[i];
        }
    }

    if (inputFile && fs.existsSync(inputFile)) {
        message = fs.readFileSync(inputFile, 'utf8');
    }

    if (!message) {
        console.error('Usage: node query_proxima.js "<message>" [--provider <name>] [--input <file>] [--output <file>] [--timeout <sec>]');
        process.exit(1);
    }

    const client = new IPCClient(19222);
    const provider = new AIProvider(providerName, client, () => true);

    try {
        console.error(`[query_proxima] Querying ${providerName} (timeout: ${timeoutMs / 1000}s)...`);
        const response = await provider.chat(message, false, filePath);
        
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
