# Grant Funnel

A web application that helps grant makers discover and manage potential grantees. It combines a public nonprofit index (sourced from ProPublica and other datasets) with a multi-tenant CRM funnel for managing grantee pipelines.

## Architecture

| Layer       | Technology                   |
| ----------- | ---------------------------- |
| Backend API | Python 3.12+ / FastAPI       |
| Database    | PostgreSQL 16                |
| ORM         | SQLAlchemy 2.0 + Alembic     |
| Frontend    | React (Vite + TypeScript)    |
| Indexer     | CLI pipeline (ProPublica v1) |

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker & Docker Compose (optional, for Postgres)

## Quick Start

### 1. Start PostgreSQL

Using Docker:

```bash
docker-compose up -d postgres
```

Or if Postgres is already running locally, create the role and database:

```bash
psql -U $(whoami) -d postgres -c "CREATE ROLE grantfunnel WITH LOGIN PASSWORD 'grantfunnel';"
psql -U $(whoami) -d postgres -c "CREATE DATABASE grantfunnel OWNER grantfunnel;"
```

### 2. Backend

```bash
cd backend
uv sync                            # Install Python dependencies
uv run alembic upgrade head        # Run database migrations
uv run uvicorn app.main:app --reload  # Start the API server on :8000
```

### 3. Seed Data (optional)

In a separate terminal:

```bash
cd backend
uv run python ../scripts/seed.py
```

This creates 8 sample organizations, 7 grants, 1 demo tenant, and 5 funnel entries.

### 4. Frontend

In a separate terminal:

```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Start Vite dev server on :5173
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 5. Import Real Data from ProPublica

```bash
cd backend

# Search by keyword (fetches up to 5 pages of results)
uv run python -m indexer --query "foundation" --max-pages 3

# Fetch specific organizations by EIN
uv run python -m indexer --eins "562618866,131684331"
```

## API Endpoints

| Method   | Path                                     | Description                     |
| -------- | ---------------------------------------- | ------------------------------- |
| `GET`    | `/api/health`                            | Health check                    |
| `GET`    | `/api/organizations`                     | List organizations (`?q=` search) |
| `GET`    | `/api/organizations/count`               | Count organizations             |
| `GET`    | `/api/organizations/{id}`                | Get organization details        |
| `POST`   | `/api/organizations`                     | Create organization             |
| `PATCH`  | `/api/organizations/{id}`                | Update organization             |
| `DELETE` | `/api/organizations/{id}`                | Delete organization             |
| `GET`    | `/api/grants`                            | List grants (filter by funder/grantee) |
| `GET`    | `/api/grants/{id}`                       | Get grant details               |
| `POST`   | `/api/grants`                            | Create grant                    |
| `DELETE` | `/api/grants/{id}`                       | Delete grant                    |
| `GET`    | `/api/tenants`                           | List tenants                    |
| `GET`    | `/api/tenants/{id}`                      | Get tenant details              |
| `POST`   | `/api/tenants`                           | Create tenant                   |
| `GET`    | `/api/tenants/{id}/funnel`               | List funnel entries (`?status=` filter) |
| `POST`   | `/api/tenants/{id}/funnel`               | Add org to funnel               |
| `POST`   | `/api/tenants/{id}/funnel/bulk`          | Bulk add orgs to funnel         |
| `PATCH`  | `/api/tenants/{id}/funnel/{entry_id}`    | Update funnel entry status      |
| `DELETE` | `/api/tenants/{id}/funnel/{entry_id}`    | Remove from funnel              |

## Project Structure

```
grant-funnel/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Settings (env vars)
│   │   ├── db.py              # Async database session
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/               # FastAPI routers
│   │   └── services/          # Business logic (future)
│   ├── indexer/
│   │   ├── __main__.py        # CLI entry point
│   │   ├── base.py            # Abstract connector interface
│   │   ├── connectors/        # Data source connectors
│   │   └── loader.py          # Upsert logic
│   ├── alembic/               # Database migrations
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/client.ts      # API client
│       ├── types/index.ts     # TypeScript types
│       └── pages/             # React page components
├── scripts/
│   └── seed.py                # Development seed data
└── docker-compose.yml
```

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```
DATABASE_URL=postgresql+asyncpg://grantfunnel:grantfunnel@localhost:5432/grantfunnel
```

## Funnel Statuses

The CRM pipeline tracks organizations through these stages:

1. **Prospect** — Identified as a potential grantee
2. **Shortlisted** — Selected for closer evaluation
3. **Researching** — Actively gathering information
4. **Application in Progress** — Grantee is preparing/submitting an application
5. **Funded** — Grant awarded
6. **Passed** — Decided not to fund
