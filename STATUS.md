# STATUS — dev-log-admin

> 자동 포트폴리오 스윕(claude/sweep-2026-06-13)에서 생성/갱신한 현황 문서. 검증된 사실만 기록한다.

## English Summary

`dev-log-admin` is a development-log unified management system being migrated from a legacy
SQLite + vanilla-JS stack to a Next.js 16 frontend + FastAPI (async SQLAlchemy 2.0) backend
on PostgreSQL, with JWT auth and GitHub OAuth/webhook integration.

- **Backend tests now fully pass: 72 passed, 0 failed** (was 32 passed / 40 errors before this sweep).
- Two fixes were applied during the sweep:
  1. **PostgreSQL-only column types broke the SQLite test database.** Models declared
     `postgresql.UUID` / `JSONB` directly, which SQLite cannot compile, so every integration
     test failed at `Base.metadata.create_all` (`UnsupportedCompilationError: can't render
     element of type UUID`). Fixed by wrapping the types with SQLAlchemy `with_variant`
     (`GUID = UUID(as_uuid=False).with_variant(CHAR(36), "sqlite")`, `JSONBType = JSONB().with_variant(JSON(), "sqlite")`)
     in `app/models/base.py` and using them across the model files. **Production PostgreSQL DDL
     is unchanged** (verified: `users`/`github_repositories` still render `UUID`, `webhook_events`
     still renders `JSONB`).
  2. **A webhook test patched the wrong object.** `test_github_webhook_ping_event` used
     `patch("app.core.config.settings")`, but the service captured the `settings` instance at
     import time, so the patch never reached it; the real secret in `backend/.env` was used and
     the test got 401 instead of 202. Fixed by `patch.object(settings, "GITHUB_WEBHOOK_SECRET", ...)`.
- Frontend: `npm run lint` reports **1 error + 2 warnings** (see below). Not fixed — pre-existing,
  unrelated to this sweep, and touches render behavior. Documented as remaining work.

## 프로젝트 목적

Git 커밋 히스토리·개발 로그·프로젝트 분석 데이터를 수집/통합하여 단일 대시보드에서 관리하는 시스템이다.
개인 도구(레거시 SQLite)에서 멀티유저 SaaS 플랫폼(PostgreSQL)으로 전환 중이다.

| 구성 | 기술 | 포트 |
|------|------|------|
| Backend (v2) | FastAPI + SQLAlchemy 2.0 async + Alembic | 8200 |
| Frontend | Next.js 16 + TypeScript + shadcn/ui | 3000 |
| Legacy (v1) | FastAPI + SQLite + Vanilla JS | 8100 |
| DB | PostgreSQL 15+ (main), SQLite (legacy) | 5432 |
| Auth | JWT + GitHub OAuth + Webhook | - |

## 현재 상태 (검증된 사실)

### 동작하는 것
- **백엔드 테스트 72개 전부 통과** (`cd backend && python3 -m pytest tests/`). 이번 스윕 전에는
  32 passed / 40 errors 였다. 단위 테스트(security, github)와 통합 테스트(auth, teams, github_api) 모두 포함된다.
- 백엔드 의존성(fastapi, sqlalchemy 2.0.25, aiosqlite 0.21, pytest)이 로컬에 이미 설치되어 즉시 테스트 가능하다.
- 모델 정의가 PostgreSQL과 SQLite 양쪽에서 컴파일된다(아래 수정 내역 참조). 운영 PostgreSQL DDL은 변하지 않았다(검증함).
- 프로젝트 구조 정리(WIP)가 거의 마무리되었다. 레거시 파일은 `legacy/`, 유틸은 `tools/`, 운영 스크립트는 `scripts/`로 이동했고
  포트가 8100→8200으로 일관되게 갱신되었다(`config.py`, `.env.example`, `frontend/src/lib/api.ts`, CORS 등).

### 동작하지 않는 것 / 미해결
- **프론트엔드 lint 에러 1건**: `frontend/src/app/projects/[slug]/page.tsx:77` —
  `react-hooks/preserve-manual-memoization`. React Compiler가 `useMemo`의 수동 메모이제이션을 보존하지 못한다는
  에러다. 렌더링 동작에 영향을 줄 수 있어 이번 스윕에서는 수정하지 않고 문서화만 했다.
- **프론트엔드 lint 경고 2건**: `theme-toggle.tsx:16` 미사용 변수 `theme` 등.
- **프론트엔드 테스트 스크립트 부재**: `frontend/package.json`에 `test` 스크립트가 없어 `make test-frontend`(=`npm test`)는 실패한다(미검증 영역).
- **PostgreSQL 실연동/마이그레이션 미검증**: 테스트는 SQLite in-memory로만 돌렸다. 실제 PostgreSQL 연결,
  Alembic 마이그레이션(`make db-migrate`), SQLite→PostgreSQL 데이터 이관(`make migrate-sqlite`)은 이번 스윕에서 검증하지 않았다(unverified).
- **프론트엔드 `npm run build` 미실행**: 시간 박스 때문에 lint만 돌렸다. 빌드 통과 여부는 unverified.

## 이번 스윕에서 변경한 파일

- `backend/app/models/base.py` — `GUID` / `JSONBType` variant 타입 정의, 믹스인 PK에 `GUID` 적용.
- `backend/app/models/{team,project,commit,github}.py` — `postgresql.UUID`/`JSONB` 직접 사용을 `GUID`/`JSONBType`로 교체.
- `backend/tests/integration/test_github_api.py` — webhook ping 테스트의 patch 대상을 `patch.object(settings, ...)`로 수정 + `settings` 임포트 추가.
- `STATUS.md` — 본 문서 신규 작성.

> 위 외의 변경분은 스윕 이전 WIP(파일 재배치 rename, 포트 8100→8200 갱신, README 확장, QUICK-START.md·start/stop/status.sh 삭제)이며
> 이번 체크포인트 커밋에 함께 포함되었다.

## 완성까지 남은 구체적 단계

1. 프론트엔드 lint 에러 해결: `projects/[slug]/page.tsx`의 `useMemo` 의존성 배열을 React Compiler가 추론한 것과 맞추거나
   해당 라인 규칙을 의도적으로 처리한다 → verify: `npm run lint` 통과(0 error).
2. 프론트엔드 테스트 도입 여부 결정: 테스트가 없으면 `make test-frontend`를 빌드 검증으로 대체하거나 `package.json`에 `test` 스크립트 추가.
3. PostgreSQL 실연동 검증: `createdb devlog` → `make db-migrate` → `make migrate-sqlite-dry`/`make migrate-sqlite` 순으로 실행 → verify: 마이그레이션 무오류, 행 수 일치.
4. 프론트엔드 `npm run build` 실행 → verify: 빌드 성공.
5. Roadmap Phase 3(GitHub/GitLab deep integration) 잔여 작업 — 코드 골격(`github.py`, `webhooks.py`, `webhook_service.py`)은 존재하고 테스트도 통과하나, 실제 GitHub OAuth/webhook 엔드투엔드는 미검증.

## 책/논문 가능성 (낮음, 엔지니어링 케이스 스터디용)

소프트웨어 도구 프로젝트라 학술 논문 소재로는 약하다. 다만 다음 두 주제는 짧은 기술 블로그/사내 케이스 스터디로 쓸 만한 1차 자료가 이미 있다.

- **레거시(SQLite)→SaaS(PostgreSQL) 점진적 마이그레이션 패턴**: v1/v2 API 병행 운영, `with_variant`로 단일 모델을 두 DB에서 테스트하는 기법.
  자료: `docs/UPGRADE_PLAN.md`, `backend/app/api/v1`·`v2`, `backend/scripts/migrate_sqlite_to_postgres.py`, 본 스윕의 `base.py` 수정.
- **멀티 에이전트 병렬 개발 회고**: `docs/dev-log/004-2026-02-06-multi-agent-parallel-development.md`에 실제 진행 기록이 있다.

### 개요 초안 (기술 케이스 스터디)
1. 배경 — 개인 dev-log 도구의 한계와 SaaS 전환 동기 (자료: UPGRADE_PLAN.md, dev-log/001~002)
2. 아키텍처 — v1/v2 병행, 포트 분리, async SQLAlchemy (자료: README Architecture, CLAUDE.md)
3. 데이터 계층 이중 호환 — PostgreSQL UUID/JSONB를 SQLite 테스트와 공존시키기 (자료: base.py `with_variant`)
4. 인증·RBAC·GitHub 연동 설계 (자료: api/v2/auth.py·teams.py·github.py, docs/phase3)
5. 테스트 전략과 함정 — settings 싱글톤 patch 함정 등 (자료: 본 스윕 webhook 테스트 수정)
6. 회고 — 멀티 에이전트 병렬 개발 (자료: dev-log/004)
</content>
</invoke>
