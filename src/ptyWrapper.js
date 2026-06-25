import { spawn } from 'child_process';
import os from 'os';

/**
 * Background PTY Wrapper (Subscription Exploitation Engine)
 * Maintains a "warm" interactive CLI session (e.g., 'agy') running in the background.
 * Bypasses per-token billing by leveraging consumer flat-rate subscriptions,
 * injecting commands directly into the active stdin.
 */
export function cleanPtyOutput(output, command) {
  let lines = output.replace(/\r\n/g, '\n').split('\n');
  
  // Clean up empty lines at start
  while (lines.length > 0 && lines[0].trim() === '') {
    lines.shift();
  }
  
  // Remove command echo line at the very beginning
  if (lines.length > 0 && (lines[0].includes(command) || command.includes(lines[0]))) {
    lines.shift();
  }
  
  // Clean up empty lines again
  while (lines.length > 0 && lines[0].trim() === '') {
    lines.shift();
  }

  // Remove prompt at the end
  if (lines.length > 0) {
    const lastLine = lines[lines.length - 1];
    if (lastLine.includes('Ready for input') || lastLine.includes('❯')) {
      lines.pop();
    }
  }

  // Clean up trailing empty lines
  while (lines.length > 0 && lines[lines.length - 1].trim() === '') {
    lines.pop();
  }
  
  return lines.join('\n').trim();
}

/**
 * Background PTY Wrapper (Subscription Exploitation Engine)
 * Maintains a "warm" interactive CLI session (e.g., 'agy') running in the background.
 * Bypasses per-token billing by leveraging consumer flat-rate subscriptions,
 * injecting commands directly into the active stdin.
 */
export class WarmPtySession {
  constructor(cliCommand = 'export PS1="Ready for input> " && bash --norc --noprofile -i', logger = console) {
    this.cliCommand = cliCommand;
    this.logger = logger;
    this.ptyProcess = null;
    this.outputBuffer = '';
    this.isReady = false;
    // Resolvers for asynchronous command execution
    this.currentTaskResolver = null;
    this.currentTaskRejecter = null;
    
    // Config for node-pty
    this.shell = process.env.SHELL || 'zsh';
  }

  /**
   * Spawns the background pseudo-terminal.
   * @returns {Promise<void>} Resolves when the PTY is warm and ready for input.
   */
  start() {
    this.logger.debug(`Spawning warm background session for: ${this.cliCommand}`);
    // Use python pty module to provide a true pseudo-terminal natively without crashing posix_spawnp or failing on macOS
    const pyCode = `import sys, pty; pty.spawn(["${this.shell}", "-c", """${this.cliCommand}"""])`;
    this.ptyProcess = spawn('python3', ['-c', pyCode], {
      cwd: process.cwd(),
      env: process.env,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    return new Promise((resolve, reject) => {
      let resolved = false;
      const timeout = setTimeout(() => {
        if (!resolved) {
          resolved = true;
          this.close();
          reject(new Error(`[PTY] Session start timed out after 5000ms waiting for prompt.`));
        }
      }, 5000);

      const handleData = (data) => {
        this.outputBuffer += data;
        
        // Intercept standard Antigravity depletion strings live in stdout stream
        if (/RESOURCE_EXHAUSTED|Quota Limit reached|Baseline model quota reached/i.test(data)) {
          this.logger.warn("\n[ALERT] Quota ceiling detected live in PTY stream.");
          this.close();
          if (this.currentTaskRejecter) {
            this.currentTaskRejecter(new Error("AGY_QUOTA_DEPLETED"));
            this.currentTaskResolver = null;
            this.currentTaskRejecter = null;
          }
          return;
        }

        if (data.includes('❯') || data.includes('Ready for input')) {
          this.isReady = true;
          if (!resolved) {
            resolved = true;
            clearTimeout(timeout);
            this.outputBuffer = ''; // Flush startup output
            resolve();
          } else if (this.currentTaskResolver) {
            const result = this.outputBuffer;
            this.outputBuffer = ''; // flush
            this.currentTaskResolver(result);
            this.currentTaskResolver = null;
            this.currentTaskRejecter = null;
          }
        }
      };

      this.ptyProcess.stdout.on('data', handleData);
      this.ptyProcess.stderr.on('data', handleData);

      this.ptyProcess.on('exit', (code, signal) => {
        this.logger.debug(`Background session terminated with code ${code}`);
        this.isReady = false;
      });
    });
  }

  /**
   * Clears the context history of the agent internally to prevent token accumulation.
   */
  async flushContext() {
    this.logger.debug(`Flushing context cache...`);
    return this.executeCommand('/clear');
  }

  /**
   * Sends an instruction directly into the interactive prompt.
   */
  async executeCommand(instruction, timeoutMs = 10000) {
    if (!this.ptyProcess) {
      throw new Error('[PTY] Session is not running. Call start() first.');
    }

    return new Promise((resolve, reject) => {
      let completed = false;
      const timer = setTimeout(() => {
        if (!completed) {
          completed = true;
          this.currentTaskResolver = null;
          this.currentTaskRejecter = null;
          reject(new Error(`[PTY] Command execution timed out after ${timeoutMs}ms: ${instruction}`));
        }
      }, timeoutMs);

      this.currentTaskResolver = (result) => {
        if (!completed) {
          completed = true;
          clearTimeout(timer);
          resolve(result);
        }
      };

      this.currentTaskRejecter = (err) => {
        if (!completed) {
          completed = true;
          clearTimeout(timer);
          reject(err);
        }
      };

      this.isReady = false;
      this.outputBuffer = ''; // Reset buffer for the new instruction
      
      // Inject instruction into stdin followed by return
      this.ptyProcess.stdin.write(`${instruction}\n`);
    });
  }

  /**
   * Cancels the currently executing task, rejects the promise, and kills/restarts the process.
   */
  cancelCurrentTask() {
    if (this.currentTaskRejecter) {
      this.currentTaskRejecter(new Error("EXECUTION_CANCELLED"));
      this.currentTaskResolver = null;
      this.currentTaskRejecter = null;
    }
    this.close();
  }
  
  /**
   * Gracefully close the PTY session.
   */
  close() {
    if (this.ptyProcess) {
      this.ptyProcess.kill();
      this.ptyProcess = null;
    }
  }
}
