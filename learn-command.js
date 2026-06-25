const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// --------------------------------------------------------------------
// Configuration
// --------------------------------------------------------------------
const SCRIPTS_DIR = path.join(os.homedir(), '.ai-os', 'learned-scripts');

// Ensure the scripts directory exists on module load
fs.mkdirSync(SCRIPTS_DIR, { recursive: true });

// In a real project you would import the actual AI client (e.g., Gemini)
// const { callGemini } = require('./ai-client');
// For this example we provide a placeholder that returns a static script.
async function callGemini(task, commands) {
  // Replace with real call to your AI model
  // The model should be given the task description and the list of commands
  // and return a parameterized shell script.
  return `#!/bin/bash
# Script generated for task: ${task}
# Original commands:
${commands.map((c, i) => `#   ${i + 1}: ${c}`).join('\n')}

echo "Hello from generated script. Real AI call would produce a useful script."
`;
}

// --------------------------------------------------------------------
// State (would live in your REPL context)
// --------------------------------------------------------------------
let isLearningMode = false;
let currentLearningTask = null;
let learnedCommands = [];

// --------------------------------------------------------------------
// Helpers
// --------------------------------------------------------------------
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function saveScript(taskName, scriptContent) {
  const fileName = `${slugify(taskName)}.sh`;
  const filePath = path.join(SCRIPTS_DIR, fileName);
  fs.writeFileSync(filePath, scriptContent, { mode: 0o755 });
  return filePath;
}

function getScriptPath(taskName) {
  const fileName = `${slugify(taskName)}.sh`;
  return path.join(SCRIPTS_DIR, fileName);
}

// --------------------------------------------------------------------
// Public API
// --------------------------------------------------------------------

/**
 * Called when the user types `/learn <task description>`.
 * @param {string} taskDescription - e.g. "set up a new Express API with auth middleware"
 */
function startLearning(taskDescription) {
  if (isLearningMode) {
    console.log('⚠️  Already in learning mode. Finish it first with /done.');
    return;
  }
  isLearningMode = true;
  currentLearningTask = taskDescription;
  learnedCommands = [];
  console.log(`📝 Learning mode activated for "${taskDescription}".`);
  console.log('Run commands normally, then type /done to stop recording.');
}

/**
 * Records a command that was executed while in learning mode.
 * @param {string} command - the raw shell command (e.g., "npm install express")
 */
function recordCommand(command) {
  if (!isLearningMode) return;
  learnedCommands.push(command);
}

/**
 * Called when the user types `/done`.
 * Sends the recorded commands to the AI model and saves the generated script.
 */
async function finishLearning() {
  if (!isLearningMode) {
    console.log('ℹ️  Not in learning mode. Use /learn first.');
    return;
  }
  if (learnedCommands.length === 0) {
    console.log('⚠️  No commands were recorded during this session.');
    isLearningMode = false;
    currentLearningTask = null;
    return;
  }

  const task = currentLearningTask;
  const commands = [...learnedCommands];

  isLearningMode = false;
  currentLearningTask = null;
  learnedCommands = [];

  console.log(`⏳ Generalizing ${commands.length} commands into a script...`);

  try {
    const scriptContent = await callGemini(task, commands);
    const filePath = saveScript(task, scriptContent);
    console.log(`✅ Script saved to ${filePath}`);
    console.log(`💡 Run it with: /run ${slugify(task)}`);
  } catch (err) {
    console.error(`❌ Failed to generate script: ${err.message}`);
  }
}

/**
 * Called when the user types `/run <script-name>`.
 * Executes the previously saved script.
 * @param {string} scriptName - slug of the script (e.g., "set-up-express-api")
 */
function runScript(scriptName) {
  const filePath = path.join(SCRIPTS_DIR, `${scriptName}.sh`);
  if (!fs.existsSync(filePath)) {
    console.log(`❌ Script "${scriptName}" not found.`);
    console.log(`   Available scripts:`);
    listScripts();
    return;
  }

  console.log(`🚀 Executing script '${scriptName}'...`);
  try {
    const output = execSync(`bash "${filePath}"`, { encoding: 'utf-8', stdio: 'inherit' });
    console.log(output);
  } catch (err) {
    console.error(`❌ Script execution failed: ${err.message}`);
  }
}

/**
 * Lists all saved scripts.
 */
function listScripts() {
  const files = fs.readdirSync(SCRIPTS_DIR).filter(f => f.endsWith('.sh'));
  if (files.length === 0) {
    console.log('   (no scripts saved yet)');
    return;
  }
  files.forEach(f => {
    const name = f.replace(/\.sh$/, '');
    console.log(`   - ${name}`);
  });
}

module.exports = {
  startLearning,
  recordCommand,
  finishLearning,
  runScript,
  listScripts,
};
