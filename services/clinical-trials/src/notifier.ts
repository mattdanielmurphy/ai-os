import { TrialEvaluationResult } from './types';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';
import { execSync } from 'child_process';

const OBSIDIAN_TARGET_DIR = '/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Financial/Clinical Trials';

export async function processNotificationsAndNotes(): Promise<void> {
  const evaluatedPath = join(process.cwd(), 'tmp', 'evaluated_trials.json');
  if (!existsSync(evaluatedPath)) {
    throw new Error(`Evaluated trials file not found at ${evaluatedPath}. Run evaluator first.`);
  }

  const rawData = readFileSync(evaluatedPath, 'utf-8');
  const results: TrialEvaluationResult[] = JSON.parse(rawData);

  // Filter out INELIGIBLE completely
  const notifyList = results.filter(r => r.verdict === 'MATCH' || r.verdict === 'UNCERTAIN');
  console.log(`[Notifier] Processing ${notifyList.length} qualified trials for notes and notifications...`);

  // Ensure Obsidian directory exists
  if (!existsSync(OBSIDIAN_TARGET_DIR)) {
    mkdirSync(OBSIDIAN_TARGET_DIR, { recursive: true });
  }

  let createdNotesCount = 0;
  const newMatches: TrialEvaluationResult[] = [];

  for (const item of notifyList) {
    const study = item.study;
    const cleanTitle = sanitizeFilename(study.briefTitle);
    const fileName = `${study.nctId} - ${cleanTitle.substring(0, 60)}.md`;
    const filePath = join(OBSIDIAN_TARGET_DIR, fileName);

    // Skip if note already created previously
    if (existsSync(filePath)) {
      continue;
    }

    const noteContent = generateObsidianNoteContent(item, fileName);
    writeFileSync(filePath, noteContent, 'utf-8');
    createdNotesCount++;
    newMatches.push(item);
    console.log(`[Note Created] ${fileName}`);
  }

  console.log(`[Notifier] Created ${createdNotesCount} new trial note(s) in Obsidian.`);

  if (newMatches.length > 0) {
    await sendHermesAlerts(newMatches);
  } else {
    console.log(`[Notifier] No new unnotified matches to dispatch.`);
  }
}

function sanitizeFilename(name: string): string {
  return name.replace(/[/\\?%*:|"<>]/g, '').replace(/\s+/g, ' ').trim();
}

function generateObsidianNoteContent(item: TrialEvaluationResult, noteFileName: string): string {
  const { study, verdict, matchScore, rationale, flaggedDisqualifiers, estimatedCompensation } = item;
  const locationsStr = study.locations.map(l => `- ${l.facility || 'Facility'}, ${l.city || 'Edmonton'}, ${l.state || 'AB'}`).join('\n') || '- Edmonton Metropolitan Area';
  const contactsStr = study.contacts?.map(c => `- ${c.name || 'Coordinator'}: ${c.phone || 'N/A'} (${c.email || 'N/A'})`).join('\n') || '- Contact study coordinator via ClinicalTrials.gov link';

  return `---
id: "${study.nctId}"
title: "${study.briefTitle.replace(/"/g, '\\"')}"
verdict: "${verdict}"
matchScore: ${matchScore}
status: "${study.overallStatus}"
url: "${study.url}"
tags: [clinical-trial, money, edmonton, ${verdict.toLowerCase()}]
created: "${new Date().toISOString().split('T')[0]}"
---

# 🧪 ${study.briefTitle}

- **NCT ID:** [${study.nctId}](${study.url})
- **Evaluation Verdict:** \`${verdict}\` (Match Score: ${matchScore}/100)
- **Status:** ${study.overallStatus}
- **Estimated Compensation / Perks:** ${estimatedCompensation || 'Compensation not explicitly listed in API summary (Check site contact)'}

---

## 💡 AI Rationale & Assessment
${rationale}

${flaggedDisqualifiers.length > 0 ? `### ⚠️ Flagged Disqualifiers / Review Points\n${flaggedDisqualifiers.map(f => `- ${f}`).join('\n')}\n` : ''}

---

## 📍 Locations & Facilities
${locationsStr}

---

## 📞 Contact Information
${contactsStr}

---

## 📋 Conditions & Eligibility Criteria
- **Conditions:** ${study.conditions.join(', ') || 'Healthy Volunteers / General'}
- **Minimum Age:** ${study.minAgeYears ?? 'None'}
- **Maximum Age:** ${study.maxAgeYears ?? 'None'}

### Eligibility Criteria Text
\`\`\`text
${study.eligibilityCriteria || 'See study page for full criteria details.'}
\`\`\`
`;
}

async function sendHermesAlerts(newMatches: TrialEvaluationResult[]): Promise<void> {
  const summaryCount = newMatches.length;
  const topMatch = newMatches[0];

  const alertMessage = `🧪 [ai-os Clinical Trials Alert] Found ${summaryCount} new potential trial match(es)!
Top Match: ${topMatch.study.nctId} - ${topMatch.study.briefTitle.substring(0, 60)}
Verdict: ${topMatch.verdict} (Score: ${topMatch.matchScore}/100)
Obsidian Note: Personal/Financial/Clinical Trials/${topMatch.study.nctId} - ...
Link: ${topMatch.study.url}`;

  console.log(`[Hermes iMessage Alert Payload]:\n${alertMessage}`);

  // Trigger notification via AppleScript iMessage / osascript fallback if available
  try {
    const appleScript = `osascript -e 'display notification "Found ${summaryCount} new clinical trial matches!" with title "Clinical Trial Scraper"'`;
    execSync(appleScript);
    console.log(`[Notifier] macOS desktop notification dispatched.`);
  } catch (e) {
    console.warn(`[Notifier] Desktop notification failed to dispatch:`, e);
  }
}

if (import.meta.main) {
  await processNotificationsAndNotes();
}
