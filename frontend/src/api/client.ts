import type {
  Organization,
  Grant,
  Tenant,
  FunnelEntry,
  FunnelStatus,
} from "../types";

const BASE = "/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Organizations
export function listOrganizations(params?: {
  q?: string;
  offset?: number;
  limit?: number;
}): Promise<Organization[]> {
  const sp = new URLSearchParams();
  if (params?.q) sp.set("q", params.q);
  if (params?.offset) sp.set("offset", String(params.offset));
  if (params?.limit) sp.set("limit", String(params.limit));
  return request(`/organizations?${sp}`);
}

export function getOrganization(id: string): Promise<Organization> {
  return request(`/organizations/${id}`);
}

export function countOrganizations(q?: string): Promise<{ count: number }> {
  const sp = new URLSearchParams();
  if (q) sp.set("q", q);
  return request(`/organizations/count?${sp}`);
}

// Grants
export function listGrants(params?: {
  funder_org_id?: string;
  grantee_org_id?: string;
  offset?: number;
  limit?: number;
}): Promise<Grant[]> {
  const sp = new URLSearchParams();
  if (params?.funder_org_id) sp.set("funder_org_id", params.funder_org_id);
  if (params?.grantee_org_id) sp.set("grantee_org_id", params.grantee_org_id);
  if (params?.offset) sp.set("offset", String(params.offset));
  if (params?.limit) sp.set("limit", String(params.limit));
  return request(`/grants?${sp}`);
}

// Tenants
export function listTenants(): Promise<Tenant[]> {
  return request("/tenants");
}

export function createTenant(data: {
  name: string;
  slug: string;
}): Promise<Tenant> {
  return request("/tenants", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Funnel
export function listFunnelEntries(
  tenantId: string,
  status?: FunnelStatus
): Promise<FunnelEntry[]> {
  const sp = new URLSearchParams();
  if (status) sp.set("status", status);
  return request(`/tenants/${tenantId}/funnel?${sp}`);
}

export function createFunnelEntry(
  tenantId: string,
  data: { org_id: string; status?: FunnelStatus }
): Promise<FunnelEntry> {
  return request(`/tenants/${tenantId}/funnel`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function bulkCreateFunnelEntries(
  tenantId: string,
  entries: { org_id: string; status?: FunnelStatus }[]
): Promise<FunnelEntry[]> {
  return request(`/tenants/${tenantId}/funnel/bulk`, {
    method: "POST",
    body: JSON.stringify(entries),
  });
}

export function updateFunnelEntry(
  tenantId: string,
  entryId: string,
  data: { status: FunnelStatus }
): Promise<FunnelEntry> {
  return request(`/tenants/${tenantId}/funnel/${entryId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteFunnelEntry(
  tenantId: string,
  entryId: string
): Promise<void> {
  return request(`/tenants/${tenantId}/funnel/${entryId}`, {
    method: "DELETE",
  });
}
