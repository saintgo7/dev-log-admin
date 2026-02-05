# Dev Log #002: Phase 2 - Authentication & Multi-user System

**Date**: 2026-02-05 23:40
**Author**: Ph.D SNT Go.
**Phase**: Backend Development - Phase 2

## Summary

Phase 2 인증 및 멀티유저 시스템의 백엔드 구현 완료. PostgreSQL 마이그레이션, JWT 인증, 팀 관리, RBAC 시스템 구축.

## Previous Session Review

#001에서 Dev Log Admin 초기 설정 완료. SQLite 기반 기본 API 구현.

## Changes Made

### Files Created

**Core Application Structure:**
- `backend/app/__init__.py`: 애플리케이션 패키지 초기화
- `backend/app/main.py`: FastAPI 애플리케이션 엔트리포인트
- `backend/app/core/config.py`: 환경 설정 관리 (Pydantic Settings)
- `backend/app/core/security.py`: JWT 토큰 생성/검증, 패스워드 해싱
- `backend/app/core/deps.py`: 공통 의존성 (team/project 권한 체크)

**Database:**
- `backend/app/db/session.py`: SQLAlchemy 2.0 async 세션 관리
- `backend/alembic.ini`: Alembic 설정
- `backend/migrations/env.py`: Alembic 환경 설정
- `backend/migrations/versions/20260205_001_initial_schema.py`: 초기 스키마
- `backend/migrations/versions/20260205_002_row_level_security.py`: RLS 정책

**Models (SQLAlchemy):**
- `backend/app/models/base.py`: 공통 믹스인 (UUID, Timestamp)
- `backend/app/models/user.py`: 사용자 모델
- `backend/app/models/team.py`: 팀, 팀멤버 모델
- `backend/app/models/project.py`: 프로젝트 모델
- `backend/app/models/commit.py`: 커밋 모델

**Schemas (Pydantic):**
- `backend/app/schemas/auth.py`: 인증 관련 스키마
- `backend/app/schemas/user.py`: 사용자 스키마
- `backend/app/schemas/team.py`: 팀 스키마
- `backend/app/schemas/project.py`: 프로젝트 스키마
- `backend/app/schemas/commit.py`: 커밋 스키마

**Services (Business Logic):**
- `backend/app/services/auth_service.py`: 인증 서비스
- `backend/app/services/user_service.py`: 사용자 서비스
- `backend/app/services/team_service.py`: 팀 서비스

**API Endpoints:**
- `backend/app/api/v1/router.py`: Legacy API (인증 불필요)
- `backend/app/api/v2/auth.py`: 인증 엔드포인트
- `backend/app/api/v2/users.py`: 사용자 엔드포인트
- `backend/app/api/v2/teams.py`: 팀 엔드포인트
- `backend/app/api/v2/projects.py`: 프로젝트 엔드포인트
- `backend/app/api/v2/router.py`: v2 라우터 통합

**Middleware:**
- `backend/app/middleware/auth.py`: JWT 인증 미들웨어

**Scripts:**
- `backend/scripts/migrate_sqlite_to_postgres.py`: SQLite -> PostgreSQL 마이그레이션

**Tests:**
- `backend/tests/conftest.py`: 테스트 픽스처
- `backend/tests/unit/test_security.py`: 보안 모듈 단위 테스트
- `backend/tests/integration/test_auth.py`: 인증 통합 테스트
- `backend/tests/integration/test_teams.py`: 팀 통합 테스트

**Configuration:**
- `backend/requirements.txt`: Python 의존성
- `backend/pyproject.toml`: 프로젝트 설정
- `backend/.env.example`: 환경 변수 예시
- `backend/README.md`: 백엔드 문서

## Technical Details

### Database Schema

```
users
├── id (UUID, PK)
├── email (unique)
├── name, avatar_url
├── hashed_password
├── auth_provider (local, github, google)
├── role (admin, member)
└── timestamps

teams
├── id (UUID, PK)
├── name, slug (unique)
├── plan (free, pro, enterprise)
└── timestamps

team_members
├── team_id (FK)
├── user_id (FK)
├── role (owner, admin, member, viewer)
└── timestamps

projects
├── id (UUID, PK)
├── slug (unique)
├── team_id (FK)
├── visibility (private, team, public)
└── timestamps

commits
├── id (INT, PK, autoincrement)
├── project_id (FK to UUID)
└── existing fields...
```

### API Structure

```
/api/v1/*          - Legacy API (no auth, read-only)
/api/v2/auth/*     - Authentication endpoints
/api/v2/users/*    - User management
/api/v2/teams/*    - Team management
/api/v2/projects/* - Project CRUD with auth
```

### RBAC Implementation

| Role | Team Access | Project Access |
|------|-------------|----------------|
| owner | Full control | Full control |
| admin | Manage members | Read/Write |
| member | Read-only | Read/Write |
| viewer | Read-only | Read-only |

### Row Level Security

PostgreSQL RLS policies ensure data isolation:
- Projects visible only to team members (or public)
- Commits follow project visibility
- Team members visible only to other members

### Authentication Flow

1. Register: `POST /api/v2/auth/register`
2. Login: `POST /api/v2/auth/login` -> JWT tokens
3. Refresh: `POST /api/v2/auth/refresh`
4. Access: Include `Authorization: Bearer <token>` header

## Key Decisions

1. **SQLAlchemy 2.0 Async**: 비동기 처리로 성능 최적화
2. **JWT + Refresh Token**: Stateless 인증 with 보안 강화
3. **UUID Primary Keys**: 분산 시스템 대비
4. **Commits ID 유지**: v1 API 호환성을 위해 Integer autoincrement 유지
5. **RLS at DB Level**: 애플리케이션 레벨 + DB 레벨 이중 보안

## Dependencies Added

```
fastapi>=0.109.0
sqlalchemy[asyncio]>=2.0.25
asyncpg>=0.29.0
alembic>=1.13.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic-settings>=2.1.0
```

## Next Steps

- [ ] PostgreSQL 데이터베이스 생성 및 마이그레이션 실행
- [ ] SQLite 데이터 PostgreSQL로 마이그레이션
- [ ] OAuth 프로바이더 설정 (GitHub, Google)
- [ ] Frontend NextAuth.js 연동
- [ ] E2E 테스트 추가

## Related

- Branch: `feature/phase2-postgres-migration`
- Previous: `001-2026-02-05-devlog-admin-initial-setup.md`
