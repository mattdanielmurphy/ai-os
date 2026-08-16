#!/usr/bin/env bun
// AI-OS Code Intelligence CLI
// Usage:
//   bun tools/code-intel/cli.js analyze <file> [--question "..."] [--symbols "foo,bar"] [--max-lines 500]
//   bun tools/code-intel/cli.js pack <dir> [--out <file>]
//   bun tools/code-intel/cli.js tree <dir>
//   bun tools/code-intel/cli.js map <file>

import fs from 'fs';
import path from 'path';
import { buildSymbolMap, smartSlice, sliceBySymbols, getFileOverview } from './smart-slicer.js';
import { packCodebase } from './codebase-packer.js';
import { generateTreeStringWithLineCounts } from './file-tree.js';
import { extractSymbols } from './symbol-extractor.js';

function printHelp() {
    console.log(`
AI-OS Code Intelligence CLI

Commands:
  analyze <file>              Smart-slice or map a source code file
    --question <str>          Target question to score & slice relevant functions
    --symbols <a,b,c>         Explicit symbol names to extract with auto-dependencies
    --max-lines <num>         Maximum lines budget (default: 500)
    --no-imports              Omit imports block
    --no-map                  Omit top symbol map

  map <file>                  Print structured symbol map of a file
  tree <dir>                  Print directory tree with line counts
  pack <dir>                  Pack codebase into AI-ready context with secret scan
    --out <file>              Save packed bundle to file

Examples:
  bun tools/code-intel/cli.js map src/server.rs
  bun tools/code-intel/cli.js analyze src/server.rs --question "How does query callback routing work?"
  bun tools/code-intel/cli.js analyze src/server.rs --symbols "handle_gemini_query,resolve_query_callback"
  bun tools/code-intel/cli.js pack ./apps/gemini-companion --out ./tmp/companion_pack.md
`);
}

function parseArgs(args) {
    const options = {};
    const positionals = [];

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg.startsWith('--')) {
            const key = arg.slice(2);
            if (key.startsWith('no-')) {
                options[key.slice(3)] = false;
            } else if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
                options[key] = args[++i];
            } else {
                options[key] = true;
            }
        } else {
            positionals.push(arg);
        }
    }
    return { command: positionals[0], target: positionals[1], options };
}

async function main() {
    const { command, target, options } = parseArgs(process.argv.slice(2));

    if (!command || command === 'help' || command === '--help' || command === '-h') {
        printHelp();
        process.exit(0);
    }

    if (!target) {
        console.error(`Error: Missing target file or directory for command "${command}"`);
        printHelp();
        process.exit(1);
    }

    const targetPath = path.resolve(process.cwd(), target);
    if (!fs.existsSync(targetPath)) {
        console.error(`Error: Target path does not exist: ${targetPath}`);
        process.exit(1);
    }

    switch (command) {
        case 'map': {
            const content = fs.readFileSync(targetPath, 'utf8');
            console.log(buildSymbolMap(content, targetPath));
            break;
        }
        case 'overview': {
            const content = fs.readFileSync(targetPath, 'utf8');
            console.log(getFileOverview(content, targetPath));
            break;
        }
        case 'symbols': {
            const content = fs.readFileSync(targetPath, 'utf8');
            const syms = extractSymbols(content, targetPath);
            console.log(JSON.stringify(syms, null, 2));
            break;
        }
        case 'analyze': {
            const content = fs.readFileSync(targetPath, 'utf8');
            if (options.symbols) {
                const symList = options.symbols.split(',').map(s => s.trim());
                const result = sliceBySymbols(content, targetPath, symList, {
                    includeImports: options.imports !== false,
                    includeMap: options.map !== false,
                });
                console.log(`=== SYMBOL SLICE (Savings: ${result.savings} | Sent ${result.sentLines}/${result.totalLines} lines) ===\n`);
                console.log(result.sliced);
            } else {
                const question = options.question || '';
                const maxLines = options['max-lines'] ? parseInt(options['max-lines'], 10) : 500;
                const result = smartSlice(content, targetPath, question, {
                    maxLines,
                    includeImports: options.imports !== false,
                    includeMap: options.map !== false,
                });
                console.log(`=== SMART SLICE (Savings: ${result.savings} | Sent ${result.sentLines}/${result.totalLines} lines | Mode: ${result.mode}) ===\n`);
                console.log(result.sliced);
            }
            break;
        }
        case 'pack': {
            const res = packCodebase(targetPath, options);
            if (!res.success) {
                console.error(`Pack error: ${res.error}`);
                process.exit(1);
            }
            console.log(`Packed ${res.metrics.totalFiles} files (${res.metrics.totalLines} lines, ~${res.metrics.totalTokens} tokens) in ${res.metrics.packDurationMs}ms`);
            if (res.secretWarnings.length > 0) {
                console.warn(`⚠️ Potential secrets detected in ${res.secretWarnings.length} files:`);
                for (const w of res.secretWarnings) {
                    console.warn(`  - ${w.file}: ${w.types.join(', ')}`);
                }
            }
            if (options.out) {
                const outPath = path.resolve(process.cwd(), options.out);
                fs.mkdirSync(path.dirname(outPath), { recursive: true });
                fs.writeFileSync(outPath, res.packed, 'utf8');
                console.log(`Saved output to ${outPath}`);
            } else {
                console.log(res.packed);
            }
            break;
        }
        case 'tree': {
            const res = packCodebase(targetPath, options);
            if (res.fileTree) {
                console.log(res.fileTree);
            }
            break;
        }
        default:
            console.error(`Unknown command: ${command}`);
            printHelp();
            process.exit(1);
    }
}

main().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
