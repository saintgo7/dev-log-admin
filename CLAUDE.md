# Dev Log Admin - Claude Code Project Config

## Project Overview

**Purpose**: Development log unified management system (v2)
**Status**: Active Development
**Author**: Ph.D SNT Go.

---

## Tech Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Legacy API | FastAPI + SQLite | 8100 |
| Backend | FastAPI + PostgreSQL (async) | 8200 |
| Frontend | Next.js 14 + TypeScript | 3000 |
| Database | PostgreSQL 15+, SQLite (legacy) | 5432 |
| ORM | SQLAlchemy 2.0 (async) | - |
| Migration | Alembic | - |
| Auth | JWT + GitHub OAuth | - |

---

## Project Structure

```text
dev-log-admin/
├── legacy/                   # Legacy SQLite system (port 8100)
│   ├── server.py             # FastAPI + SQLite API
│   ├── database.py           # SQLite schema
│   ├── sync.py               # JSON -> SQLite sync
│   ├── auto-discover.py      # Project auto-discovery
│   ├── config.json           # Project registry
│   ├── devlog.db             # SQLite database
│   └── static/               # Legacy frontend (vanilla JS)
│
├── backend/                  # New backend (port 8200)
│   ├── app/
│   │   ├── api/              # API routes (v2)
│   │   ├── core/             # Config, security, database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── migrations/           # Alembic migrations
│   ├── scripts/              # Migration scripts
│   └── tests/
│
├── frontend/                 # Next.js dashboard (port 3000)
│   └── src/
│       ├── app/              # App router pages
│       ├── components/       # React components
│       ├── lib/              # API client, utilities
│       └── types/            # TypeScript types
│
├── scripts/                  # Operational scripts
│   ├── start.sh              # Start services
│   ├── stop.sh               # Stop services
│   ├── status.sh             # Check status
│   ├── migrate.sh            # SQLite -> PostgreSQL
│   └── sync-legacy.sh        # Legacy data sync
│
├── tools/                    # Utility scripts
├── docs/                     # Documentation
├── Makefile                  # Unified commands
└── .env.example              # Environment template
```

---

## Commands

```bash
# Service management
make start              # Start all (legacy + backend + frontend)
make start-no-legacy    # Start without legacy
make stop               # Stop all
make status             # Check status

# Database
make db-init            # Initialize SQLite
make db-migrate         # Run Alembic migrations
make migrate-sqlite     # SQLite -> PostgreSQL migration

# Data sync
make sync-legacy        # Sync JSON -> SQLite
make discover           # Auto-discover + sync

# Development
make test-backend       # Run backend tests
make lint-backend       # Lint backend
make install            # Install all dependencies
```

---

## Port Assignment

| Service | Port | Description |
|---------|------|-------------|
| Legacy SQLite API | 8100 | Will be removed after migration |
| Backend (FastAPI) | 8200 | New v2 API |
| Frontend (Next.js) | 3000 | Dashboard |
| PostgreSQL | 5432 | Main database |

---

## Environment Variables

See `.env.example` for full list. Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Application secret |
| `JWT_SECRET` | JWT signing secret |
| `GITHUB_CLIENT_ID` | GitHub OAuth (optional) |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth (optional) |

---

## Coding Conventions

### Backend (Python)
- Async/await for all DB operations
- Pydantic v2 schemas for validation
- SQLAlchemy 2.0 async style
- UUID primary keys in PostgreSQL

### Frontend (TypeScript)
- Next.js App Router
- shadcn/ui components
- TypeScript strict mode
- API client in `src/lib/api.ts`

---

## Prohibited

- Direct commits to main without PR
- Hardcoded secrets or API keys
- Bypassing type checks
- Skipping tests for business logic
