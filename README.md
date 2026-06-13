# Dev Log Admin

> Development log unified management system with multi-project dashboard.

Git commit history, development log, project analysis data를 수집/통합하여 단일 대시보드에서 관리하는 시스템입니다. Legacy(SQLite) 시스템에서 PostgreSQL 기반 SaaS 플랫폼으로 전환 중입니다.

## Architecture

```
                    +-------------------+
                    |   Frontend        |
                    |   Next.js 16      |
                    |   :3000           |
                    +---------+---------+
                              |
               +--------------+--------------+
               |                             |
    +----------v----------+       +----------v-----------+
    |   Backend (v2)      |       |   Legacy (v1)        |
    |   FastAPI + async   |       |   FastAPI + SQLite    |
    |   :8200             |       |   :8100               |
    +----------+----------+       +----------+-----------+
               |                             |
    +----------v----------+       +----------v-----------+
    |   PostgreSQL 15+    |       |   SQLite              |
    |   :5432             |       |   legacy/devlog.db    |
    +---------------------+       +----------------------+
```

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI + SQLAlchemy 2.0 (async) | Python 3.11+ |
| Frontend | Next.js + TypeScript + shadcn/ui | Next.js 16, React 19 |
| Database | PostgreSQL (main), SQLite (legacy) | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 async + Alembic | - |
| Auth | JWT + GitHub OAuth | - |
| UI | Tailwind CSS 4 + shadcn/ui + Recharts | - |
| Legacy | FastAPI + SQLite + Vanilla JS | - |

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+ (npm)
- **PostgreSQL** 15+
- **Git**

## Quick Start

### 1. Clone & Install

```bash
git clone <repository-url>
cd dev-log-admin

# Install all dependencies (backend + frontend)
make install
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Backend environment
cp backend/.env.example backend/.env
```

`.env` 파일을 열어 다음 값을 설정합니다:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | No |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | No |

Secret key 생성:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb devlog

# Run Alembic migrations
make db-migrate

# (Optional) Initialize legacy SQLite & sync data
make db-init
make discover
```

### 4. Start Services

```bash
# Start all services (legacy + backend + frontend)
make start

# Or start without legacy
make start-no-legacy

# Check status
make status
```

### Access URLs

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| Backend API (Swagger) | http://localhost:8200/docs |
| Legacy API (Swagger) | http://localhost:8100/docs |

## Project Structure

```
dev-log-admin/
├── backend/                    # New backend (port 8200)
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/             # Legacy-compatible read-only API
│   │   │   └── v2/             # New API with auth (CRUD)
│   │   │       ├── auth.py     # Authentication endpoints
│   │   │       ├── projects.py # Project management
│   │   │       ├── teams.py    # Team management
│   │   │       ├── users.py    # User management
│   │   │       ├── github.py   # GitHub integration
│   │   │       └── webhooks.py # Webhook handlers
│   │   ├── core/               # Config, security, encryption
│   │   ├── db/                 # Database session (async)
│   │   ├── middleware/         # Auth middleware
│   │   ├── models/             # SQLAlchemy models (User, Project, Team, Commit)
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   └── services/           # Business logic layer
│   ├── migrations/             # Alembic migrations
│   ├── scripts/                # Utility scripts
│   ├── tests/                  # Test suite (pytest)
│   └── requirements.txt
│
├── frontend/                   # Next.js dashboard (port 3000)
│   └── src/
│       ├── app/                # App Router pages
│       │   ├── page.tsx        # Dashboard home
│       │   ├── analytics/      # Analytics page
│       │   ├── projects/       # Project list & detail ([slug])
│       │   └── settings/       # Settings page
│       ├── components/
│       │   ├── dashboard/      # Dashboard components (sidebar, stats, charts)
│       │   └── ui/             # shadcn/ui components
│       ├── hooks/              # Custom React hooks
│       ├── lib/                # API client, utilities
│       └── types/              # TypeScript type definitions
│
├── legacy/                     # Legacy SQLite system (port 8100)
│   ├── server.py               # FastAPI + SQLite API
│   ├── database.py             # SQLite schema
│   ├── sync.py                 # JSON -> SQLite sync
│   ├── auto-discover.py        # Project auto-discovery
│   ├── config.json             # Project registry
│   └── static/                 # Legacy frontend (vanilla JS)
│
├── scripts/                    # Operational scripts
│   ├── start.sh                # Start services
│   ├── stop.sh                 # Stop services
│   ├── status.sh               # Check status
│   ├── migrate.sh              # SQLite -> PostgreSQL migration
│   └── sync-legacy.sh          # Legacy data sync
│
├── tools/                      # Utility scripts
│   ├── batch-generate-json.py  # Batch JSON generation
│   ├── deep-analyze.py         # Deep project analysis
│   └── git-to-devlog.py        # Git history -> dev log
│
├── docs/                       # Documentation
│   ├── UPGRADE_PLAN.md         # SaaS upgrade roadmap
│   ├── BRANCH_STRATEGY.md      # Git branch strategy
│   └── CONTRIBUTING.md         # Contribution guide
│
├── Makefile                    # Unified commands
├── CLAUDE.md                   # Claude Code project config
└── .env.example                # Environment template
```

## Commands

### Service Management

| Command | Description |
|---------|-------------|
| `make start` | Start all services (legacy + backend + frontend) |
| `make start-no-legacy` | Start backend + frontend only |
| `make start-legacy` | Start legacy server only (port 8100) |
| `make start-backend` | Start backend only (port 8200) |
| `make start-frontend` | Start frontend only (port 3000) |
| `make stop` | Stop all services |
| `make status` | Check service status |

### Database

| Command | Description |
|---------|-------------|
| `make db-init` | Initialize legacy SQLite database |
| `make db-migrate` | Run Alembic migrations (PostgreSQL) |
| `make migrate-sqlite` | Migrate SQLite data to PostgreSQL |
| `make migrate-sqlite-dry` | Dry run: show what would be migrated |

### Data Sync

| Command | Description |
|---------|-------------|
| `make sync-legacy` | Sync JSON data to SQLite |
| `make discover` | Auto-discover projects and sync |

### Development

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make test-backend` | Run backend tests |
| `make test-frontend` | Run frontend tests |
| `make lint-backend` | Lint backend code (ruff) |
| `make lint-frontend` | Lint frontend code (eslint) |
| `make help` | Show all available commands |

## API Overview

### v1 (Legacy) - `/api/*`

- Read-only endpoints
- No authentication required
- Backward compatible with legacy frontend

### v2 (New) - `/api/v2/*`

- Full CRUD operations
- JWT authentication required
- Team-based access control (RBAC)

#### Authentication

```bash
# Register
curl -X POST http://localhost:8200/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8200/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Authenticated request
curl http://localhost:8200/api/v2/auth/me \
  -H "Authorization: Bearer <access_token>"
```

#### RBAC Roles

| Role | Permissions |
|------|-------------|
| **owner** | Full access, can delete team |
| **admin** | Manage members, projects |
| **member** | Read/write projects |
| **viewer** | Read-only access |

## Port Assignment

| Service | Port | Description |
|---------|------|-------------|
| Legacy SQLite API | 8100 | Will be removed after full migration |
| Backend (FastAPI) | 8200 | New v2 API |
| Frontend (Next.js) | 3000 | Dashboard |
| PostgreSQL | 5432 | Main database |

## Development

### Backend

```bash
cd backend

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8200

# Test
pytest tests/ -v
pytest --cov=app --cov-report=html

# Lint & Format
ruff check app/
black app/
mypy app/

# Database migration
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Frontend

```bash
cd frontend

# Install
npm install

# Development server
npm run dev

# Build
npm run build

# Lint
npm run lint
```

## Migration Guide (SQLite -> PostgreSQL)

Legacy SQLite 데이터를 PostgreSQL로 마이그레이션하는 방법:

```bash
# 1. PostgreSQL database 생성
createdb devlog

# 2. Alembic migration 실행
make db-migrate

# 3. Dry run으로 마이그레이션 대상 확인
make migrate-sqlite-dry

# 4. 실제 마이그레이션 실행
make migrate-sqlite
```

## Contributing

`docs/CONTRIBUTING.md`를 참조하세요.

### Branch Naming

```
feature/{issue-number}-{short-description}
fix/{issue-number}-{short-description}
hotfix/{issue-number}-{short-description}
```

### Commit Format

```
type(scope): subject

Co-Authored-By: Ph.D SNT Go. <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

## Roadmap

- [x] Phase 1: UI/UX redesign (Next.js + shadcn/ui)
- [x] Phase 2: Authentication & multi-user (JWT + OAuth)
- [ ] Phase 3: GitHub/GitLab deep integration
- [ ] Phase 4: Real-time collaboration
- [ ] Phase 5: Advanced analytics

## License

MIT
