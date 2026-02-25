# Grant Funnel — Project Spec

## Overview

Grant Funnel is a web application that helps **grant makers discover and manage potential grantees**. It has two major components:

1. **The Indexer** — a data pipeline that builds a structured database of nonprofits, grant-makers, and the grants between them, sourced from public datasets (ProPublica Nonprofit Explorer, Open990, UK Charity Commission, and eventually scraped grant-maker websites).
2. **The CRM / Funnel Tool** — a multi-tenant application where grant-making organizations manage a pipeline of prospective grantees. Supports bulk population (e.g. "import all orgs funded by Funder X into my funnel") and will eventually include overlap-based recommendations.

## Architecture

### Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend API | **Python 3.12+ / FastAPI** | Serves the CRM API and shares codebase with the indexer |
| Database | **PostgreSQL 16** | Shared public index + tenant-private funnel data |
| ORM | **SQLAlchemy 2.0** + **Alembic** | Async support, migrations |
| Background Jobs | **CLI scripts** (invoke via cron) | Keep simple for v1; add Celery/task queue later if needed |
| Frontend | **React (Vite + TypeScript)** | SPA that talks to the FastAPI backend |
| Auth | **TBD** (likely JWT + OAuth2) | Must support multi-tenancy |

### Project Structure

```
grant-funnel/
├── CLAUDE.md                  # This file
├── README.md
├── docker-compose.yml         # Postgres + backend + frontend for local dev
│
├── backend/
│   ├── pyproject.toml         # Python dependencies (use uv or poetry)
│   ├── alembic/               # Database migrations
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Settings (env vars, DB URL, etc.)
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── organization.py
│   │   │   ├── grant.py
│   │   │   ├── tenant.py
│   │   │   └── funnel_entry.py
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/               # FastAPI routers
│   │   │   ├── organizations.py
│   │   │   ├── grants.py
│   │   │   ├── funnel.py
│   │   │   └── tenants.py
│   │   ├── services/          # Business logic layer
│   │   └── db.py              # Database session management
│   │
│   ├── indexer/               # Data pipeline (same codebase, shared models)
│   │   ├── __main__.py        # CLI entry point: python -m indexer
│   │   ├── base.py            # Abstract connector interface
│   │   ├── connectors/
│   │   │   ├── propublica.py  # ProPublica Nonprofit Explorer connector
│   │   │   ├── open990.py     # Open990 connector (future)
│   │   │   └── uk_charity.py  # UK Charity Commission connector (future)
│   │   └── loader.py          # Upsert logic into the shared DB
│   │
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/               # API client (fetch wrapper or react-query)
│   │   └── types/
│   └── public/
│
└── scripts/
    └── seed.py                # Dev seed data
```

## Data Model (v1 — intentionally minimal)

### Organization
The central entity. Both funders and grantees are rows in this table. The distinction is **computed from activity**, not stored as a type field.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Internal primary key |
| `name` | TEXT | Required |
| `country` | TEXT | ISO 3166-1 alpha-2 (e.g. "US", "GB") |
| `registry` | TEXT | e.g. "IRS", "UK_CHARITY_COMMISSION" |
| `external_id` | TEXT | EIN, UK charity number, etc. |
| `website` | TEXT | Nullable |
| `city` | TEXT | Nullable |
| `region` | TEXT | Nullable (state, county, etc.) |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

**Unique constraint**: `(registry, external_id)` — an org is uniquely identified by its registry + ID.

### Grant
A directed relationship: one Organization funded another.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Internal primary key |
| `funder_org_id` | UUID | FK → Organization |
| `grantee_org_id` | UUID | FK → Organization |
| `amount` | NUMERIC | In original currency (assume USD for v1) |
| `year` | INTEGER | Fiscal year of the grant |
| `source` | TEXT | Which connector produced this record (e.g. "propublica", "open990") |
| `created_at` | TIMESTAMP | |

**Index**: `(funder_org_id)`, `(grantee_org_id)`, `(funder_org_id, grantee_org_id)`.

### Tenant
A grant-making organization that has signed up to use the CRM. May also exist as an Organization in the public index.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Internal primary key |
| `name` | TEXT | Display name |
| `slug` | TEXT | URL-safe identifier, unique |
| `linked_org_id` | UUID | Nullable FK → Organization (if they exist in the index) |
| `created_at` | TIMESTAMP | |

### FunnelEntry
Links a Tenant to an Organization with pipeline status.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Internal primary key |
| `tenant_id` | UUID | FK → Tenant |
| `org_id` | UUID | FK → Organization |
| `status` | ENUM | See statuses below |
| `created_at` | TIMESTAMP | When added to funnel |
| `updated_at` | TIMESTAMP | Last status change |

**Unique constraint**: `(tenant_id, org_id)` — an org appears in a tenant's funnel at most once.

**Funnel Statuses (ordered pipeline)**:
1. `prospect` — Identified as a potential grantee
2. `shortlisted` — Selected for closer evaluation
3. `researching` — Actively gathering information
4. `application_in_progress` — Grantee is preparing or submitting an application
5. `funded` — Grant awarded
6. `passed` — Decided not to fund (terminal state)

## Indexer Design

### Connector Interface
Each data source implements a connector. All connectors share the same interface:

```python
class BaseConnector(ABC):
    @abstractmethod
    def fetch(self) -> Iterator[RawRecord]:
        """Yield raw records from the data source."""
        pass
```

The `loader` module takes raw records and upserts them into Organization and Grant tables, handling deduplication via `(registry, external_id)`.

### v1 Connector: ProPublica Nonprofit Explorer
- **API**: https://projects.propublica.org/nonprofits/api
- Provides org search, org details, and 990 filing data
- Key endpoints:
  - `GET /api/v2/search.json?q={query}` — search orgs
  - `GET /api/v2/organizations/{ein}.json` — org details + filings
- Grant-level data (funder → grantee) may require parsing Schedule I of 990-PF filings (XML)
- Start with bulk org import; add grant relationship extraction as a second step

### Future Connectors (not for v1)
- **Open990** — alternative/supplement to ProPublica
- **UK Charity Commission** — public dataset for UK charities
- **Website scraper** — extract grantee lists from funder websites (less structured)

## Key Design Decisions

1. **Single Organization entity** — no hard funder/grantee distinction. The profile (primarily funder, primarily grantee, both) is computed from grant activity (count and volume of grants given vs. received).

2. **Shared index, private funnels** — the Organization and Grant tables are public/shared across all tenants. FunnelEntry is private per tenant.

3. **International-ready schema** — `registry` + `external_id` instead of a US-specific EIN field. Supports IRS, UK Charity Commission, and future registries without schema changes.

4. **Start simple, add incrementally** — v1 is a one-time snapshot import. Incremental refresh, additional data fields (NTEE codes, descriptions, focus areas), and recommendations come later.

5. **Recommendations approach (future)** — find funders with high portfolio overlap, then surface what they fund that the current tenant doesn't. Simple, interpretable, no ML required. Depends on good funder→grantee relationship coverage in the index.

## Build Priorities (ordered)

### Phase 1: Foundation
- [ ] Project scaffold (backend + frontend + docker-compose)
- [ ] Database schema + Alembic migrations
- [ ] Basic FastAPI CRUD endpoints for Organizations, Grants
- [ ] ProPublica connector — bulk org import

### Phase 2: CRM Core
- [ ] Tenant + auth model
- [ ] FunnelEntry CRUD + status transitions
- [ ] Frontend: funnel board view (kanban or table)
- [ ] Bulk add to funnel ("import all grantees of Funder X")

### Phase 3: Discovery & Enrichment
- [ ] Grant relationship extraction (parse 990-PF Schedule I)
- [ ] Computed org stats (grants given/received, top co-funders)
- [ ] Search and filter organizations in the index
- [ ] Frontend: org detail page with grant history

### Phase 4: Recommendations (future)
- [ ] Funder overlap scoring
- [ ] "Funders like you also funded..." suggestions
- [ ] Additional connectors (UK Charity Commission, website scraper)

## Development Commands

```bash
# Backend
cd backend
uv sync                              # Install dependencies
alembic upgrade head                  # Run migrations
uvicorn app.main:app --reload         # Start API server
python -m indexer                     # Run indexer (one-time import)

# Frontend
cd frontend
npm install
npm run dev                           # Start Vite dev server

# Database
docker-compose up -d postgres         # Start Postgres
```

## Conventions

- **Python**: Follow PEP 8. Use type hints everywhere. Async endpoints in FastAPI.
- **TypeScript**: Strict mode. Prefer functional components with hooks.
- **Database**: Use Alembic for all schema changes. Never modify the DB manually.
- **API**: RESTful. Use Pydantic schemas for request/response validation. Return consistent error shapes.
- **Testing**: pytest for backend. Vitest for frontend. Prioritize integration tests for API endpoints and indexer logic.
- **Environment**: Use `.env` files for config. Never commit secrets.
