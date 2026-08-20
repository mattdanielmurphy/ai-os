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
  // 1. Status Bar Item Creation (Left-aligned, high priority for guaranteed visibility)
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 1000);
  statusBarItem.command = 'antigravity.showTelemetryMenu';
  statusBarItem.text = '$(sparkle) Antigravity: Initializing';
  statusBarItem.tooltip = 'Antigravity IDE Live Telemetry (Click to view details)';
  statusBarItem.show();

  const stateFilePath = path.join(os.homedir(), '.hermes', 'antigravity_tokens.json');

  const updateUI = () => {
    try {
      if (!fs.existsSync(stateFilePath)) {
        statusBarItem.text = '$(sparkle) Antigravity: Ready';
        statusBarItem.tooltip = 'State file ~/.hermes/antigravity_tokens.json not found';
        return;
      }
      const raw = fs.readFileSync(stateFilePath, 'utf-8');
      const state: AntigravityTokensState = JSON.parse(raw);

      const promptTokens = (state.promptTokens ?? 0).toLocaleString();
      const completionTokens = (state.completionTokens ?? 0).toLocaleString();
      const triageMode = state.triageMode || 'Orchestrator';
      const workspaceId = state.workspace_id || 'Global';
      const lastPreflight = state.lastPreflightStatus || 'Ready';
      const endpoint = state.cloud_code_endpoint || 'https://daily-cloudcode-pa.googleapis.com';

      statusBarItem.text = `$(sparkle) ${promptTokens} in / ${completionTokens} out [${triageMode}]`;
      statusBarItem.tooltip = new vscode.MarkdownString(
        `### Antigravity Telemetry\n\n` +
        `- **Prompt Tokens In:** \`${promptTokens}\`\n` +
        `- **Completion Tokens Out:** \`${completionTokens}\`\n` +
        `- **Triage Mode:** \`${triageMode}\`\n` +
        `- **Workspace:** \`${workspaceId}\`\n` +
        `- **Preflight Status:** \`${lastPreflight}\`\n` +
        `- **Endpoint:** \`${endpoint}\`\n\n` +
        `*Click to open telemetry actions*`
      );
    } catch (err) {
      console.error('Antigravity Telemetry UI update error:', err);
    }
  };

  updateUI();

  // Watch state file with 500ms interval polling
  try {
    fs.watchFile(stateFilePath, { interval: 500 }, () => {
      updateUI();
    });
  } catch (err) {
    console.error('Failed to attach fs.watchFile:', err);
  }

  // Register Commands
  const menuCommand = vscode.commands.registerCommand('antigravity.showTelemetryMenu', async () => {
    updateUI();
    let state: AntigravityTokensState = {};
    if (fs.existsSync(stateFilePath)) {
      try {
        state = JSON.parse(fs.readFileSync(stateFilePath, 'utf-8'));
      } catch {}
    }
    const selection = await vscode.window.showQuickPick(
      [
        {
          label: `$(sparkle) Current Mode: ${state.triageMode || 'Orchestrator'}`,
          description: `Tokens: ${state.promptTokens ?? 0} in / ${state.completionTokens ?? 0} out`,
          detail: `Workspace: ${state.workspace_id || 'Global'}`
        },
        {
          label: '$(refresh) Refresh Telemetry',
          description: 'Re-read ~/.hermes/antigravity_tokens.json'
        },
        {
          label: '$(gear) Select Triage Mode',
          description: 'Change active triage routing mode'
        }
      ],
      { placeHolder: 'Antigravity IDE Telemetry & Triage' }
    );

    if (selection?.label.includes('Refresh Telemetry')) {
      updateUI();
      vscode.window.showInformationMessage('Antigravity Telemetry refreshed.');
    } else if (selection?.label.includes('Select Triage Mode')) {
      const modeChoice = await vscode.window.showQuickPick(
        [
          { label: 'Orchestrator', description: 'Standard orchestrator with subagent delegation' },
          { label: 'FastPath', description: 'Lightweight direct execution with minimal tokens' },
          { label: 'ProPlanner', description: 'Deep reasoning planning via ai-os / Perplexity' },
          { label: 'Hermes', description: 'Delegate to Hermes agent architecture' }
        ],
        { placeHolder: 'Select active triage mode' }
      );
      if (modeChoice) {
        state.triageMode = modeChoice.label;
        state.lastUpdated = Date.now() / 1000;
        fs.writeFileSync(stateFilePath, JSON.stringify(state, null, 2), 'utf-8');
        updateUI();
        vscode.window.showInformationMessage(`Triage mode set to: ${modeChoice.label}`);
      }
    }
  });

  const refreshCommand = vscode.commands.registerCommand('antigravity.refreshTelemetry', () => {
    updateUI();
  });

  context.subscriptions.push(
    statusBarItem,
    menuCommand,
    refreshCommand,
    new vscode.Disposable(() => {
      try {
        fs.unwatchFile(stateFilePath);
      } catch {}
    })
  );
}

export function deactivate() {
  const stateFilePath = path.join(os.homedir(), '.hermes', 'antigravity_tokens.json');
  try {
    fs.unwatchFile(stateFilePath);
  } catch {}
}
