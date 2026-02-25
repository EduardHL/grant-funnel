import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listTenants, createTenant } from "../api/client";
import type { Tenant } from "../types";

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");

  useEffect(() => {
    listTenants().then(setTenants);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createTenant({ name, slug });
    setShowCreate(false);
    setName("");
    setSlug("");
    listTenants().then(setTenants);
  };

  return (
    <div>
      <div className="page-header">
        <h2>Tenants</h2>
        <button className="primary" onClick={() => setShowCreate(true)}>
          New Tenant
        </button>
      </div>

      {tenants.length === 0 ? (
        <div className="empty-state">
          <p>No tenants yet. Create one to get started.</p>
        </div>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.id}>
                  <td>{t.name}</td>
                  <td>{t.slug}</td>
                  <td>{new Date(t.created_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/tenants/${t.id}/funnel`}>
                      <button>View Funnel</button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create Tenant</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    setSlug(
                      e.target.value
                        .toLowerCase()
                        .replace(/[^a-z0-9]+/g, "-")
                        .replace(/^-|-$/g, "")
                    );
                  }}
                  required
                />
              </div>
              <div className="form-group">
                <label>Slug</label>
                <input
                  type="text"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  required
                />
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowCreate(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
