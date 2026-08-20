import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface AntigravityTokensState {
  pid?: number;
  timestamp?: number;
  workspace_id?: string;
  csrf_token?: string;
  cloud_code_endpoint?: string;
  promptTokens?: number;
  completionTokens?: number;
  triageMode?: string;
  lastPreflightStatus?: string;
  lastUpdated?: number;
}

export function activate(context: vscode.ExtensionContext) {
  // 1. Status Bar Item Creation
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = '$(hubot) Antigravity: Initializing';
  statusBarItem.tooltip = 'Antigravity IDE Live Telemetry';
  statusBarItem.show();

  const stateFilePath = path.join(os.homedir(), '.hermes', 'antigravity_tokens.json');

  const updateUI = () => {
    try {
      if (!fs.existsSync(stateFilePath)) {
        return;
      }
      const raw = fs.readFileSync(stateFilePath, 'utf-8');
      const state: AntigravityTokensState = JSON.parse(raw);

      const promptTokens = (state.promptTokens ?? 0).toLocaleString();
      const completionTokens = (state.completionTokens ?? 0).toLocaleString();
      const triageMode = state.triageMode || 'Orchestrator';
      const workspaceId = state.workspace_id || 'N/A';
      const lastPreflight = state.lastPreflightStatus || 'Ready';
      const endpoint = state.cloud_code_endpoint || 'https://daily-cloudcode-pa.googleapis.com';

      statusBarItem.text = `$(hubot) ${promptTokens} in / ${completionTokens} out | ${triageMode}`;
      statusBarItem.tooltip = `Workspace: ${workspaceId}\nLast Preflight: ${lastPreflight}\nEndpoint: ${endpoint}`;
    } catch (err) {
      // Ignore transient read errors during atomic write operations
    }
  };

  // Initial read
  updateUI();

  // 2. File Watcher with 500ms polling interval
  try {
    fs.watchFile(stateFilePath, { interval: 500 }, () => {
      updateUI();
    });
  } catch (err) {
    console.error('Failed to attach fs.watchFile to antigravity_tokens.json:', err);
  }

  // 4. Disposal
  context.subscriptions.push(
    statusBarItem,
    new vscode.Disposable(() => {
      try {
        fs.unwatchFile(stateFilePath);
      } catch {
        // ignore
      }
    })
  );
}

export function deactivate() {
  const stateFilePath = path.join(os.homedir(), '.hermes', 'antigravity_tokens.json');
  try {
    fs.unwatchFile(stateFilePath);
  } catch {
    // ignore
  }
}
