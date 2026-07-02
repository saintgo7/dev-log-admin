<!-- dev-log-admin의 P1 우선순위 수정 계획을 기록하는 실행 문서 -->
# NEXT-STEPS — dev-log-admin

> 작성: 2026-07-02 (P1 production-safe pass). 검증된 사실만 기록한다.
> 브랜치 `claude/graphfix-2026-06-15`, 워킹트리 clean. 배경·전체 현황은 `STATUS.md` 참조.

## 이번 패스에서 검증한 현재 상태

| 항목 | 명령 | 결과 |
|------|------|------|
| 백엔드 테스트 | `cd backend && python3 -m pytest tests/` | ✅ **87 passed** (STATUS 시점 72 → 증가, 2026-07-02 재실행) |
| 프론트 lint | `cd frontend && npm run lint` | ⚠️ **1 error + 2 warnings** (아래 P1-1) |

- 백엔드 테스트는 SQLite in-memory 경로만 검증한다(실 PostgreSQL 미검증).
- `.gitignore`는 `.logs/` `.pids/` `*.db` 등 포함, 추가 필요 항목 없음. graphify-out/은 의도적으로 추적되는 그래프 산출물.

## P1 우선순위

### 1. 프론트엔드 lint 에러 1건 (render 동작 영향 → HELD)
- **위치**: `frontend/src/app/projects/[slug]/page.tsx:77`.
- **규칙**: `react-hooks/preserve-manual-memoization`.
- **원인(확인함)**: `useMemo`의 수동 의존성 `[commitsData?.commits, selectedTypes]`가 React Compiler가 추론한 의존성(`commitsData.commits`)과 불일치. Compiler가 최적화를 스킵한다.
- **조치안**: 의존성 배열을 Compiler 추론과 일치시키거나(`commitsData.commits` 접근 방식 통일), 필터 로직을 컴포넌트 밖으로 추출.
- **safe 여부**: **HELD** — 렌더 동작(메모이제이션 빈도)에 영향을 줄 수 있어 이 패스의 런타임-불변 원칙에 걸린다. 별도 검증 후 수정.
- **verify**: `npm run lint` 0 error + 필터 UI 수동 확인.

### 2. 프론트엔드 lint 경고 2건 (사소)
- **위치**: `frontend/src/components/theme-toggle.tsx:16` — 미사용 변수 `theme` (@typescript-eslint/no-unused-vars) 외 1건.
- **조치**: 미사용 변수 제거. 단 `theme`가 향후 사용 의도인지 확인 필요(제거 시 의미 변화 가능성) → 소규모지만 **문서화만**, 수정은 P1-1과 함께.
- **verify**: `npm run lint` 경고 0.

### 3. PostgreSQL 실연동·마이그레이션 검증 (미검증 → 리스크)
- **현상**: 테스트는 SQLite in-memory. 실 PostgreSQL 연결, Alembic 마이그레이션(`make db-migrate`), SQLite→PostgreSQL 이관(`make migrate-sqlite`) 미검증.
- **모델 이중 호환**: `backend/app/models/base.py`의 `GUID`/`JSONBType` `with_variant`로 두 DB 컴파일 지원(운영 DDL 불변, STATUS에서 검증).
- **조치**: `createdb devlog` → `make db-migrate` → `make migrate-sqlite-dry`/`make migrate-sqlite`.
- **주의(HELD)**: 마이그레이션·스키마·데이터 이관은 이 패스 금지 항목.
- **verify**: 마이그레이션 무오류, 행 수 일치.

### 4. 프론트엔드 테스트/빌드 게이트 부재
- **현상**: `frontend/package.json`에 `test` 스크립트 없음 → `make test-frontend`(=`npm test`) 실패. `npm run build` 미검증.
- **조치**: `test` 스크립트 추가하거나 빌드 검증으로 대체. `npm run build` 실행하여 통과 확인.
- **verify**: `npm run build` exit 0.

### 5. GitHub OAuth/webhook E2E (Phase 3, mock→real)
- **현상**: 코드 골격(`backend/app/api/v2/github.py`, `webhooks.py`, `webhook_service.py`) 존재·테스트 통과하나 실제 GitHub OAuth/webhook 엔드투엔드 미검증. 최근 `73730ac`에서 IDOR 차단 보안 수정 반영됨.
- **주의(HELD)**: OAuth/webhook 인증 경로는 이 패스 금지 항목. 시크릿(`backend/.env` GITHUB_WEBHOOK_SECRET) 미변경.
- **verify**: 실제 repo 웹훅 ping → 202, OAuth 콜백 → 세션 발급.

## Held for review (이 패스에서 수행하지 않음)
- 프론트 useMemo lint 에러 수정 (P1-1, 렌더 동작 영향)
- theme-toggle 미사용 변수 제거 (P1-2, P1-1과 함께)
- PostgreSQL 마이그레이션·데이터 이관 (P1-3)
- GitHub OAuth/webhook 통합 (P1-5)
