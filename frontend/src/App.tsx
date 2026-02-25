import { BrowserRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import "./App.css";
import OrganizationsPage from "./pages/OrganizationsPage";
import OrganizationDetailPage from "./pages/OrganizationDetailPage";
import TenantsPage from "./pages/TenantsPage";
import FunnelPage from "./pages/FunnelPage";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <h1>Grant Funnel</h1>
          <NavLink to="/organizations">Organizations</NavLink>
          <NavLink to="/tenants">Tenants</NavLink>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/organizations" replace />} />
            <Route path="/organizations" element={<OrganizationsPage />} />
            <Route path="/organizations/:orgId" element={<OrganizationDetailPage />} />
            <Route path="/tenants" element={<TenantsPage />} />
            <Route path="/tenants/:tenantId/funnel" element={<FunnelPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
