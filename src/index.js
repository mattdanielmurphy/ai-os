#!/usr/bin/env node
import { FinancialGovernor, ProcessWatchdog, killActiveProcesses } from './circuitBreaker.js';
import { GatewayLogger, colors } from './logger.js';
import { WarmPtySession, cleanPtyOutput } from './ptyWrapper.js';
import { calculateCost, formatTokens, loadPricing } from './pricing.js';
import { execSync, spawn } from 'child_process';

import { DeterministicSandbox } from './sandbox.js';
import { extractMetadata } from './extractor.js';
import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { validateCommand } from './commandValidator.js';

// 1. Parse .env file locally without requiring dotenv dependency
const PROJECT_ROOT = process.cwd();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CODEBASE_ROOT = path.resolve(__dirname, '..');

function loadEnvFile(filePath) {
  if (fs.existsSync(filePath)) {
    const envContent = fs.readFileSync(filePath, 'utf8');
    envContent.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const index = trimmed.indexOf('=');
        if (index !== -1) {
          const key = trimmed.substring(0, index).trim();
          const value = trimmed.substring(index + 1).trim();
          process.env[key] = value;
        }
      }
    });
  }
}

// Load codebase root .env first, then cwd .env (which can override it)
loadEnvFile(path.join(CODEBASE_ROOT, '.env'));
loadEnvFile(path.join(PROJECT_ROOT, '.env'));

// 2. Determine default model
const DEFAULT_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';

// 3. Parse arguments for mode, files, flags, and query robustly
const args = process.argv.slice(2);

let isInteractive = false;
let hasUserFlag = false;
let hasDebugFlag = false;
let modeVal = null;
let filePath = null;
let listSuggestions = false;
let resolveSuggestionId = null;
let cliModel = null;
const queryArgs = [];

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg.startsWith('--mode=')) {
    modeVal = arg.split('=')[1];
  } else if (arg === '--user' || arg === '-user') {
    hasUserFlag = true;
  } else if (arg === '--debug' || arg === '-debug') {
    hasDebugFlag = true;
  } else if (arg.startsWith('--file=')) {
    filePath = arg.split('=')[1];
  } else if (arg === '--interactive' || arg === '-interactive' || arg === '-i') {
    isInteractive = true;
  } else if (arg === '--suggestions' || arg === '-suggestions') {
    listSuggestions = true;
  } else if (arg.startsWith('--resolve-suggestion=')) {
    resolveSuggestionId = parseInt(arg.split('=')[1], 10);
  } else if (arg.startsWith('--model=')) {
    cliModel = arg.split('=')[1];
  } else if ((arg === '--model' || arg === '-model' || arg === '-m') && i + 1 < args.length) {
    cliModel = args[i + 1];
    i++;
  } else if (arg.startsWith('-')) {
    // Ignore other unknown flags
  } else {
    queryArgs.push(arg);
  }
}

const mode = hasUserFlag ? 'user' : (hasDebugFlag ? 'debug' : (modeVal || process.env.GATEWAY_MODE || 'debug'));
const query = queryArgs.join(' ').trim();

const logger = new GatewayLogger(mode);
let sandbox = new DeterministicSandbox(PROJECT_ROOT);
const governor = new FinancialGovernor(1.00, logger); 
const ptySession = new WarmPtySession(undefined, logger); 

/**
 * Technical Git Version Control Utility
 */
function autoCommit(message) {
  try {
    execSync('git add .', { stdio: 'ignore' });
    // Check if there are staged changes to commit
    const status = execSync('git status --porcelain', { encoding: 'utf8' }).trim();
    if (status) {
      logger.debug(`Auto-committing changes: "${message}"`);
      execSync(`git commit -m "${message}"`, { stdio: 'ignore' });
    } else {
      logger.debug(`No changes to commit.`);
    }
  } catch (err) {
    logger.debug(`No changes to commit or not a git repository.`);
  }
}

// Active Suggestion Resolution ID
let activeResolveId = null;

function getSuggestionsPath() {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  return path.join(homeDir, '.ai-os', 'suggestions.json');
}

function loadGlobalSuggestions() {
  const filePath = getSuggestionsPath();
  if (fs.existsSync(filePath)) {
    try {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
      return [];
    }
  }
  return [];
}

function saveGlobalSuggestions(suggestions) {
  const filePath = getSuggestionsPath();
  const dirPath = path.dirname(filePath);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  fs.writeFileSync(filePath, JSON.stringify(suggestions, null, 2), 'utf8');
}

function appendSuggestion(suggestionData) {
  const suggestions = loadGlobalSuggestions();
  const maxId = suggestions.reduce((max, s) => s.id > max ? s.id : max, 0);
  const newSuggestion = {
    id: maxId + 1,
    timestamp: new Date().toISOString(),
    status: 'pending',
    ...suggestionData
  };
  suggestions.push(newSuggestion);
  saveGlobalSuggestions(suggestions);
  return newSuggestion;
}

function markSuggestionResolved(id) {
  const suggestions = loadGlobalSuggestions();
  const index = suggestions.findIndex(s => s.id === id);
  if (index !== -1) {
    suggestions[index].status = 'resolved';
    suggestions[index].resolved_at = new Date().toISOString();
    saveGlobalSuggestions(suggestions);
  }
}

function handleSuggestionsCommand() {
  const suggestions = loadGlobalSuggestions();
  const pending = suggestions.filter(s => s.status === 'pending');
  if (pending.length === 0) {
    console.log(`\n🎉 ${colors.bold}${colors.green}No pending optimization suggestions found!${colors.reset}\n`);
    return;
  }

  console.log(`\n${colors.bold}${colors.lightBlue}━━ PENDING OPTIMIZATION SUGGESTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`);
  pending.forEach((s) => {
    const dateStr = s.timestamp ? new Date(s.timestamp).toLocaleString() : 'No Timestamp';
    console.log(`\n${colors.bold}ID: ${s.id}${colors.reset} | ${colors.dim}${dateStr}${colors.reset} | Type: ${colors.lightYellow}${s.type}${colors.reset}`);
    console.log(`  ${colors.bold}Project Path:${colors.reset} ${s.project_root}`);
    console.log(`  ${colors.bold}Original Query:${colors.reset} "${s.query}"`);
    console.log(`  ${colors.bold}Description:${colors.reset} ${s.description}`);
    console.log(`  ${colors.bold}Recommendation:${colors.reset} ${colors.green}${s.recommendation}${colors.reset}`);
  });
  console.log(`\n${colors.bold}${colors.lightBlue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);
  console.log(`To resolve a suggestion, run: ai-os --resolve-suggestion=<id>\n`);
}

// Global Token Counters
let threadPromptTokens = 0;
let threadCandidatesTokens = 0;
let threadTotalTokens = 0;

let currentQueryPromptTokens = 0;
let currentQueryCandidatesTokens = 0;
let currentQueryTotalTokens = 0;

// Global Cost Trackers
let threadCost = 0.0;
let currentQueryCost = 0.0;

/**
 * Reads local rulebook and ledger context
 */
function readContext() {
  const stateLedgerPath = path.join(PROJECT_ROOT, 'state_ledger.json');
  const rulebookPath = path.join(PROJECT_ROOT, 'rulebook.md');
  
  let state = {};
  if (fs.existsSync(stateLedgerPath)) {
    state = JSON.parse(fs.readFileSync(stateLedgerPath, 'utf8'));
  }
  
  let rulebook = '';
  if (fs.existsSync(rulebookPath)) {
    rulebook = fs.readFileSync(rulebookPath, 'utf8');
  }

  return { state, rulebook };
}

/**
 * Checks if the Antigravity allocation is completely tapped out.
 * Reads the local settings file or runs a rapid, truncated diagnostic check.
 */
function checkAgyHealth() {
  try {
    const homeDir = process.env.HOME || process.env.USERPROFILE || '';
    const settingsPath = path.join(homeDir, '.gemini/antigravity-cli/settings.json');
    
    if (fs.existsSync(settingsPath)) {
      const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
      if (settings.use_g1_credits === 'off' && settings.quota_status === 'depleted') {
        return { healthy: false, reason: "Baseline quota exhausted and G1 overage credits are disabled." };
      }
    }
    return { healthy: true };
  } catch (e) {
    return { healthy: true };
  }
}

/**
 * Appends a new rule permanently to rulebook.md.
 */
function modifyRulebook(rule) {
  const rulebookPath = path.join(PROJECT_ROOT, 'rulebook.md');
  let content = '';
  if (fs.existsSync(rulebookPath)) {
    content = fs.readFileSync(rulebookPath, 'utf8');
  }
  
  let ruleText = rule.trim();
  if (!ruleText.startsWith('-')) {
    ruleText = `- ${ruleText}`;
  }
  
  if (content && !content.endsWith('\n')) {
    content += '\n';
  }
  content += `${ruleText}\n`;
  
  try {
    sandbox.writeFile(rulebookPath, content, true);
    logger.info(`Appended rule to rulebook.md: "${ruleText}"`);
  } catch (err) {
    logger.error(`Failed to write to rulebook.md: ${err.message}`);
  }
}

/**
 * Appends a path declaration permanently under the ## Environment & Paths section in AG_CONTEXT.md.
 */
function modifyContext(pathDeclaration) {
  const contextPath = path.join(PROJECT_ROOT, 'AG_CONTEXT.md');
  let content = '';
  if (fs.existsSync(contextPath)) {
    content = fs.readFileSync(contextPath, 'utf8');
  }
  
  let pathText = pathDeclaration.trim();
  if (!pathText.startsWith('-')) {
    pathText = `- ${pathText}`;
  }
  
  if (content.includes('## Environment & Paths')) {
    const lines = content.split('\n');
    const index = lines.findIndex(line => line.trim() === '## Environment & Paths');
    lines.splice(index + 1, 0, pathText);
    content = lines.join('\n');
  } else {
    if (content && !content.endsWith('\n')) {
      content += '\n';
    }
    content += `\n## Environment & Paths\n${pathText}\n`;
  }
  
  try {
    sandbox.writeFile(contextPath, content, true);
    logger.info(`Added path declaration to AG_CONTEXT.md: "${pathText}"`);
  } catch (err) {
    logger.error(`Failed to write to AG_CONTEXT.md: ${err.message}`);
  }
}


/**
 * Call Gemini API via agy CLI using PTY
 */
/*
async function callGemini(model, systemInstruction, promptOrContents, useJson = false) {
  let promptText = '';
  if (systemInstruction) {
    promptText += `${systemInstruction}\n\n`;
  }
  
  if (Array.isArray(promptOrContents)) {
    promptText += JSON.stringify(promptOrContents);
  } else {
    promptText += promptOrContents;
  }

  return new Promise((resolve, reject) => {
    const args = ['--model', model || 'gemini-3.1-pro-low', '--dangerously-skip-permissions', '-p', '-'];
    
    if (typeof updateTuiStats === 'function') {
      updateTuiStats('Executing task via agy...');
    }

    const child = spawn('/Users/matthewmurphy/.local/bin/agy', args, {
      cwd: '/tmp',
      env: process.env,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    child.stdin.write(promptText);
    child.stdin.end();

    let outputBuffer = '';
    let resolved = false;

    function extractJson(str) {
      const match = str.match(/```json\n([\s\S]*?)\n```/);
      if (match) {
        try {
          JSON.parse(match[1]);
          return match[1];
        } catch(e) {}
      }
      let startObj = str.indexOf('{');
      let startArr = str.indexOf('[');
      let startIndex = (startObj !== -1 && startArr !== -1) ? Math.min(startObj, startArr) : Math.max(startObj, startArr);
      let endObj = str.lastIndexOf('}');
      let endArr = str.lastIndexOf(']');
      let endIndex = Math.max(endObj, endArr);
      if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
        try {
          const cleanStr = str.slice(startIndex, endIndex + 1).replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
          JSON.parse(cleanStr);
          return cleanStr;
        } catch(e) {}
      }
      return null;
    }

    child.stdout.on('data', (data) => {
      outputBuffer += data.toString();
      
      if (outputBuffer.trim().startsWith('Error: ')) {
         if (!resolved) {
             resolved = true;
             child.kill();
             resolve({ text: outputBuffer.trim(), usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
         }
         return;
      }
      
      if (useJson && !resolved) {
         const extracted = extractJson(outputBuffer);
         if (extracted) {
             resolved = true;
             child.kill();
             resolve({ text: extracted, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
         }
      }
      
      if (!resolved && outputBuffer.includes('[END_OF_RESPONSE]')) {
         resolved = true;
         child.kill();
         let finalOutput = outputBuffer.replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '').replace('[END_OF_RESPONSE]', '').trim();
         if (useJson) {
           const extracted = extractJson(finalOutput);
           if (extracted) finalOutput = extracted;
         }
         resolve({ text: finalOutput, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
      }
    });

    child.stderr.on('data', (data) => {
      const chunk = data.toString();
      if (chunk.trim().startsWith('Error: ') && !resolved) {
         resolved = true;
         child.kill();
         resolve({ text: chunk.trim(), usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
      }
    });

    child.on('exit', (code) => {
      if (!resolved) {
        resolved = true;
        const cleanStr = outputBuffer.replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
        resolve({ text: cleanStr, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
      }
    });

    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        child.kill();
        const cleanStr = outputBuffer.replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
        resolve({ text: cleanStr || "Timeout waiting for agy response", usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } });
      }
    }, 120000);
  });
}
*/

function extractJson(str) {
  const match = str.match(/```json\n([\s\S]*?)\n```/);
  if (match) {
    try {
      JSON.parse(match[1]);
      return match[1];
    } catch(e) {}
  }
  let startObj = str.indexOf('{');
  let startArr = str.indexOf('[');
  let startIndex = (startObj !== -1 && startArr !== -1) ? Math.min(startObj, startArr) : Math.max(startObj, startArr);
  let endObj = str.lastIndexOf('}');
  let endArr = str.lastIndexOf(']');
  let endIndex = Math.max(endObj, endArr);
  if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
    try {
      const cleanStr = str.slice(startIndex, endIndex + 1).replace(/\x1B\[[0-9;]*[a-zA-Z]/g, '');
      JSON.parse(cleanStr);
      return cleanStr;
    } catch(e) {}
  }
  return null;
}

async function callGemini(model, systemInstruction, promptOrContents, useJson = false) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return { text: "Error: GEMINI_API_KEY environment variable is missing.", usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } };
  }

  let promptText = '';
  if (Array.isArray(promptOrContents)) {
    promptText += JSON.stringify(promptOrContents);
  } else {
    promptText += promptOrContents;
  }

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model || 'gemini-2.5-flash'}:generateContent?key=${apiKey}`;

  const payload = {
    contents: [{ parts: [{ text: promptText }] }],
  };

  if (systemInstruction) {
    payload.systemInstruction = { parts: [{ text: systemInstruction }] };
  }

  if (useJson) {
    payload.generationConfig = { responseMimeType: "application/json" };
  }

  if (typeof updateTuiStats === 'function') {
    updateTuiStats('Executing task via Gemini API...');
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errText = await response.text();
      if (response.status === 503) {
        return { text: `Error: Gemini API 503 Service Unavailable. Triggering immediate fallback.`, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } };
      }
      return { text: `Error: Gemini API Error: ${response.status} ${response.statusText} - ${errText}`, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } };
    }

    const data = await response.json();
    let text = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
    const usage = data.usageMetadata || { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 };

    if (useJson) {
      const extracted = extractJson(text);
      if (extracted) text = extracted;
    }

    return { text, usage };
  } catch (err) {
    return { text: `Error: ${err.message}`, usage: { promptTokenCount: 0, candidatesTokenCount: 0, totalTokenCount: 0 } };
  }
}


/**
 * Direct API Action Executor (Fallback when agy is unavailable/rate-limited)
 */
async function executeInstructionDirectly(instruction, sandbox, logger, state, activeProjectRoot, budgetMode = 'ARCHITECTURAL', projectContext = {}, modelOverride = null) {
  logger.info(`Executing instruction via Direct API: "${instruction}"`);
  
  const { agContext, features, recentLogs, directoryStructure } = projectContext;

  const executionSystemInstruction = `
    # DIRECT API TASK EXECUTOR
    [BUDGET_MODE: ${budgetMode}]
    You are the execution engine of the AI-OS Gateway. Your job is to complete the given instruction by outputting a sequence of filesystem or terminal actions.
    
    You MUST output a raw JSON block matching this schema:
    {
      "action": "run_command" | "write_file" | "read_file" | "list_dir" | "done",
      "command": "shell command to run (if run_command)",
      "file_path": "path to the file to read or write (if write_file or read_file or list_dir)",
      "file_content": "complete content to write to the file (if write_file)",
      "explanation": "Why this action is taken."
    }
    
    CRITICAL RULES:
    1. Perform ONE action at a time. After each action, the gateway will execute it and return the result to you in the next turn so you can verify and decide on the next action.
    2. Strictly respect the rulebook. Never use "rm". Do not write files outside the workspace.
    3. When you have completed the instruction fully, return {"action": "done", "explanation": "Instruction completed successfully"}.
    4. **Directory Consideration & Nesting:** If the active directory is a generic parent directory (like ~/projects or /Users/matthewmurphy/projects), NEVER write files or initialize git repositories directly in it. You MUST first run a command or write files to create a dedicated, appropriately-named subfolder, switch to it, and work inside that subfolder. However, if the active directory is already a specific project directory (such as a subfolder under projects, e.g. /Users/matthewmurphy/projects/now-music, or contains files like package.json, src/, index.js, etc.), do NOT create a new project directory or subfolder. You must work directly within the active project directory.
    5. **No Command Misuse:** Never call internal actions like "read_file", "write_file", "list_dir", or "done" as shell commands (e.g. do NOT set "action": "run_command" and "command": "read_file ..."). Use the proper "action" values directly in the JSON response.
    6. **No "rm" allowed:** Running "rm" commands is strictly prohibited. The system will reject it.
    7. **Write File Content Requirement:** When using the "write_file" action, you MUST provide the complete, full new file content in the "file_content" field. The "file_content" field must never be empty, null, or undefined. Do not write partial or placeholder code.
    8. **External Path Approval:** If an action requires writing to a path outside the active project root or standard user directories (Documents, Desktop, etc.), you must explicitly state the path and the reason in your explanation.
    9. **Robust macOS Path Handling:** When dealing with paths containing spaces (like iCloud/Obsidian), always wrap the path in double quotes.
    10. **Golden Command for "Most Recent File":** To find the most recently modified non-hidden file in a directory, use: \`ls -t "/path/to/dir/" | grep -v / | grep -v "^\\." | head -n 1\`. This is more reliable than complex \`find\` pipes.
    11. **Robust Directory Listing:** To list directories by modification time, prefer `ls -t -d /path/*/ | xargs -n 1 basename` over complex `sed` or `awk` pipelines which often fail on hidden files or specific shell environments.
    ${budgetMode === 'LEAN' ? `
    CRITICAL LEAN BUDGET CONSTRAINT:
    The budget mode is set to LEAN. You must strictly limit all tool executions to single-file write configurations and complete the entire task in a single step.` : ''}
  `;

  let stepResult = "";
  let actionCount = 0;
  const maxActions = budgetMode === 'LEAN' ? 2 : 8;
  let done = false;
  let actionHistory = [];

  while (!done && actionCount < maxActions) {
    actionCount++;
    
    const prompt = `
      Project Context (AG_CONTEXT.md):
      ${agContext || 'None'}
 
      Project Features (FEATURES.md):
      ${features || 'None'}
 
      Recent Agent Logs (Context & Past Decisions):
      ${recentLogs || 'None'}
 
      Active Workspace Directory Structure:
      ${directoryStructure || 'Empty or unable to read'}
 
      Current Instruction: "${instruction}"
      Active Workspace Directory: "${activeProjectRoot}"
      
      Action History in this Step:
      ${actionHistory.length > 0 ? actionHistory.map((h, i) => `Action ${i + 1}: ${h.action} (${h.explanation})
Result:
${h.result}`).join('\n\n') : 'None'}
    `;

    let decision;
    try {
      const { text: rawResponse } = await callGemini(modelOverride || DEFAULT_MODEL, executionSystemInstruction, prompt, true);
      let jsonStr = rawResponse;
      const jsonStart = rawResponse.indexOf('{');
      const jsonEnd = rawResponse.lastIndexOf('}');
      if (jsonStart !== -1 && jsonEnd !== -1) {
        jsonStr = rawResponse.substring(jsonStart, jsonEnd + 1);
      }
      decision = JSON.parse(jsonStr);
      logger.debug(`Direct Exec Action ${actionCount}: ${JSON.stringify(decision, null, 2)}`);
    } catch (err) {
      logger.error(`Failed to get action decision from Gemini: ${err.message}`);
      return `Failed to execute instruction: ${err.message}`;
    }

    if (!decision.action || decision.action === 'undefined') {
      logger.warn(`Model returned undefined action. Forcing termination to prevent loop.`);
      done = true;
      break;
    }

    if (decision.action === 'done') {
      logger.info(`Direct execution completed: ${decision.explanation}`);
      done = true;
      break;
    }

    let result = "";
    try {
      if (decision.action === 'run_command') {
        const validation = validateCommand(decision.command);
        if (!validation.allowed) {
          logger.warn(`Command validation rejected: ${validation.reason}`);
          result = validation.reason;
        } else {
          const fullCommand = `cd ${JSON.stringify(activeProjectRoot)} && ${decision.command}`;
          logger.info(`Running command: ${fullCommand}`);
          result = await ProcessWatchdog.runSafeCommand(fullCommand, 30000, 100);
        }
      } else if (decision.action === 'write_file') {
        if (!decision.file_path) {
          logger.warn(`Write file validation rejected: file_path is missing or empty.`);
          result = "Error: write_file action rejected. You must provide a valid 'file_path'.";
        } else if (decision.file_content === undefined || decision.file_content === null) {
          logger.warn(`Write file validation rejected: file_content is undefined or null.`);
          result = "Error: write_file action rejected. You must provide a valid 'file_content' string containing the complete file content. 'file_content' cannot be undefined or null.";
        } else {
          logger.info(`Writing file: ${decision.file_path}`);
          const absolutePath = path.isAbsolute(decision.file_path)
            ? decision.file_path
            : path.resolve(activeProjectRoot, decision.file_path);
          sandbox.writeFile(absolutePath, decision.file_content, true);
          result = `Successfully wrote to ${decision.file_path}`;
        }
      } else if (decision.action === 'read_file') {
        logger.info(`Reading file: ${decision.file_path}`);
        const absolutePath = path.isAbsolute(decision.file_path)
          ? decision.file_path
          : path.resolve(activeProjectRoot, decision.file_path);
        if (fs.existsSync(absolutePath)) {
          result = fs.readFileSync(absolutePath, 'utf8');
        } else {
          result = `File not found: ${decision.file_path}`;
        }
      } else if (decision.action === 'list_dir') {
        logger.info(`Listing directory: ${decision.file_path || '.'}`);
        const targetDir = decision.file_path 
          ? (path.isAbsolute(decision.file_path) ? decision.file_path : path.resolve(activeProjectRoot, decision.file_path))
          : activeProjectRoot;
        if (fs.existsSync(targetDir)) {
          const files = fs.readdirSync(targetDir);
          result = files.map(f => {
            const stat = fs.statSync(path.join(targetDir, f));
            return `${f}${stat.isDirectory() ? '/' : ''}`;
          }).join('\n');
        } else {
          result = `Directory not found: ${decision.file_path}`;
        }
      } else {
        result = `Unknown action: ${decision.action}`;
      }
    } catch (execErr) {
      logger.error(`Error during action execution: ${execErr.message}`);
      result = `Error: ${execErr.message}`;
    }

    actionHistory.push({
      action: decision.action,
      explanation: decision.explanation,
      result: result
    });

    stepResult += `\nAction: ${decision.action} (${decision.explanation})\nResult:\n${result}\n`;
  }

  return stepResult.trim();
}

// Global Chat History
const chatHistory = [];
const THREAD_ID = `thread_${Date.now()}`;
let activeAbortController = null;
let isExecuting = false;
let lastSentMessage = "";

function loadPromptHistory() {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const historyFile = path.join(homeDir, '.ai-os', 'prompt_history.json');
  if (fs.existsSync(historyFile)) {
    try {
      return JSON.parse(fs.readFileSync(historyFile, 'utf8'));
    } catch (e) {
      return [];
    }
  }
  return [];
}

function savePrompt(promptText) {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const historyFile = path.join(homeDir, '.ai-os', 'prompt_history.json');
  const history = loadPromptHistory();
  if (history.length === 0 || history[history.length - 1] !== promptText) {
    history.push(promptText);
    if (history.length > 1000) {
      history.shift();
    }
    const dirPath = path.dirname(historyFile);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    fs.writeFileSync(historyFile, JSON.stringify(history, null, 2), 'utf8');
  }
}

function saveThreadHistory() {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const threadFile = path.join(homeDir, '.ai-os', 'threads', `${THREAD_ID}.json`);
  const dirPath = path.dirname(threadFile);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  fs.writeFileSync(threadFile, JSON.stringify(chatHistory, null, 2), 'utf8');
}

/**
 * Prompts the user with a question and returns the answer, reusing the active readline interface if available.
 */
let tuiActive = false;
function updateTuiStats(statusText = '') {}

let isPrompting = false;

async function askQuestion(queryText, rlInterface = null) {
  isPrompting = true;
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false);
  }
  let rl = rlInterface;
  const createdNew = !rl;
  if (createdNew) {
    rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  const answer = await new Promise((resolve) => {
    rl.question(queryText, (ans) => {
      resolve(ans);
    });
  });

  if (createdNew) {
    rl.close();
  }
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(true);
  }
  isPrompting = false;
  return answer;
}

/**
 * Helper to read project context (AG_CONTEXT.md, FEATURES.md, and recent agent logs)
 */
function readProjectContext(projectRoot) {
  let agContext = '';
  const agContextPath = path.join(projectRoot, 'AG_CONTEXT.md');
  if (fs.existsSync(agContextPath)) {
    agContext = fs.readFileSync(agContextPath, 'utf8');
  }

  let features = '';
  const featuresPath = path.join(projectRoot, 'FEATURES.md');
  if (fs.existsSync(featuresPath)) {
    features = fs.readFileSync(featuresPath, 'utf8');
  }

  let recentLogs = '';
  const logsDir = path.join(projectRoot, '.agent-logs');
  if (fs.existsSync(logsDir) && fs.statSync(logsDir).isDirectory()) {
    try {
      const files = fs.readdirSync(logsDir)
        .filter(f => f.endsWith('.md'))
        .sort((a, b) => b.localeCompare(a)) // Sort descending (newest first)
        .slice(0, 3);
      
      recentLogs = files.map(file => {
        const content = fs.readFileSync(path.join(logsDir, file), 'utf8');
        return `--- LOG: ${file} ---\n${content}`;
      }).join('\n\n');
    } catch (e) {
      // ignore
    }
  }

  let directoryStructure = '';
  try {
    if (fs.existsSync(projectRoot)) {
      const items = fs.readdirSync(projectRoot);
      directoryStructure = items.map(item => {
        const stat = fs.statSync(path.join(projectRoot, item));
        return `${item}${stat.isDirectory() ? '/' : ''}`;
      }).join('\n');
    }
  } catch (e) {
    // ignore
  }

  return { agContext, features, recentLogs, directoryStructure };
}

/**
 * CORE RUNTIME LOOP
 * The Synchronous Checklist Gateway Engine
 */
async function processGatewayRequest(userInput, attachedFilePath = null, rlInterface = null, modelOverride = null) {
  isExecuting = true;
  lastSentMessage = userInput;
  activeAbortController = new AbortController();
  savePrompt(userInput);

  try {
    currentQueryPromptTokens = 0;
    currentQueryCandidatesTokens = 0;
    currentQueryTotalTokens = 0;
    currentQueryCost = 0.0;
    updateTuiStats('Executing task...');

    let executionHistory = [];
    let resultText = "";

    logger.info(`Gateway Initiating (Mode: ${logger.mode.toUpperCase()})...`);

  logger.showQuery(userInput);

  // 2. Native File Scan (0-Tokens)
  let metadataText = "No attached file.";
  let metadata = null;
  if (attachedFilePath) {
    logger.info(`Analyzing attached file: ${path.basename(attachedFilePath)}...`);
    logger.debug(`Performing native file scan for ${attachedFilePath}`);
    metadata = extractMetadata(attachedFilePath);
    metadataText = JSON.stringify(metadata, null, 2);
    logger.debug(`Extracted 0-Token Metadata: ${metadata.sizeHuman}, ${metadata.lineCount} lines, Mime: ${metadata.mimeType}`);
  }

  // 3. Read Rulebook & State
  logger.debug(`Reading Living Rulebook & State Ledger`);
  const { state, rulebook } = readContext();

  // Dynamically update target root if query contains a project path
  const projectPathRegex = /(\/Users\/matthewmurphy\/[^\s'"]+)/;
  const match = userInput.match(projectPathRegex);
  if (match) {
    const matchedPath = match[1];
    if (fs.existsSync(matchedPath) && fs.statSync(matchedPath).isDirectory()) {
      state.project_target_root = matchedPath;
      logger.info(`Detected target project root in query: ${matchedPath}. Updating state ledger.`);
    }
  }

  let activeProjectRoot = PROJECT_ROOT;
  if (state.project_target_root && fs.existsSync(state.project_target_root)) {
    activeProjectRoot = state.project_target_root;
  }

  // Re-initialize sandbox for this request
  sandbox = new DeterministicSandbox(activeProjectRoot);

  const { agContext, features, recentLogs, directoryStructure } = readProjectContext(activeProjectRoot);

  // Construct history text for prompts
  const historyText = chatHistory.length > 0 
    ? chatHistory.map(h => `${h.role === 'user' ? 'User' : 'Model'}: ${h.parts[0].text}`).join('\n')
    : 'None';

  // 4. Executive Triage (Tier 2 / Gemini Triage Decisions)
  let decision;
  const modelToUse = modelOverride || cliModel;
  if (modelToUse) {
    logger.info(`Bypassing triage protocol. Direct execution model set to: ${modelToUse}`);
    decision = {
      target_tier: 'DIRECT_OVERRIDE',
      complexity: 'strategic',
      sanitized_directive: userInput,
      requires_clarification: false
    };
  } else {
    logger.info(`Routing request via Triage Model...`);
    logger.debug(`Running Triage via ${DEFAULT_MODEL}...`);
    
    const triageSystemInstruction = `
      # TRIAGE PROTOCOL
      You are a structural parser and router. You do not write bash scripts. You do not solve the user's problem. 

      Your only allowed output is a raw JSON block matching this schema:
      {
        "complexity": "trivial" | "strategic" | "architectural",
        "target_tier": "TIER1_LITE" | "TIER2_FLASH" | "TIER3_HEAVY" | "CONVERSATIONAL",
        "sanitized_directive": "A dense string framing the instructions for the execution tier, completely stripped of raw file text.",
        "direct_response": "If the user is just saying hello, asking a simple question that doesn't require tools, or making small talk, provide the final response here and set target_tier to CONVERSATIONAL.",
        "requires_clarification": true | false,
        "clarification_message": "Message explaining the ambiguity and asking the user to choose (only set if requires_clarification is true).",
        "clarification_options": ["Option 1 text", "Option 2 text", ...] // optional array of specific options for the user to choose from (only set if requires_clarification is true).
      }

      CRITICAL: 
      - If a task has architectural, scale, budget or setup ambiguity (e.g. choice between simple standalone canvas vs Vite build scaffolding, or other architectural options), you MUST set "requires_clarification" to true, provide a clear "clarification_message" explaining the ambiguity, and provide options in "clarification_options".
      - Do NOT trigger clarification for straightforward document creation/modification tasks (such as creating AG_CONTEXT.md, rulebook updates, or simple code changes) unless there is a genuine technological stack/framework ambiguity.
      - Inspect the Active Project Root Directory Listing in the prompt to understand the project structure; do not guess or hallucinate project details.

      If a task requires deep contextual understanding of a workspace or complex planning, you MUST assign it to TIER3_HEAVY and set the sanitized_directive to explain the problem to the underlying agent. Do not attempt to guess commands here.
      
      - For simple, non-destructive exploratory requests (e.g. "describe the files in this dir", "what is this project", "list the files"), you MUST assign it to TIER1_LITE and set complexity to "trivial". Only use TIER3_HEAVY for complex, multi-step actions or deep architectural debugging.
    `;

    const triagePrompt = `
      Conversation History:
      ${historyText}

      User Prompt: "${userInput}"
      Attached File Metadata:
      ${metadataText}
      
      State Ledger Context:
      ${JSON.stringify(state, null, 2)}
      
      Rulebook Constraints:
      ${rulebook}

      Active Project Root Path:
      "${activeProjectRoot}"

      Active Project Root Directory Listing:
      ${directoryStructure || 'Empty or unable to read'}

      Project Context (AG_CONTEXT.md):
      ${agContext || 'None'}

      Project Features (FEATURES.md):
      ${features || 'None'}

      Recent Agent Logs (Context & Past Decisions):
      ${recentLogs || 'None'}
    `;

    try {
      const { text: rawResponse } = await callGemini(DEFAULT_MODEL, triageSystemInstruction, triagePrompt, true);
      let jsonStr = rawResponse;
      const jsonStart = rawResponse.indexOf('{');
      const jsonEnd = rawResponse.lastIndexOf('}');
      if (jsonStart !== -1 && jsonEnd !== -1) {
        jsonStr = rawResponse.substring(jsonStart, jsonEnd + 1);
      }
      decision = JSON.parse(jsonStr);
      logger.info(`Routed to [${decision.target_tier}] (${decision.complexity})`);
      logger.debug(`Triage Decision: Routing to [${decision.target_tier}]`);
      logger.debug(`Complexity: ${decision.complexity}`);
      logger.debug(`Sanitized Directive: ${decision.sanitized_directive}`);
    } catch (err) {
      logger.warn(`Triage executive failed. Falling back to default TIER1_LITE. Error: ${err.message}`);
      decision = { target_tier: 'TIER1_LITE', complexity: 'trivial', sanitized_directive: userInput };
    }
  }

  // Handle Dynamic Clarification State
  let budgetMode = 'ARCHITECTURAL';
  if (decision.requires_clarification) {
    const message = decision.clarification_message || 'Ambiguity detected in your request.';
    const options = decision.clarification_options && decision.clarification_options.length > 0
      ? decision.clarification_options
      : [
          'Lean Path (Fast, ultra-cheap tokens, zero setup)',
          'Architectural Path (Structured framework, relies on deep quota execution)'
        ];

    let choice;
    console.log(`\n❓ ${colors.bold}${colors.lightYellow}[CLARIFICATION REQUIRED]:${colors.reset}`);
    console.log(message);
    console.log();
    options.forEach((opt, idx) => {
      console.log(`[${idx + 1}] ${opt}`);
    });
    console.log();

    choice = await new Promise((resolve) => {
      const ask = async () => {
        const answer = await askQuestion(`Select option (1-${options.length}): `, rlInterface);
        const num = parseInt(answer.trim(), 10);
        if (num >= 1 && num <= options.length) {
          resolve(num);
        } else {
          console.log(`Invalid choice. Please select a number between 1 and ${options.length}.`);
          ask();
        }
      };
      ask();
    });

    const selectedOption = options[choice - 1];
    logger.info(`Selected: ${selectedOption}`);
    
    if (selectedOption.toLowerCase().includes('lean')) {
      budgetMode = 'LEAN';
    } else {
      budgetMode = 'ARCHITECTURAL';
    }

    // Inject selection directly into the sanitized directive for the execution layer
    decision.sanitized_directive = `[BUDGET_MODE: ${budgetMode}] ${decision.sanitized_directive} (User selection: "${selectedOption}")`;
  }

  // Record spend for triage
  governor.recordSpend('tier2_flash', 1500, 500);
  const triageSpend = calculateCost('gemini-2.5-flash', 1500, 500);
  currentQueryCost += triageSpend;
  threadCost += triageSpend;

  // Execute Route
  if (decision.target_tier === 'CONVERSATIONAL') {
    const responseText = decision.direct_response || "Hello! How can I help you today?";
    chatHistory.push({ role: 'user', parts: [{ text: userInput }] });
    chatHistory.push({ role: 'model', parts: [{ text: responseText }] });
    logger.showResponse(responseText, 'TRIAGE_DIRECT');
  } else if (decision.target_tier === 'TIER3_HEAVY') {
    logger.info(`Executing request in warm background PTY session...`);
    
    if (!ptySession.isReady) {
      await ptySession.start();
    }

    // Check agy CLI health
    let agyWorking = false;
    const agyHealth = checkAgyHealth();
    if (!agyHealth.healthy) {
      logger.warn(`[WARN] ${agyHealth.reason} Bypassing agy CLI and dropping to Direct API Fallback...`);
    } else {
      agyWorking = true;
      logger.info("agy CLI is healthy and available based on settings.");
    }

    const goal = userInput;
    let completed = false;
    let iteration = 0;
    const maxIterations = budgetMode === 'LEAN' ? 1 : 10;
    executionHistory = [];
    let lastPtyResult = "";

    const orchestratorSystemInstruction = `
      # AI-OS GATEWAY HIGH-LEVEL ORCHESTRATOR
      [BUDGET_MODE: ${budgetMode}]
      You are the high-level orchestrator and monitor for the AI-OS Gateway.
      Your job is to analyze the user's overall goal, the steps executed so far, the terminal outputs from the underlying agent (agy), and decide if the goal has been successfully accomplished.
      
      You must output a raw JSON block matching this schema:
      {
        "completed": true | false,
        "next_instruction": "Specific, actionable instruction for the underlying agent (agy) for the next step, or empty if completed.",
        "reason": "Brief explanation of the current progress, what has been completed, and what is left to do."
      }
      
      CRITICAL: 
      - If the agent has run some commands but has not fully completed the task (e.g. they only did a directory listing, or wrote a partial file, or didn't verify that the code runs/works), you MUST set "completed" to false and provide the "next_instruction" to guide the agent to perform the next action (e.g. editing the files, writing the code, running verification tests, etc.).
      - The underlying agent (agy) runs non-interactively via "--print" or "--continue --print". It performs one set of tool actions per call. You must guide it step-by-step.
      - Do not stop until the task is completely implemented, verified, and confirmed to work. If there are tests, instruct the agent to run them. If there's a game, instruct the agent to verify all files are correctly created and not corrupted.
      - **Directory Consideration:** If the active directory is a generic parent folder (like ~/projects or /Users/matthewmurphy/projects), ensure the agent creates and operates within a dedicated, appropriately-named subfolder instead of writing files directly to the parent folder. However, if the active directory is already a specific project folder (such as a subfolder of ~/projects, e.g. /Users/matthewmurphy/projects/now-music, or contains files like package.json, src/, index.js, etc.), do NOT instruct the agent to create a new subdirectory or project folder. The agent must work directly in the active project directory.
      - **Verification of Bug Fixes & Findings:** When guiding the agent to investigate or resolve a user-reported bug, ensure the agent explicitly runs verification steps (such as tests, launching/running the script, or viewing logs) to confirm the issue is addressed.
      ${budgetMode === 'LEAN' ? `
      CRITICAL LEAN BUDGET CONSTRAINT:
      The budget mode is set to LEAN. You must strictly limit all execution commands and tool executions to single-file configurations and write operations. Do NOT create multi-file Vite or standard framework boilerplate. Complete the entire task in this single loop iteration.` : ''}
    `;

    while (!completed && iteration < maxIterations) {
      iteration++;
      logger.info(`Orchestration Loop: Iteration ${iteration}/${maxIterations}`);

      // Call orchestrator model to check completion status and get next instruction
      const orchestratorPrompt = `
        Active Project Root Path:
        "${activeProjectRoot}"

        Active Project Root Directory Listing:
        ${directoryStructure || 'Empty or unable to read'}

        Project Context (AG_CONTEXT.md):
        ${agContext || 'None'}

        Project Features (FEATURES.md):
        ${features || 'None'}

        Recent Agent Logs (Context & Past Decisions):
        ${recentLogs || 'None'}

        User Overall Goal: "${goal}"
        
        Execution History So Far:
        ${executionHistory.length > 0 ? executionHistory.map((h, i) => `Step ${i + 1}:
Instruction: ${h.instruction}
Result Output:
${h.result}`).join('\n\n') : 'None'}
      `;

      let orchestratorDecision;
      try {
        const { text: rawOrchResponse } = await callGemini(DEFAULT_MODEL, orchestratorSystemInstruction, orchestratorPrompt, true);
        orchestratorDecision = JSON.parse(rawOrchResponse);
        logger.debug(`Orchestrator Decision: ${JSON.stringify(orchestratorDecision, null, 2)}`);
      } catch (err) {
        logger.warn(`Orchestration checker failed. Falling back to default directive. Error: ${err.message}`);
        orchestratorDecision = {
          completed: iteration > 1, // fallback to stop if we already ran once
          next_instruction: iteration === 1 ? decision.sanitized_directive : "",
          reason: "Fallback due to JSON parsing / API error."
        };
      }

      if (orchestratorDecision.completed) {
        logger.info(`Goal successfully completed according to Orchestrator: ${orchestratorDecision.reason}`);
        completed = true;
        break;
      }

      const nextInstruction = orchestratorDecision.next_instruction || decision.sanitized_directive;
      logger.info(`Orchestration Step: ${orchestratorDecision.reason}`);
      logger.info(`Sending instruction to agent: "${nextInstruction}"`);

      let ptyResult = "";
      let useFallback = !agyWorking;

      if (!useFallback) {
        const commandToRun = iteration === 1
          ? `/Users/matthewmurphy/.local/bin/agy --dangerously-skip-permissions --print ${JSON.stringify(nextInstruction)}`
          : `/Users/matthewmurphy/.local/bin/agy --dangerously-skip-permissions --continue --print ${JSON.stringify(nextInstruction)}`;

        logger.debug(`Executing command: ${commandToRun}`);
        
        try {
          // Warm PTY execution of agy with a 5-minute timeout to allow full execution
          const ptyRawResult = await ptySession.executeCommand(commandToRun, 300000);
          if (!ptyRawResult || ptyRawResult.trim() === "" || ptyRawResult.includes("quota") || ptyRawResult.includes("Error") || ptyRawResult.includes("503") || ptyRawResult.includes("UNAVAILABLE") || ptyRawResult.includes("exceeded")) {
            logger.warn(`Agent execution returned empty, error, or quota exceeded. Falling back to Direct API Executor...`);
            useFallback = true;
          } else {
            ptyResult = cleanPtyOutput(ptyRawResult, commandToRun);
          }
        } catch (execErr) {
          if (execErr.message === "AGY_QUOTA_DEPLETED") {
            logger.warn("[ALERT] Quota ceiling detected live in PTY stream. Activating Direct API Fallback Subagent...");
          } else {
            logger.warn(`Agent execution failed or timed out: ${execErr.message}. Falling back to Direct API Executor...`);
          }
          useFallback = true;
        }
      }

      if (useFallback) {
        ptyResult = await executeInstructionDirectly(nextInstruction, sandbox, logger, state, activeProjectRoot, budgetMode, { agContext, features, recentLogs, directoryStructure });
      }
      
      lastPtyResult = ptyResult;

      executionHistory.push({
        instruction: nextInstruction,
        result: ptyResult
      });

      // Update state ledger with latest status
      state.latest_milestone = `Completed step ${iteration}: ${nextInstruction.substring(0, 50)}...`;
      fs.writeFileSync(path.join(PROJECT_ROOT, 'state_ledger.json'), JSON.stringify(state, null, 2), 'utf8');

      // Record spend for the agy run (estimated model call within agy)
      governor.recordSpend('tier3_heavy', 5000, 2000);
      const agySpend = calculateCost('gemini-2.5-pro', 5000, 2000);
      currentQueryCost += agySpend;
      threadCost += agySpend;
    }

    if (iteration >= maxIterations && !completed) {
      logger.warn(`Orchestrator reached maximum iteration limit (${maxIterations}) without completion.`);
    }

    // Synthesize final response explaining what was done and confirming completion
    logger.info(`Synthesizing execution response...`);
    const explainSystemInstruction = `
      You are the friendly executive responder for the AI-OS Gateway.
      Analyze the overall goal and the full execution history of steps taken.
      Summarize what actions were taken to accomplish the goal, highlight any tests or verifications performed, and state clearly if the goal succeeded.
      
      CRITICAL: If the user's request was to retrieve information (like a file list, file content, or command output), you MUST include that specific information in your response. Do not just say you found it; show it.
      
      Keep the tone helpful, professional, and very concise.
      
      CRITICAL BUG REPORTING DIRECTIVE:
      If the user requested an investigation or fix for a bug:
      - You must explicitly articulate findings from the code review/execution logs (i.e. whether a bug was found, what it was, or if no bug was detected).
      - If no code-level bug matching the description could be found, explicitly state this, provide a rationale, and suggest alternative hypotheses (e.g., browser-specific behaviors, environmental factors, user input details) or request clarification. Never leave a bug investigation unaddressed or without clear findings.
      
      CRITICAL COMPLETION MARKER:
      You MUST output the exact string [END_OF_RESPONSE] at the very end of your message. This acts as an EOF marker for the pipeline. Do not forget this.
    `;
    const explainPrompt = `
      Conversation History:
      ${historyText}

      User Request: "${userInput}"
      Execution History:
      ${executionHistory.map((h, i) => `Step ${i + 1}:
Instruction: ${h.instruction}
Result:
${h.result}`).join('\n\n')}
    `;
    
    let responseText;
    try {
      const { text: rawResponseText } = await callGemini(DEFAULT_MODEL, explainSystemInstruction, explainPrompt);
      responseText = rawResponseText.replace('[END_OF_RESPONSE]', '').trim();
    } catch (err) {
      logger.warn(`Failed to synthesize response. Falling back to last terminal output. Error: ${err.message}`);
      responseText = lastPtyResult || 'Command executed successfully.';
    }
    
    // Record spend for explanation call
    governor.recordSpend('tier1_flash_lite', 800, 200);
    const explainSpend = calculateCost('gemini-2.5-flash-lite', 800, 200);
    currentQueryCost += explainSpend;
    threadCost += explainSpend;
    
    chatHistory.push({ role: 'user', parts: [{ text: userInput }] });
    chatHistory.push({ role: 'model', parts: [{ text: responseText }] });

    logger.showResponse(responseText, 'TIER3_HEAVY');
  } else {
    logger.info(`Executing request via Gemini Direct API...`);
    logger.debug(`Dispatching task to Gemini direct API node [${modelToUse || DEFAULT_MODEL}]...`);
    
    resultText = await executeInstructionDirectly(decision.sanitized_directive || userInput, sandbox, logger, state, activeProjectRoot, budgetMode, { agContext, features, recentLogs }, modelToUse);
    
    // Synthesize final response explaining what was done and confirming completion
    logger.info(`Synthesizing execution response...`);
    const explainSystemInstruction = `
      You are the friendly executive responder for the AI-OS Gateway.
      Analyze the overall goal and the full execution history of steps taken.
      Summarize what actions were taken to accomplish the goal, highlight any tests or verifications performed, and state clearly if the goal succeeded.
      
      CRITICAL: If the user's request was to retrieve information (like a file list, file content, or command output), you MUST include that specific information in your response. Do not just say you found it; show it.
      
      Keep the tone helpful, professional, and very concise.
      
      CRITICAL BUG REPORTING DIRECTIVE:
      If the user requested an investigation or fix for a bug:
      - You must explicitly articulate findings from the code review/execution logs (i.e. whether a bug was found, what it was, or if no bug was detected).
      - If no code-level bug matching the description could be found, explicitly state this, provide a rationale, and suggest alternative hypotheses (e.g., browser-specific behaviors, environmental factors, user input details) or request clarification. Never leave a bug investigation unaddressed or without clear findings.
      
      CRITICAL COMPLETION MARKER:
      You MUST output the exact string [END_OF_RESPONSE] at the very end of your message. This acts as an EOF marker for the pipeline. Do not forget this.
    `;
    const explainPrompt = `
      Conversation History:
      ${historyText}

      User Request: "${userInput}"
      Execution History:
      ${resultText}
    `;
    
    let responseText;
    try {
      const { text: rawResponseText } = await callGemini(modelToUse || DEFAULT_MODEL, explainSystemInstruction, explainPrompt);
      responseText = rawResponseText.replace('[END_OF_RESPONSE]', '').trim();
    } catch (err) {
      logger.warn(`Failed to synthesize response. Falling back to last execution output. Error: ${err.message}`);
      responseText = resultText || 'Command executed successfully.';
    }
    
    state.latest_milestone = `Processed: ${userInput}`;
    governor.recordSpend('tier1_flash_lite', 1000, 400);
    const directExplainSpend = calculateCost('gemini-2.5-flash-lite', 1000, 400);
    currentQueryCost += directExplainSpend;
    threadCost += directExplainSpend;
    
    chatHistory.push({ role: 'user', parts: [{ text: userInput }] });
    chatHistory.push({ role: 'model', parts: [{ text: responseText }] });
    
    logger.showResponse(responseText, decision.target_tier);
  }

  // Save the updated state ledger back to disk
  fs.writeFileSync(path.join(PROJECT_ROOT, 'state_ledger.json'), JSON.stringify(state, null, 2), 'utf8');

  // 5. Version Control Staging
  autoCommit(`Gateway Auto-Commit: Executed request '${userInput.substring(0, 30)}...'`);

  // Log token metrics
  console.log(`\n${colors.bold}${colors.gray}[Token Metrics]${colors.reset} Query: ${colors.bold}${formatTokens(currentQueryTotalTokens)}${colors.reset} tokens (Prompt: ${formatTokens(currentQueryPromptTokens)}, Completion: ${formatTokens(currentQueryCandidatesTokens)}) | Cost: ${colors.bold}$${currentQueryCost.toFixed(4)}${colors.reset} | Thread: ${colors.bold}${formatTokens(threadTotalTokens)}${colors.reset} tokens (Prompt: ${formatTokens(threadPromptTokens)}, Completion: ${formatTokens(threadCandidatesTokens)}) | Cost: ${colors.bold}$${threadCost.toFixed(4)}${colors.reset}\n`);

  // --- SELF-REFLECTION & ANALYSIS LOOP ---
  const sessionSummary = {
    userInput,
    targetTier: decision ? decision.target_tier : 'UNKNOWN',
    complexity: decision ? decision.complexity : 'UNKNOWN',
    tokenUsage: {
      prompt: currentQueryPromptTokens,
      candidates: currentQueryCandidatesTokens,
      total: currentQueryTotalTokens,
      cost: currentQueryCost
    },
    steps: decision && decision.target_tier === 'TIER3_HEAVY' ? executionHistory : [{
      instruction: (decision && decision.sanitized_directive) || userInput,
      result: resultText
    }]
  };

  const selfReflectionSystemInstruction = `
    # GATEWAY SELF-REFLECTION AUDIT
    You are the diagnostic auditor of the AI-OS Gateway.
    Your task is to analyze the execution history (steps, commands, inputs, and results) of the session and generate a micro-diagnostic report identifying optimization suggestions.

    Analyze the session using these three explicit criteria:
    1. **Tool Waste:** Did any model attempt an invalid command, repetitive operation, or run a blocked server like python3 -m http.server that timed out or failed?
    2. **Context Bleed:** Did a massive string input or file read cause an unexpected token spike?
    3. **Implicit Preferences:** Did the user mention a habit or environmental preference (e.g., "Projects belong in ~/projects", "always use pnpm")? 
       *CRITICAL:* Before suggesting a rule, you MUST verify it is not already present in the provided Rulebook or AG_CONTEXT. If the information was already known to the system, it is NOT a new preference. Do not suggest redundant rules, rules that contradict existing context, or rules for one-off actions that don't represent a recurring pattern.

    STRICT QUALITY FILTER:
    - If the suggestion is trivial, redundant with existing rules, or based on a single non-habitual command, set "has_suggestions" to false.
    - Only propose a rule if you are >90% certain it improves long-term efficiency and is not already documented.

    You MUST output a raw JSON block matching this schema:
    {
      "has_suggestions": true,
      "suggestions": [
        {
          "type": "Bug Report" | "Candidate Rule" | "Path Declaration",
          "description": "Details of the issue or pattern found.",
          "recommendation": "Suggested action or candidate rule/path text."
        }
      ],
      "proposed_rulebook_rule": "A single clean string representing the rule to append to rulebook.md if it is a high-level constraint (e.g., '- All new projects must default to folders under /Users/matthewmurphy/projects/'), or null if not applicable.",
      "proposed_context_path": "A path to declare under '## Environment & Paths' in AG_CONTEXT.md (e.g., '- Project X: /Users/matthewmurphy/...'), or null if not applicable."
    }

    Do NOT wrap the JSON block in markdown formatting or any other text. Output ONLY the raw valid JSON.
    If there are no suggestions, return: {"has_suggestions": false, "suggestions": []}
  `;

  logger.info("Initiating system self-reflection & analysis...");
  const auditPrompt = `
    Session Execution Summary:
    ${JSON.stringify(sessionSummary, null, 2)}
    
    Current Rulebook:
    ${rulebook}
    
    Current State Ledger:
    ${JSON.stringify(state, null, 2)}
  `;

  let auditResult = { has_suggestions: false };
  try {
    const { text: rawAuditResponse } = await callGemini(DEFAULT_MODEL, selfReflectionSystemInstruction, auditPrompt, true);
    let jsonStr = rawAuditResponse;
    const jsonStart = rawAuditResponse.indexOf('{');
    const jsonEnd = rawAuditResponse.lastIndexOf('}');
    if (jsonStart !== -1 && jsonEnd !== -1) {
      jsonStr = rawAuditResponse.substring(jsonStart, jsonEnd + 1);
    }
    auditResult = JSON.parse(jsonStr);
  } catch (err) {
    logger.warn(`Self-reflection audit failed: ${err.message}`);
  }

  if (auditResult.has_suggestions && auditResult.suggestions && auditResult.suggestions.length > 0) {
    console.log(`\n${colors.bold}${colors.lightBlue}━━  SYSTEM SELF-REFLECTION & ANALYSIS  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`);
    console.log(`${colors.bold}💡 Optimization Suggestions:${colors.reset}`);
    auditResult.suggestions.forEach((s, idx) => {
      const saved = appendSuggestion({
        type: s.type,
        description: s.description,
        recommendation: s.recommendation,
        proposed_rulebook_rule: auditResult.proposed_rulebook_rule,
        proposed_context_path: auditResult.proposed_context_path,
        project_root: activeProjectRoot,
        query: userInput
      });
      console.log(`${idx + 1}. [${s.type}] (ID: ${saved.id}): ${s.description}`);
      console.log(`   Recommendation: ${s.recommendation}`);
    });

    const ruleToAppend = auditResult.proposed_rulebook_rule;
    const pathDeclaration = auditResult.proposed_context_path;

    if (ruleToAppend || pathDeclaration) {
      let answer;
      console.log(`\nWould you like to append this to your living rulebook / context?`);
      if (ruleToAppend) {
        console.log(`-> Rulebook: "${ruleToAppend}"`);
      }
      if (pathDeclaration) {
        console.log(`-> Context: "${pathDeclaration}"`);
      }

      const ans = await new Promise(async (resolve) => {
        const ansVal = await askQuestion(`\nPress [A] to Accept and append, or [I] to Ignore: `, rlInterface);
        resolve(ansVal);
      });
      answer = ans.trim().toLowerCase();

      if (answer === 'a') {
        if (ruleToAppend) {
          modifyRulebook(ruleToAppend);
        }
        if (pathDeclaration) {
          modifyContext(pathDeclaration);
        }
      } else {
        logger.info("Suggestions ignored.");
      }
    }
    console.log(`${colors.bold}${colors.lightBlue}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);
  }

  if (activeResolveId !== null) {
    markSuggestionResolved(activeResolveId);
    logger.info(`Suggestion ID ${activeResolveId} marked as resolved.`);
    activeResolveId = null;
  }

  logger.info(`Gateway run complete.`);
  } catch (err) {
    if (err.name === 'AbortError' || err.message === 'EXECUTION_CANCELLED') {
      logger.warn(`\nExecution cancelled by user.`);
      console.log(`\nLast sent message: "${lastSentMessage}"\n`);
    } else {
      logger.error(`Error during execution: ${err.message}`);
    }
  } finally {
    isExecuting = false;
    activeAbortController = null;
    saveThreadHistory();
    updateTuiStats('Idle');
  }
}

// Interactive REPL loop
function startRepl() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: `${colors.bold}${colors.cyan}ai-os>${colors.reset} `
  });

  rl.prompt();

  rl.on('line', async (line) => {
    const trimmed = line.trim();
    if (trimmed === 'exit' || trimmed === 'quit') {
      rl.close();
      return;
    }

    if (trimmed.startsWith('/clear')) {
      chatHistory.length = 0;
      threadPromptTokens = 0;
      threadCandidatesTokens = 0;
      threadTotalTokens = 0;
      threadCost = 0.0;
      console.log(`${colors.bold}${colors.cyan}Thread history and token usage metrics cleared.${colors.reset}`);
      rl.prompt();
      return;
    }

    if (trimmed.startsWith('/suggestions')) {
      const parts = trimmed.split(/\s+/);
      if (parts.length === 1) {
        handleSuggestionsCommand();
      } else if (parts[1].toLowerCase() === 'resolve') {
        const id = parseInt(parts[2], 10);
        if (isNaN(id)) {
          logger.error("Please specify a valid suggestion ID to resolve, e.g. /suggestions resolve 1");
        } else {
          const suggestions = loadGlobalSuggestions();
          const suggestion = suggestions.find(s => s.id === id);
          if (!suggestion) {
            logger.error(`Suggestion ID ${id} not found.`);
          } else {
            activeResolveId = id;
            logger.info(`Resolving Suggestion ${id}...`);
            logger.info(`Switching workspace target to: ${suggestion.project_root}`);
            
            const { state: activeState } = readContext();
            activeState.project_target_root = suggestion.project_root;
            fs.writeFileSync(path.join(PROJECT_ROOT, 'state_ledger.json'), JSON.stringify(activeState, null, 2), 'utf8');
            sandbox = new DeterministicSandbox(suggestion.project_root);
            
            const queryPrompt = `Resolve the following suggestion:\nRecommendation: "${suggestion.recommendation}"\nOriginal Context/Query: "${suggestion.query}"`;
            
            await processGatewayRequest(queryPrompt, null, rl);
          }
        }
      }
      rl.prompt();
      return;
    }

    if (trimmed.startsWith('/settings')) {
      const { state } = readContext();
      const parts = trimmed.split(/\s+/);
      if (parts.length === 1) {
        console.log(`\n${colors.bold}${colors.blue}━━ CURRENT SETTINGS ━━${colors.reset}`);
        console.log(`  ${colors.bold}Mode:${colors.reset} ${logger.mode}`);
        console.log(`  ${colors.bold}Model:${colors.reset} ${process.env.GEMINI_MODEL || DEFAULT_MODEL}`);
        console.log(`  ${colors.bold}Target Root:${colors.reset} ${state.project_target_root || PROJECT_ROOT}`);
        console.log(`\nTo modify, use: /settings [mode|model|root] [value]\n`);
      } else {
        const key = parts[1].toLowerCase();
        const value = parts.slice(2).join(' ').trim();
        if (key === 'mode') {
          if (value === 'user' || value === 'debug') {
            logger.mode = value;
            logger.info(`Mode set to: ${value}`);
          } else {
            logger.error(`Invalid mode. Choose 'user' or 'debug'.`);
          }
        } else if (key === 'model') {
          if (value) {
            process.env.GEMINI_MODEL = value;
            cliModel = value;
            logger.info(`Model set to: ${value} (Triage bypassed)`);
          } else {
            logger.error(`Please specify a model name.`);
          }
        } else if (key === 'root' || key === 'project') {
          if (fs.existsSync(value) && fs.statSync(value).isDirectory()) {
            state.project_target_root = value;
            fs.writeFileSync(path.join(PROJECT_ROOT, 'state_ledger.json'), JSON.stringify(state, null, 2), 'utf8');
            sandbox = new DeterministicSandbox(value);
            logger.info(`Target root updated to: ${value}`);
          } else {
            logger.error(`Directory does not exist: ${value}`);
          }
        }
      }
      rl.prompt();
      return;
    }

    if (trimmed) {
      await processGatewayRequest(trimmed, null, rl);
    }
    rl.prompt();
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

(async () => {
  try {
    await loadPricing();

    if (listSuggestions) {
      handleSuggestionsCommand();
      process.exit(0);
    }

    if (resolveSuggestionId !== null) {
      const suggestions = loadGlobalSuggestions();
      const suggestion = suggestions.find(s => s.id === resolveSuggestionId);
      if (!suggestion) {
        logger.error(`Suggestion ID ${resolveSuggestionId} not found.`);
        process.exit(1);
      }
      if (suggestion.status !== 'pending') {
        logger.warn(`Suggestion ID ${resolveSuggestionId} is already ${suggestion.status}.`);
      }

      activeResolveId = resolveSuggestionId;
      logger.info(`Resolving Suggestion ${resolveSuggestionId}...`);
      logger.info(`Switching workspace target to: ${suggestion.project_root}`);

      // Update state project root to match suggestion
      const stateLedgerPath = path.join(PROJECT_ROOT, 'state_ledger.json');
      let state = {};
      if (fs.existsSync(stateLedgerPath)) {
        state = JSON.parse(fs.readFileSync(stateLedgerPath, 'utf8'));
      }
      state.project_target_root = suggestion.project_root;
      fs.writeFileSync(stateLedgerPath, JSON.stringify(state, null, 2), 'utf8');

      const queryPrompt = `Resolve the following suggestion:
Recommendation: "${suggestion.recommendation}"
Original Context/Query: "${suggestion.query}"`;

      await processGatewayRequest(queryPrompt, null);
      ptySession.close();
      process.exit(0);
    }

    if (query || isInteractive) {
      if (isInteractive) {
        logger.info('Entering interactive mode. Type "exit" or "quit" to exit.');
        startRepl();
      } else {
        await processGatewayRequest(query, filePath);
        ptySession.close();
        process.exit(0);
      }
    } else {
      // Default to interactive mode if no CLI arguments are supplied
      logger.info('Entering interactive mode. Type "exit" or "quit" to exit.');
      startRepl();
    }
  } catch (e) {
    logger.error(`Gateway Error: ${e.message}`, e);
    ptySession.close();
    process.exit(1);
  }
})();
