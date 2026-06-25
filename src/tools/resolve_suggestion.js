import fs from 'fs';
import path from 'path';
import os from 'os';

const suggestionId = parseInt(process.argv[2], 10);

if (isNaN(suggestionId)) {
  console.error("Usage: node src/tools/resolve_suggestion.js <suggestion_id>");
  process.exit(1);
}

const filePath = path.join(os.homedir(), '.ai-os', 'suggestions.json');

if (!fs.existsSync(filePath)) {
  console.error("Suggestions file not found.");
  process.exit(1);
}

try {
  const suggestions = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const index = suggestions.findIndex(s => s.id === suggestionId);

  if (index === -1) {
    console.error(`Suggestion ID ${suggestionId} not found.`);
    process.exit(1);
  }

  suggestions[index].status = 'resolved';
  suggestions[index].resolved_at = new Date().toISOString();

  fs.writeFileSync(filePath, JSON.stringify(suggestions, null, 2), 'utf8');
  console.log(`Successfully marked suggestion ${suggestionId} as resolved.`);
} catch (err) {
  console.error(`Error updating suggestions: ${err.message}`);
  process.exit(1);
}
