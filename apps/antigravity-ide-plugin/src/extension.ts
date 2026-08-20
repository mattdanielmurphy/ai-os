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
  activeConversationId?: string;
}

const STATE_DIR = path.join(os.homedir(), '.gemini', 'antigravity-ide');
const STATE_FILE = path.join(STATE_DIR, 'tokens.json');

function estimateTokens(text: string): number {
  if (!text) return 0;
  return Math.max(1, Math.floor(text.length / 3.5));
}

function calculateConversationTokens(transcriptPath: string): { promptTokens: number; completionTokens: number } {
  let promptTokens = 34500; // Base system prompt + rules + skills baseline
  let completionTokens = 0;

  if (!fs.existsSync(transcriptPath)) {
    return { promptTokens: 0, completionTokens: 0 };
  }

  try {
    const content = fs.readFileSync(transcriptPath, 'utf-8');
    const lines = content.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const step = JSON.parse(trimmed);
        const stype = step.type;
        const body = step.content || '';
        const thinking = step.thinking || '';
        const toolCalls = step.tool_calls || [];

        if (stype === 'USER_INPUT' || stype === 'CONVERSATION_HISTORY' || stype === 'SYSTEM_MESSAGE' || stype === 'CHECKPOINT' || stype === 'KNOWLEDGE_ARTIFACTS') {
          promptTokens += estimateTokens(body);
        } else if (stype === 'PLANNER_RESPONSE') {
          let outText = thinking + (body || '');
          for (const tc of toolCalls) {
            outText += ' ' + (tc.name || '') + ' ' + JSON.stringify(tc.args || {});
          }
          completionTokens += estimateTokens(outText);
        } else {
          // Tool results and errors are fed back as model input
          promptTokens += estimateTokens(body);
        }
      } catch {}
    }
  } catch (err) {
    console.error('Error calculating conversation tokens:', err);
  }

  return { promptTokens, completionTokens };
}

function findLatestConversation(): { convId: string; transcriptPath: string } | null {
  const brainDir = path.join(STATE_DIR, 'brain');
  if (!fs.existsSync(brainDir)) return null;

  try {
    const entries = fs.readdirSync(brainDir, { withFileTypes: true });
    let latestTime = 0;
    let latestConv: { convId: string; transcriptPath: string } | null = null;

    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
      const transcript = path.join(brainDir, entry.name, '.system_generated', 'logs', 'transcript.jsonl');
      if (fs.existsSync(transcript)) {
        const stat = fs.statSync(transcript);
        if (stat.mtimeMs > latestTime) {
          latestTime = stat.mtimeMs;
          latestConv = { convId: entry.name, transcriptPath: transcript };
        }
      }
    }
    return latestConv;
  } catch {
    return null;
  }
}

export function activate(context: vscode.ExtensionContext) {
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 1000);
  statusBarItem.command = 'antigravity.showTelemetryMenu';
  statusBarItem.text = '$(sparkle) Antigravity: Initializing';
  statusBarItem.tooltip = 'Antigravity IDE Live Telemetry';
  statusBarItem.show();

  let activeConvId: string | null = null;
  let activeTranscriptPath: string | null = null;

  const updateUI = () => {
    try {
      // 1. Check if active editor is in a brain conversation folder
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor) {
        const docPath = activeEditor.document.uri.fsPath;
        const match = docPath.match(/\/brain\/([0-9a-fA-F-]{36})\//);
        if (match) {
          activeConvId = match[1];
          activeTranscriptPath = path.join(STATE_DIR, 'brain', activeConvId, '.system_generated', 'logs', 'transcript.jsonl');
        }
      }

      // 2. Fallback to latest active conversation if no thread document is focused
      if (!activeConvId || !activeTranscriptPath || !fs.existsSync(activeTranscriptPath)) {
        const latest = findLatestConversation();
        if (latest) {
          activeConvId = latest.convId;
          activeTranscriptPath = latest.transcriptPath;
        }
      }

      // 3. Compute live token counts from transcript
      let promptTokens = 0;
      let completionTokens = 0;
      if (activeTranscriptPath && fs.existsSync(activeTranscriptPath)) {
        const counts = calculateConversationTokens(activeTranscriptPath);
        promptTokens = counts.promptTokens;
        completionTokens = counts.completionTokens;
      }

      // 4. Read state metadata (triage mode, endpoint)
      let state: AntigravityTokensState = {};
      if (fs.existsSync(STATE_FILE)) {
        try {
          state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
        } catch {}
      }

      const triageMode = state.triageMode || 'Orchestrator';
      const workspaceId = state.workspace_id || 'Global';
      const promptFormatted = promptTokens.toLocaleString();
      const compFormatted = completionTokens.toLocaleString();
      const convShort = activeConvId ? activeConvId.substring(0, 8) : 'N/A';

      statusBarItem.text = `$(sparkle) ${promptFormatted} in / ${compFormatted} out [${triageMode}]`;
      statusBarItem.tooltip = new vscode.MarkdownString(
        `### Antigravity Telemetry\n\n` +
        `- **Active Thread:** \`${convShort}\`\n` +
        `- **Prompt Tokens In:** \`${promptFormatted}\`\n` +
        `- **Completion Tokens Out:** \`${compFormatted}\`\n` +
        `- **Triage Mode:** \`${triageMode}\`\n` +
        `- **Workspace:** \`${workspaceId}\`\n\n` +
        `*Click to switch triage mode or refresh*`
      );
    } catch (err) {
      console.error('Antigravity Telemetry UI update error:', err);
    }
  };

  updateUI();

  // Listen to active editor changes to track thread switches
  const editorListener = vscode.window.onDidChangeActiveTextEditor(() => {
    updateUI();
  });

  // Watch state file
  try {
    fs.watchFile(STATE_FILE, { interval: 1000 }, () => {
      updateUI();
    });
  } catch (err) {
    console.error('Failed to attach fs.watchFile:', err);
  }

  // Poll for token updates every 2 seconds
  const intervalTimer = setInterval(updateUI, 2000);

  // Register commands
  const menuCommand = vscode.commands.registerCommand('antigravity.showTelemetryMenu', async () => {
    updateUI();
    let state: AntigravityTokensState = {};
    if (fs.existsSync(STATE_FILE)) {
      try {
        state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
      } catch {}
    }
    const selection = await vscode.window.showQuickPick(
      [
        {
          label: `$(sparkle) Current Mode: ${state.triageMode || 'Orchestrator'}`,
          description: `Thread: ${activeConvId ? activeConvId.substring(0, 8) : 'Global'}`,
          detail: 'Active execution policy'
        },
        {
          label: '$(refresh) Refresh Telemetry',
          description: 'Re-calculate active thread tokens'
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
        try {
          fs.mkdirSync(STATE_DIR, { recursive: true });
          fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
        } catch {}
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
    editorListener,
    menuCommand,
    refreshCommand,
    new vscode.Disposable(() => {
      clearInterval(intervalTimer);
      try {
        fs.unwatchFile(STATE_FILE);
      } catch {}
    })
  );
}

export function deactivate() {
  try {
    fs.unwatchFile(STATE_FILE);
  } catch {}
}
