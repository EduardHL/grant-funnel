import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listOrganizations, countOrganizations } from "../api/client";
import type { Organization } from "../types";

export default function OrganizationsPage() {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [query, setQuery] = useState("");
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const q = query || undefined;
    setLoading(true);
    Promise.all([listOrganizations({ q }), countOrganizations(q)]).then(
      ([data, count]) => {
        setOrgs(data);
        setTotal(count.count);
        setLoading(false);
      }
    );
  }, [query]);

  return (
    <div>
      <div className="page-header">
        <h2>Organizations</h2>
        <span>{total.toLocaleString()} total</span>
      </div>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search organizations..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : orgs.length === 0 ? (
        <div className="empty-state">
          <p>No organizations found.</p>
          <p>Run the indexer to import data from ProPublica.</p>
        </div>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Registry</th>
                <th>External ID</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              {orgs.map((org) => (
                <tr key={org.id}>
                  <td>
                    <Link to={`/organizations/${org.id}`}>{org.name}</Link>
                  </td>
                  <td>{org.registry}</td>
                  <td>{org.external_id}</td>
                  <td>
                    {[org.city, org.region, org.country]
                      .filter(Boolean)
                      .join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
