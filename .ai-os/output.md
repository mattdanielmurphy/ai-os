# Tauri Filesystem Scope Fixed

The issue has been diagnosed and fixed in the configuration.

## 🔍 Root Cause
Tauri's filesystem scope glob patterns (like `$HOME/**`) do not match hidden files or folders starting with a dot (like `.ai-os/`) by default as a security guardrail. Because of this, trying to check or read `.ai-os/output.md` threw a path scope permission exception.

## 🛠️ Resolution
1. **Updated Tauri Configurations**: Added explicit scope permissions for `.ai-os` directories in [src-tauri/tauri.conf.json](file:///Users/matthewmurphy/projects/ai-os/src-tauri/tauri.conf.json#L21-L28):
   ```json
   "scope": [
     "**",
     "$HOME/**",
     "/**",
     "$HOME/**/.ai-os/*",
     "$HOME/**/.ai-os/**/*",
     "$HOME/projects/**/.ai-os/*",
     "$HOME/projects/**/.ai-os/**/*"
   ]
   ```
2. **Updated Workspace Memory**: Catalogued this behavior under Issue 2 in [memory/agent-quirks-and-workarounds.md](file:///Users/matthewmurphy/projects/ai-os/memory/agent-quirks-and-workarounds.md).

> [!IMPORTANT]
> You must **restart your Tauri application / dev process** for the filesystem scope changes in `tauri.conf.json` to take effect.
