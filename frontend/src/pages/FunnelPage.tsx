import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import {
  listFunnelEntries,
  listOrganizations,
  createFunnelEntry,
  updateFunnelEntry,
  deleteFunnelEntry,
} from "../api/client";
import type { FunnelEntry, Organization, FunnelStatus } from "../types";
import { FUNNEL_STATUSES, STATUS_LABELS } from "../types";

export default function FunnelPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [entries, setEntries] = useState<FunnelEntry[]>([]);
  const [orgMap, setOrgMap] = useState<Record<string, Organization>>({});
  const [showAdd, setShowAdd] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Organization[]>([]);

  const loadEntries = useCallback(async () => {
    if (!tenantId) return;
    const data = await listFunnelEntries(tenantId);
    setEntries(data);
    // Fetch org details for each entry
    const orgIds = [...new Set(data.map((e) => e.org_id))];
    const orgs = await Promise.all(
      orgIds.map((id) =>
        fetch(`/api/organizations/${id}`)
          .then((r) => r.json())
          .catch(() => null)
      )
    );
    const map: Record<string, Organization> = {};
    for (const org of orgs) {
      if (org) map[org.id] = org;
    }
    setOrgMap(map);
  }, [tenantId]);

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  const handleStatusChange = async (
    entryId: string,
    status: FunnelStatus
  ) => {
    if (!tenantId) return;
    await updateFunnelEntry(tenantId, entryId, { status });
    loadEntries();
  };

  const handleDelete = async (entryId: string) => {
    if (!tenantId) return;
    await deleteFunnelEntry(tenantId, entryId);
    loadEntries();
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    const results = await listOrganizations({ q: searchQuery });
    setSearchResults(results);
  };

  const handleAddToFunnel = async (orgId: string) => {
    if (!tenantId) return;
    await createFunnelEntry(tenantId, { org_id: orgId });
    setShowAdd(false);
    setSearchQuery("");
    setSearchResults([]);
    loadEntries();
  };

  const grouped = FUNNEL_STATUSES.reduce(
    (acc, status) => {
      acc[status] = entries.filter((e) => e.status === status);
      return acc;
    },
    {} as Record<FunnelStatus, FunnelEntry[]>
  );

  return (
    <div>
      <div className="page-header">
        <h2>Funnel</h2>
        <button className="primary" onClick={() => setShowAdd(true)}>
          Add Organization
        </button>
      </div>

      <div className="kanban">
        {FUNNEL_STATUSES.map((status) => (
          <div className="kanban-column" key={status}>
            <h3>
              {STATUS_LABELS[status]}{" "}
              <span className="count">{grouped[status].length}</span>
            </h3>
            {grouped[status].map((entry) => {
              const org = orgMap[entry.org_id];
              const statusIdx = FUNNEL_STATUSES.indexOf(entry.status);
              const nextStatuses = FUNNEL_STATUSES.filter(
                (_, i) => i !== statusIdx
              );
              return (
                <div className="kanban-card" key={entry.id}>
                  <div className="org-name">
                    {org ? (
                      <Link to={`/organizations/${org.id}`}>{org.name}</Link>
                    ) : (
                      entry.org_id.slice(0, 8) + "..."
                    )}
                  </div>
                  {org && (
                    <div style={{ color: "#888", fontSize: "0.75rem" }}>
                      {[org.city, org.region].filter(Boolean).join(", ")}
                    </div>
                  )}
                  <div className="actions">
                    {nextStatuses.slice(0, 3).map((s) => (
                      <button
                        key={s}
                        onClick={() => handleStatusChange(entry.id, s)}
                      >
                        {STATUS_LABELS[s]}
                      </button>
                    ))}
                    <button
                      onClick={() => handleDelete(entry.id)}
                      style={{ color: "#c5221f" }}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              );
            })}
            {grouped[status].length === 0 && (
              <div
                style={{
                  color: "#bbb",
                  fontSize: "0.8rem",
                  textAlign: "center",
                  padding: "1rem 0",
                }}
              >
                No entries
              </div>
            )}
          </div>
        ))}
      </div>

      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add Organization to Funnel</h3>
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search organizations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <button onClick={handleSearch}>Search</button>
            </div>
            {searchResults.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Location</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {searchResults.map((org) => (
                    <tr key={org.id}>
                      <td>{org.name}</td>
                      <td>
                        {[org.city, org.region].filter(Boolean).join(", ")}
                      </td>
                      <td>
                        <button
                          className="primary"
                          onClick={() => handleAddToFunnel(org.id)}
                        >
                          Add
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <div className="form-actions">
              <button onClick={() => setShowAdd(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
