import { ClinicalTrialStudy, LocationFacility } from './types';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const API_BASE_URL = 'https://clinicaltrials.gov/api/v2/studies';

// Edmonton coordinates: 53.5461, -113.4938
const EDMONTON_LAT = 53.5461;
const EDMONTON_LON = -113.4938;
const RADIUS_MILES = 50;

export async function fetchClinicalTrials(): Promise<ClinicalTrialStudy[]> {
  const params = new URLSearchParams({
    'filter.overallStatus': 'RECRUITING,NOT_YET_RECRUITING',
    'query.locn': 'Edmonton OR Alberta',
    'filter.geo': `distance(${EDMONTON_LAT},${EDMONTON_LON},${RADIUS_MILES}mi)`,
    'pageSize': '100',
  });

  const requestUrl = `${API_BASE_URL}?${params.toString()}`;
  console.log(`[Fetcher] Querying ClinicalTrials.gov API v2: ${requestUrl}`);

  const response = await fetch(requestUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch clinical trials: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  const rawStudies = data.studies || [];
  console.log(`[Fetcher] Received ${rawStudies.length} raw studies from API.`);

  const candidateStudies: ClinicalTrialStudy[] = [];

  for (const raw of rawStudies) {
    const protocol = raw.protocolSection || {};
    const nctId = protocol.identificationModule?.nctId;
    if (!nctId) continue;

    const briefTitle = protocol.identificationModule?.briefTitle || 'Untitled Study';
    const officialTitle = protocol.identificationModule?.officialTitle;
    const overallStatus = protocol.statusModule?.overallStatus || 'UNKNOWN';

    // Eligibility parsing
    const eligibility = protocol.eligibilityModule || {};
    const healthyVolunteers = eligibility.healthyVolunteers === true;

    // Age parsing (ClinicalTrials.gov format e.g. "18 Years", "65 Years")
    const minAgeYears = parseAgeToYears(eligibility.minimumAge);
    const maxAgeYears = parseAgeToYears(eligibility.maximumAge);

    // Age Hard-Rule Filter (User is 28 years old)
    const USER_AGE = 28;
    if (minAgeYears !== undefined && USER_AGE < minAgeYears) {
      console.log(`[Filter Out] ${nctId}: User age (28) below minimum age (${minAgeYears}).`);
      continue;
    }
    if (maxAgeYears !== undefined && USER_AGE > maxAgeYears) {
      console.log(`[Filter Out] ${nctId}: User age (28) above maximum age (${maxAgeYears}).`);
      continue;
    }

    // Conditions
    const conditions = protocol.conditionsModule?.conditions || [];

    // Locations
    const rawLocations = protocol.contactsLocationsModule?.locations || [];
    const locations: LocationFacility[] = rawLocations.map((loc: any) => ({
      facility: loc.facility,
      city: loc.city,
      state: loc.state,
      zip: loc.zip,
      country: loc.country,
      geoPoint: loc.geoPoint ? { lat: loc.geoPoint.lat, lon: loc.geoPoint.lon } : undefined,
    }));

    // Summary & Criteria text
    const briefSummary = protocol.descriptionModule?.briefSummary;
    const eligibilityCriteria = eligibility.eligibilityCriteria;

    // Contacts
    const rawContacts = protocol.contactsLocationsModule?.centralContacts || [];
    const contacts = rawContacts.map((c: any) => ({
      name: c.name,
      phone: c.phone,
      email: c.email,
    }));

    candidateStudies.push({
      nctId,
      briefTitle,
      officialTitle,
      overallStatus,
      healthyVolunteers,
      minAgeYears,
      maxAgeYears,
      conditions,
      locations,
      briefSummary,
      eligibilityCriteria,
      contacts,
      url: `https://clinicaltrials.gov/study/${nctId}`,
    });
  }

  console.log(`[Fetcher] Filtered down to ${candidateStudies.length} candidate studies for AI evaluation.`);
  return candidateStudies;
}

function parseAgeToYears(ageStr?: string): number | undefined {
  if (!ageStr) return undefined;
  const match = ageStr.match(/(\d+)\s*(Year|Years|Yr|Yrs)/i);
  if (match) {
    return parseInt(match[1], 10);
  }
  return undefined;
}

// Run directly when executed
if (import.meta.main) {
  try {
    const studies = await fetchClinicalTrials();
    const outputDir = join(process.cwd(), 'tmp');
    mkdirSync(outputDir, { recursive: true });
    const outputPath = join(outputDir, 'candidate_trials.json');
    writeFileSync(outputPath, JSON.stringify(studies, null, 2));
    console.log(`[Fetcher] Successfully wrote candidate studies payload to ${outputPath}`);
  } catch (err) {
    console.error(`[Fetcher Error]:`, err);
    process.exit(1);
  }
}
