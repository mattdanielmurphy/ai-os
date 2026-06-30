# Debugging Output.md Preview Pane Issues

I have added debug logging and documented this as a potential ongoing issue in the workspace.

## 🛠️ Changes Implemented

### 1. Added Debug Logging in Polling Loop
In [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts#L358-L361), the polling interval's `catch` block has been updated to log the exact error and path when checking or reading `.ai-os/output.md` fails:
```typescript
} catch (e) {
    // Log details to console for debugging
    console.error(`[AI-OS Preview Pane] Error checking/reading ${outputPath}:`, e);
}
```
This will allow you to see the exact root cause (e.g. Tauri FS API scope security restrictions, path mismatches, etc.) in the developer console.

### 2. Documented Ongoing Issue
Added **Issue 2: output.md Not Opening in Preview Pane** to [memory/agent-quirks-and-workarounds.md](file:///Users/matthewmurphy/projects/ai-os/memory/agent-quirks-and-workarounds.md) to log it as a potential ongoing problem, tracking the current mitigations and planned future work (evaluating `tauri.conf.json` filesystem scopes).

---

## 🔍 How to Inspect the Debug Output
1. Open the AI-OS application developer tools (Web Inspector).
2. Check the console logs for entries matching:
   `[AI-OS Preview Pane] Error checking/reading ...`
3. These logs will reveal why Tauri is failing to read the `.ai-os/output.md` file.
