import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getOrganization, listGrants } from "../api/client";
import type { Organization, Grant } from "../types";

export default function OrganizationDetailPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const [org, setOrg] = useState<Organization | null>(null);
  const [grantsGiven, setGrantsGiven] = useState<Grant[]>([]);
  const [grantsReceived, setGrantsReceived] = useState<Grant[]>([]);

  useEffect(() => {
    if (!orgId) return;
    getOrganization(orgId).then(setOrg);
    listGrants({ funder_org_id: orgId }).then(setGrantsGiven);
    listGrants({ grantee_org_id: orgId }).then(setGrantsReceived);
  }, [orgId]);

  if (!org) return <p>Loading...</p>;

  return (
    <div>
      <div className="page-header">
        <h2>{org.name}</h2>
      </div>
      <div className="card">
        <p>
          <strong>Registry:</strong> {org.registry} &mdash;{" "}
          <strong>ID:</strong> {org.external_id}
        </p>
        <p>
          <strong>Location:</strong>{" "}
          {[org.city, org.region, org.country].filter(Boolean).join(", ") ||
            "N/A"}
        </p>
        {org.website && (
          <p>
            <strong>Website:</strong>{" "}
            <a href={org.website} target="_blank" rel="noreferrer">
              {org.website}
            </a>
          </p>
        )}
      </div>

      <h3 style={{ margin: "1.5rem 0 0.75rem" }}>
        Grants Given ({grantsGiven.length})
      </h3>
      {grantsGiven.length > 0 ? (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Grantee</th>
                <th>Amount</th>
                <th>Year</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {grantsGiven.map((g) => (
                <tr key={g.id}>
                  <td>
                    <Link to={`/organizations/${g.grantee_org_id}`}>
                      {g.grantee_org_id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td>{g.amount ? `$${Number(g.amount).toLocaleString()}` : "N/A"}</td>
                  <td>{g.year ?? "N/A"}</td>
                  <td>{g.source ?? "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p style={{ color: "#888" }}>No grants given recorded.</p>
      )}

      <h3 style={{ margin: "1.5rem 0 0.75rem" }}>
        Grants Received ({grantsReceived.length})
      </h3>
      {grantsReceived.length > 0 ? (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Funder</th>
                <th>Amount</th>
                <th>Year</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {grantsReceived.map((g) => (
                <tr key={g.id}>
                  <td>
                    <Link to={`/organizations/${g.funder_org_id}`}>
                      {g.funder_org_id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td>{g.amount ? `$${Number(g.amount).toLocaleString()}` : "N/A"}</td>
                  <td>{g.year ?? "N/A"}</td>
                  <td>{g.source ?? "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p style={{ color: "#888" }}>No grants received recorded.</p>
      )}
    </div>
  );
}
