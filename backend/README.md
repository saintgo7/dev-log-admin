# Dev Log Admin Backend - Phase 2

Authentication & Multi-user System for Dev Log Admin.

## Features

- **PostgreSQL Database** with SQLAlchemy 2.0 async
- **JWT Authentication** with access/refresh tokens
- **Multi-user Support** with teams and RBAC
- **API Versioning**: v1 (legacy) and v2 (new)
- **Row Level Security** for data isolation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip or poetry

### Setup

1. **Create virtual environment**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Create PostgreSQL database**

```bash
createdb devlog
```

5. **Run migrations**

```bash
cd backend
alembic upgrade head
```

6. **Migrate data from SQLite (optional)**

```bash
python scripts/migrate_sqlite_to_postgres.py
```

7. **Run server**

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

## API Documentation

- **Swagger UI**: http://localhost:8100/docs
- **ReDoc**: http://localhost:8100/redoc

### API Versions

#### v1 (Legacy) - `/api/*`
- Read-only endpoints
- No authentication required
- Backward compatible with existing frontend

#### v2 (New) - `/api/v2/*`
- Full CRUD operations
- JWT authentication required
- Team-based access control

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/          # Legacy API
│   │   └── v2/          # New API with auth
│   ├── core/            # Config, security, deps
│   ├── db/              # Database session
│   ├── middleware/      # Auth middleware
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── migrations/          # Alembic migrations
├── scripts/             # Utility scripts
└── tests/               # Test suite
```

## Authentication

### Register

```bash
curl -X POST http://localhost:8100/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Login

```bash
curl -X POST http://localhost:8100/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Use Token

```bash
curl http://localhost:8100/api/v2/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Team Management

### Create Team

```bash
curl -X POST http://localhost:8100/api/v2/teams \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Team", "slug": "my-team"}'
```

### Add Member

```bash
curl -X POST http://localhost:8100/api/v2/teams/{team_id}/members \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email": "member@example.com", "role": "member"}'
```

## RBAC Roles

| Role | Permissions |
|------|-------------|
| **owner** | Full access, can delete team |
| **admin** | Manage members, projects |
| **member** | Read/write projects |
| **viewer** | Read-only access |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_auth.py -v
```

## Development

### Code Formatting

```bash
black app/
ruff check app/ --fix
```

### Type Checking

```bash
mypy app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://localhost/devlog` |
| `JWT_SECRET` | Secret key for JWT | Required |
| `JWT_EXPIRATION_HOURS` | Access token expiry | `24` |
| `DEBUG` | Enable debug mode | `false` |

## License

MIT
