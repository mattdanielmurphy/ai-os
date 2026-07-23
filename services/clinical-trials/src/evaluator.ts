import { ClinicalTrialStudy, TrialEvaluationResult, EvaluationVerdict } from './types';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

export function evaluateTrialRuleBased(study: ClinicalTrialStudy, profileText: string): TrialEvaluationResult {
  const criteriaText = (study.eligibilityCriteria || '').toLowerCase();
  const summaryText = (study.briefSummary || '').toLowerCase();
  const titleText = (study.briefTitle || '' + ' ' + (study.officialTitle || '')).toLowerCase();
  const fullText = `${titleText} ${summaryText} ${criteriaText}`;

  const flaggedDisqualifiers: string[] = [];
  let matchScore = 80;
  let verdict: EvaluationVerdict = 'MATCH';

  // Rule 1: Mounjaro / GLP-1 Exclusions
  if (
    fullText.includes('glp-1') ||
    fullText.includes('tirzepatide') ||
    fullText.includes('semaglutide') ||
    fullText.includes('weight loss medication') ||
    fullText.includes('anti-obesity medication')
  ) {
    if (criteriaText.includes('exclusion') && (criteriaText.includes('glp-1') || criteriaText.includes('weight loss'))) {
      verdict = 'INELIGIBLE';
      flaggedDisqualifiers.push('Active GLP-1 / Mounjaro (tirzepatide) exclusion');
      matchScore = 0;
    } else {
      verdict = 'UNCERTAIN';
      flaggedDisqualifiers.push('Mentions GLP-1 / weight loss medications; requires manual check for active user exclusion');
      matchScore = 50;
    }
  }

  // Rule 2: Cannabis / Substance Restrictions
  if (
    criteriaText.includes('cannabis') ||
    criteriaText.includes('marijuana') ||
    criteriaText.includes('substance use') ||
    criteriaText.includes('thc')
  ) {
    if (criteriaText.includes('exclude') || criteriaText.includes('exclusion') || criteriaText.includes('prohibited')) {
      verdict = 'INELIGIBLE';
      flaggedDisqualifiers.push('Cannabis use exclusion or positive drug screen requirement');
      matchScore = 0;
    } else {
      if (verdict !== 'INELIGIBLE') verdict = 'UNCERTAIN';
      flaggedDisqualifiers.push('Mentions cannabis/substance criteria');
      matchScore = Math.min(matchScore, 60);
    }
  }

  // Rule 3: SSRI / Fluoxetine Exclusions
  if (
    criteriaText.includes('ssri') ||
    criteriaText.includes('fluoxetine') ||
    criteriaText.includes('antidepressant') ||
    criteriaText.includes('psychotropic')
  ) {
    if (criteriaText.includes('exclusion') || criteriaText.includes('prohibit') || criteriaText.includes('washout')) {
      verdict = 'INELIGIBLE';
      flaggedDisqualifiers.push('Active SSRI (Fluoxetine / Prozac) exclusion or required medication washout');
      matchScore = 0;
    } else {
      if (verdict !== 'INELIGIBLE') verdict = 'UNCERTAIN';
      flaggedDisqualifiers.push('Mentions psychotropic / SSRI medication criteria');
      matchScore = Math.min(matchScore, 55);
    }
  }

  // Rule 4: Resistance Training / Fitness Requirements
  if (
    criteriaText.includes('resistance training') ||
    criteriaText.includes('regular exercise') ||
    criteriaText.includes('athlete') ||
    criteriaText.includes('trained individuals')
  ) {
    if (criteriaText.includes('must have') || criteriaText.includes('required') || criteriaText.includes('inclusion')) {
      verdict = 'INELIGIBLE';
      flaggedDisqualifiers.push('Requires prior active resistance training history (user is sedentary)');
      matchScore = 0;
    }
  }

  // Rule 5: BMI Thresholds (User BMI ~34.5)
  const bmiMatch = criteriaText.match(/bmi\s*(<|>|<=|>=|less than|greater than|between)?\s*(\d+(\.\d+)?)/i);
  if (bmiMatch) {
    const bmiVal = parseFloat(bmiMatch[2]);
    if (criteriaText.includes('bmi <') || criteriaText.includes('bmi less than')) {
      if (bmiVal < 34.5) {
        verdict = 'INELIGIBLE';
        flaggedDisqualifiers.push(`Strict BMI upper limit (< ${bmiVal}) excludes user BMI (~34.5)`);
        matchScore = 0;
      }
    }
  }

  // Rule 6: Healthy Volunteers
  if (study.healthyVolunteers && verdict === 'MATCH') {
    matchScore = Math.max(matchScore, 90);
  }

  // Rationale Generation
  let rationale = '';
  if (verdict === 'MATCH') {
    rationale = `Study matches user profile (Age 28, Edmonton Metro). Fits healthy volunteer or general eligibility without flagged medication or lifestyle disqualifiers.`;
  } else if (verdict === 'UNCERTAIN') {
    rationale = `Potential match requiring manual verification. Flagged criteria: ${flaggedDisqualifiers.join('; ')}.`;
  } else {
    rationale = `Ineligible due to hard disqualifier(s): ${flaggedDisqualifiers.join('; ')}.`;
  }

  // Compensation Extraction
  let estimatedCompensation: string | undefined = undefined;
  const compMatch = fullText.match(/(\$\d+|\d+\s*dollars|stipend|compensation|paid|reimbursement)/i);
  if (compMatch) {
    const contextSnippet = fullText.substring(Math.max(0, compMatch.index! - 30), Math.min(fullText.length, compMatch.index! + 60));
    estimatedCompensation = contextSnippet.trim();
  }

  return {
    study,
    verdict,
    matchScore,
    rationale,
    flaggedDisqualifiers,
    estimatedCompensation,
  };
}

export async function evaluateAllCandidateTrials(): Promise<TrialEvaluationResult[]> {
  const candidatePath = join(process.cwd(), 'tmp', 'candidate_trials.json');
  if (!existsSync(candidatePath)) {
    throw new Error(`Candidate trials file not found at ${candidatePath}. Run fetcher first.`);
  }

  const rawData = readFileSync(candidatePath, 'utf-8');
  const studies: ClinicalTrialStudy[] = JSON.parse(rawData);

  const profilePath = join(process.cwd(), '..', '..', 'context', 'clinical-profile.md');
  const profileText = existsSync(profilePath) ? readFileSync(profilePath, 'utf-8') : '';

  console.log(`[Evaluator] Evaluating ${studies.length} candidate studies...`);
  const results: TrialEvaluationResult[] = [];

  for (const study of studies) {
    const evalResult = evaluateTrialRuleBased(study, profileText);
    results.push(evalResult);
  }

  const matches = results.filter(r => r.verdict === 'MATCH');
  const uncertains = results.filter(r => r.verdict === 'UNCERTAIN');
  const ineligibles = results.filter(r => r.verdict === 'INELIGIBLE');

  console.log(`[Evaluator Summary]:`);
  console.log(`  - Matched: ${matches.length}`);
  console.log(`  - Uncertain / Potential Match: ${uncertains.length}`);
  console.log(`  - Ineligible (Ignored): ${ineligibles.length}`);

  const outputPath = join(process.cwd(), 'tmp', 'evaluated_trials.json');
  writeFileSync(outputPath, JSON.stringify(results, null, 2));
  console.log(`[Evaluator] Successfully wrote evaluated trials to ${outputPath}`);

  return results;
}

if (import.meta.main) {
  await evaluateAllCandidateTrials();
}
