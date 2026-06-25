import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import os from 'os';

/**
 * Deterministic Sandbox
 * Hardware firewall for file system operations.
 */
export class DeterministicSandbox {
  constructor(projectRoot) {
    this.projectRoot = path.resolve(projectRoot);
    // Files that trigger Human-In-The-Loop confirmation before write
    this.protectedFiles = ['rulebook.md', 'state_ledger.json', 'package.json', 'AG_CONTEXT.md'];
  }

  /**
   * Validates if a path strictly belongs within the designated project root.
   */
  isPathAllowed(targetPath) {
    const absolute = path.resolve(targetPath);
    return absolute.startsWith(this.projectRoot) || 
           absolute.startsWith('/Users/matthewmurphy/projects/') || 
           absolute.startsWith('/Users/matthewmurphy/School/') || 
           absolute.startsWith('/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal');
  }

  /**
   * Intercepts standard deletions and routes files to ~/.Trash/
   */
  deleteFile(targetPath) {
    const absolute = path.resolve(targetPath);
    
    if (!this.isPathAllowed(absolute)) {
      throw new Error(`Sandbox Violation: Attempted to delete outside root: ${absolute}`);
    }
    
    if (!fs.existsSync(absolute)) {
      return false; // Nothing to delete
    }
    
    // Route to macOS Trash with a timestamp to prevent overwrite collisions in Trash
    const trashDir = path.join(os.homedir(), '.Trash');
    const baseName = path.basename(absolute);
    const dest = path.join(trashDir, `${Date.now()}_${baseName}`);
    
    try {
      execSync(`mv "${absolute}" "${dest}"`);
      return true;
    } catch (e) {
      throw new Error(`Sandbox Error: Failed to safe-delete to Trash: ${e.message}`);
    }
  }

  /**
   * Guarded write operation that checks path boundaries and protected file intercepts.
   */
  writeFile(targetPath, content, userHasApproved = false) {
    const absolute = path.resolve(targetPath);
    
    if (!this.isPathAllowed(absolute)) {
      throw new Error(`Sandbox Violation: Attempted to write outside root: ${absolute}`);
    }

    const baseName = path.basename(absolute);
    
    // Human-In-The-Loop Hook intercept
    if (this.protectedFiles.includes(baseName) && !userHasApproved) {
      // In a live system, the Orchestrator catches this specific Error type 
      // and blocks execution until the user manually types 'Y' in the CLI.
      const err = new Error(`HUMAN_APPROVAL_REQUIRED: Modification to protected file '${baseName}' blocked.`);
      err.code = 'HUMAN_APPROVAL_REQUIRED';
      err.targetFile = baseName;
      throw err;
    }

    // Safely ensure directory structure exists before writing
    const dir = path.dirname(absolute);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(absolute, content, 'utf8');
    return true;
  }
}
