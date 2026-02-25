export interface Organization {
  id: string;
  name: string;
  country: string | null;
  registry: string | null;
  external_id: string | null;
  website: string | null;
  city: string | null;
  region: string | null;
  created_at: string;
  updated_at: string;
}

export interface Grant {
  id: string;
  funder_org_id: string;
  grantee_org_id: string;
  amount: string | null;
  year: number | null;
  source: string | null;
  created_at: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  linked_org_id: string | null;
  created_at: string;
}

export type FunnelStatus =
  | "prospect"
  | "shortlisted"
  | "researching"
  | "application_in_progress"
  | "funded"
  | "passed";

export const FUNNEL_STATUSES: FunnelStatus[] = [
  "prospect",
  "shortlisted",
  "researching",
  "application_in_progress",
  "funded",
  "passed",
];

export const STATUS_LABELS: Record<FunnelStatus, string> = {
  prospect: "Prospect",
  shortlisted: "Shortlisted",
  researching: "Researching",
  application_in_progress: "Application in Progress",
  funded: "Funded",
  passed: "Passed",
};

export interface FunnelEntry {
  id: string;
  tenant_id: string;
  org_id: string;
  status: FunnelStatus;
  created_at: string;
  updated_at: string;
}
