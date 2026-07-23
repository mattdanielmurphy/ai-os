export interface LocationFacility {
  facility?: string;
  city?: string;
  state?: string;
  zip?: string;
  country?: string;
  geoPoint?: {
    lat: number;
    lon: number;
  };
}

export interface ClinicalTrialStudy {
  nctId: string;
  briefTitle: string;
  officialTitle?: string;
  overallStatus: string;
  healthyVolunteers?: boolean;
  minAgeYears?: number;
  maxAgeYears?: number;
  conditions: string[];
  locations: LocationFacility[];
  briefSummary?: string;
  eligibilityCriteria?: string;
  contacts?: Array<{
    name?: string;
    phone?: string;
    email?: string;
  }>;
  compensationInfo?: string;
  url: string;
}

export type EvaluationVerdict = 'MATCH' | 'UNCERTAIN' | 'INELIGIBLE';

export interface TrialEvaluationResult {
  study: ClinicalTrialStudy;
  verdict: EvaluationVerdict;
  matchScore: number; // 0 - 100
  rationale: string;
  flaggedDisqualifiers: string[];
  estimatedCompensation?: string;
}
