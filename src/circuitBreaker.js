import { spawn } from 'child_process';
import { calculateCost } from './pricing.js';

/**
 * Circuit Breaker: Process Watchdog & Stream Slicer
 * Ensures deterministic protection against infinite loops, runaway build logs,
 * and excessive token consumption.
 */

export const activeProcesses = new Set();

export function killActiveProcesses() {
  for (const child of activeProcesses) {
    try {
      child.kill('SIGKILL');
    } catch (e) {}
  }
  activeProcesses.clear();
}

export class ProcessWatchdog {
  /**
   * Runs a command with a hard timeout and slices the output to a safe buffer limit.
   * @param {string} command - Shell command to execute
   * @param {number} timeoutMs - Maximum execution time in milliseconds
   * @param {number} maxLines - Maximum output lines to capture before truncating
   * @returns {Promise<string>} - The sliced stdout/stderr output
   */
  static runSafeCommand(command, timeoutMs = 15000, maxLines = 50) {
    return new Promise((resolve, reject) => {
      // Spawn using shell to allow standard bash parsing
      const child = spawn(command, { shell: true });
      activeProcesses.add(child);
      
      let outputBuffer = [];
      let lineCount = 0;
      let isTruncated = false;

      const handleData = (data) => {
        if (isTruncated) return;
        
        const lines = data.toString().split('\n');
        for (const line of lines) {
          if (lineCount >= maxLines) {
            isTruncated = true;
            outputBuffer.push(`\n... [SYSTEM]: Output truncated at ${maxLines} lines to preserve token context.`);
            break;
          }
          outputBuffer.push(line);
          lineCount++;
        }
      };

      child.stdout.on('data', handleData);
      child.stderr.on('data', handleData);

      // Setup the hard cutoff watchdog timer
      const timer = setTimeout(() => {
        child.kill('SIGKILL'); // Merciless kill, bypassing SIGTERM traps
        outputBuffer.push(`\n... [WATCHDOG]: Process forcefully killed after ${timeoutMs}ms to prevent infinite loops.`);
        resolve(outputBuffer.join('\n'));
      }, timeoutMs);

      child.on('close', (code) => {
        activeProcesses.delete(child);
        clearTimeout(timer);
        outputBuffer.push(`\n... [PROCESS]: Exited with code ${code}`);
        resolve(outputBuffer.join('\n'));
      });

      child.on('error', (err) => {
        activeProcesses.delete(child);
        clearTimeout(timer);
        reject(err);
      });
    });
  }
}

/**
 * Financial Governor
 * Locally tracks session cost state to enforce hard token boundaries.
 */
export class FinancialGovernor {
  constructor(maxSpendLimitUsd = 1.00, logger = console) {
    this.maxSpendLimitUsd = maxSpendLimitUsd;
    this.currentSessionSpendUsd = 0.0;
    this.logger = logger;
  }

  /**
   * Tracks simulated token cost and halts execution if breached.
   */
  recordSpend(tier, inputTokens, outputTokens) {
    let model = 'gemini-2.5-flash';
    if (tier === 'tier1_flash_lite') model = 'gemini-2.5-flash-lite';
    else if (tier === 'tier2_flash') model = 'gemini-2.5-flash';
    else if (tier === 'tier3_heavy') model = 'gemini-2.5-pro';

    const cost = calculateCost(model, inputTokens, outputTokens);
    this.currentSessionSpendUsd += cost;

    if (this.currentSessionSpendUsd >= this.maxSpendLimitUsd) {
      // Execute a hard shutdown to protect user finances
      this.logger.error(`Financial Governor tripped. Session spend ($${this.currentSessionSpendUsd.toFixed(4)}) exceeded hard limit ($${this.maxSpendLimitUsd.toFixed(2)}).`);
      process.exit(1);
    }
    
    return this.currentSessionSpendUsd;
  }
}
