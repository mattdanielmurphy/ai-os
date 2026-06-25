/**
 * Helper to validate a command against forbidden list and internal actions
 * @param {string} command - Shell command to validate
 * @returns {{allowed: boolean, reason?: string}}
 */
export function validateCommand(command) {
  if (!command) {
    return { allowed: true };
  }
  
  // Split command by command chaining/separators to check individual commands
  const commands = command.split(/;|&|\||\n/);
  
  for (const cmd of commands) {
    const trimmedCmd = cmd.trim();
    if (!trimmedCmd) continue;
    
    // Split into tokens
    const tokens = trimmedCmd.split(/\s+/);
    const firstToken = tokens[0] ? tokens[0].trim() : '';
    
    // Check for 'rm' command (which is explicitly forbidden in rulebook)
    const hasRm = firstToken === 'rm' || firstToken.endsWith('/rm');
    
    if (hasRm) {
      return {
        allowed: false,
        reason: "Command execution blocked by sandbox. The 'rm' command is strictly prohibited by the rulebook. Use the sandbox file deletion mechanism (mv to ~/.Trash/) instead."
      };
    }
    
    // Check for misuse of internal actions (calling read_file, write_file, list_dir, done, run_command as shell commands)
    const internalActions = ['read_file', 'write_file', 'list_dir', 'done', 'run_command'];
    if (internalActions.includes(firstToken)) {
      return {
        allowed: false,
        reason: `Command execution blocked. You attempted to use the internal action '${firstToken}' as a shell command ('run_command ${trimmedCmd}'). This is invalid syntax. To read, write, or list directories, set the "action" field in your JSON response directly (e.g., {"action": "${firstToken}", "file_path": "..."}).`
      };
    }

    // New validation: Check for reserved action names within the command string
    const reservedActions = ['done', 'read_file', 'write_file', 'list_dir', 'run_command'];
    if (reservedActions.some(action => trimmedCmd.includes(action))) {
      return {
        allowed: false,
        reason: `Command contains reserved API action names - use direct JSON actions instead`
      };
    }
  }
  
  return { allowed: true };
}
