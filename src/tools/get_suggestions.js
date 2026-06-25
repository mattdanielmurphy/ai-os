import fs from 'fs';
import path from 'path';
import os from 'os';

/**
 * Reads ~/.ai-os/suggestions.json and returns unresolved items.
 */
function getUnresolvedSuggestions() {
  const filePath = path.join(os.homedir(), '.ai-os', 'suggestions.json');
  
  if (!fs.existsSync(filePath)) {
    console.log(JSON.stringify({ error: "Suggestions file not found.", suggestions: [] }));
    return;
  }

  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const suggestions = Array.isArray(data) ? data : [];
    
    // Filter for 'pending' status and sort by timestamp descending (latest first)
    const unresolved = suggestions
      .filter(s => s.status === 'pending')
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    console.log(JSON.stringify(unresolved, null, 2));
  } catch (err) {
    console.error(JSON.stringify({ error: "Failed to parse suggestions.", details: err.message }));
  }
}

getUnresolvedSuggestions();
