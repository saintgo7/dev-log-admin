# Branch Strategy

## 🌳 Git Flow 다이어그램

```
main (v1.0.0) ────────────────────○ (v2.0.0) ──────────
                                  ╱
develop ──○──○──○──○──○──○──○──○─────○──○──○──────
         ╱    ╲  ╱  ╱  ╱  ╱  ╱
feature/phase1-ui  │  │  │  │
feature/phase1-dark   │  │  │
feature/phase2-auth ───┘  │  │
feature/phase2-rbac ──────┘  │
feature/phase3-github ───────┘
```

---

## 📋 브랜치 구조

### Permanent Branches (영구 브랜치)

| Branch | Purpose | Deploy To |
|--------|---------|-----------|
| `main` | Production 코드 | production.devlog-admin.com |
| `develop` | 통합/테스트 | dev.devlog-admin.com |

### Temporary Branches (임시 브랜치)

| Type | Pattern | Base | Merge To | Delete After |
|------|---------|------|----------|--------------|
| Feature | `feature/*` | develop | develop | Yes |
| Bugfix | `bugfix/*` | develop | develop | Yes |
| Release | `release/*` | develop | main + develop | Yes |
| Hotfix | `hotfix/*` | main | main + develop | Yes |

---

## 🚀 Phase별 브랜치 전략

### Phase 1: UI/UX Redesign

```bash
develop
  ├── feature/phase1-nextjs-setup
  ├── feature/phase1-tailwind-config
  ├── feature/phase1-sidebar-layout
  ├── feature/phase1-dark-mode
  ├── feature/phase1-responsive
  └── feature/phase1-charts
```

**병렬 개발:**
- UI 컴포넌트: `feature/phase1-*`
- 차트: `feature/phase1-charts`
- 다크모드: `feature/phase1-dark-mode`

**머지 순서:**
1. nextjs-setup (기반)
2. tailwind-config (스타일)
3. sidebar-layout (레이아웃)
4. 나머지 병렬 머지

### Phase 2: Auth & Multi-user

```bash
develop
  ├── feature/phase2-postgres-migration
  ├── feature/phase2-nextauth-setup
  ├── feature/phase2-user-model
  ├── feature/phase2-team-system
  └── feature/phase2-rbac
```

**순차 개발:**
1. postgres-migration (필수)
2. nextauth-setup (인증)
3. user-model → team-system → rbac

### Phase 3: GitHub Integration

```bash
develop
  ├── feature/phase3-github-oauth
  ├── feature/phase3-webhook-setup
  ├── feature/phase3-auto-sync
  └── feature/phase3-issue-tracking
```

---

## 📝 브랜치 명명 규칙

### Feature

```
feature/phase{N}-{description}
feature/phase1-dark-mode
feature/phase2-team-management
feature/add-search-filter
```

### Bugfix

```
bugfix/{issue-number}-{description}
bugfix/123-fix-sync-timeout
bugfix/456-resolve-login-error
```

### Hotfix

```
hotfix/{issue-number}-{description}
hotfix/789-critical-auth-bug
hotfix/urgent-database-fix
```

### Release

```
release/v{major}.{minor}.{patch}
release/v2.0.0
release/v2.1.0
```

---

## 🔄 Workflow Examples

### 새 기능 개발

```bash
# 1. develop에서 시작
git checkout develop
git pull origin develop

# 2. feature 브랜치 생성
git checkout -b feature/phase1-dark-mode

# 3. 개발 & 커밋
git add .
git commit -m "feat(ui): add dark mode toggle"

# 4. 정기적으로 develop 머지 (충돌 방지)
git fetch origin develop
git merge origin/develop

# 5. Push
git push -u origin feature/phase1-dark-mode

# 6. GitHub에서 PR 생성
# Base: develop
# Compare: feature/phase1-dark-mode

# 7. 리뷰 & 머지 후 브랜치 삭제
git checkout develop
git pull origin develop
git branch -d feature/phase1-dark-mode
git push origin --delete feature/phase1-dark-mode
```

### 버그 수정

```bash
# develop에서 bugfix 브랜치
git checkout develop
git checkout -b bugfix/123-fix-sync-error

# 수정 & 테스트
git commit -m "fix(api): resolve sync timeout issue"

# PR → develop
git push -u origin bugfix/123-fix-sync-error
```

### 릴리즈

```bash
# 1. Release 브랜치 생성
git checkout develop
git checkout -b release/v2.0.0

# 2. 버전 업데이트
# package.json, __version__.py 수정
git commit -m "chore: bump version to 2.0.0"

# 3. 최종 테스트 & 버그 수정
git commit -m "fix: last minute bug fixes"

# 4. main으로 머지 & 태그
git checkout main
git merge --no-ff release/v2.0.0
git tag -a v2.0.0 -m "Release version 2.0.0"

# 5. develop으로 백머지
git checkout develop
git merge --no-ff release/v2.0.0

# 6. Push
git push origin main develop --tags

# 7. 브랜치 삭제
git branch -d release/v2.0.0
git push origin --delete release/v2.0.0
```

### 긴급 핫픽스

```bash
# 1. main에서 hotfix 브랜치
git checkout main
git checkout -b hotfix/critical-security-bug

# 2. 수정
git commit -m "hotfix: patch critical security vulnerability"

# 3. main 머지 & 태그
git checkout main
git merge --no-ff hotfix/critical-security-bug
git tag -a v2.0.1 -m "Hotfix 2.0.1"

# 4. develop 머지
git checkout develop
git merge --no-ff hotfix/critical-security-bug

# 5. Push & 배포
git push origin main develop --tags

# 6. 브랜치 삭제
git branch -d hotfix/critical-security-bug
```

---

## 🔍 PR 체크리스트

### Feature PR

```markdown
## Phase 1: Dark Mode Implementation

### Changes
- Added dark mode toggle component
- Updated color tokens for dark theme
- Persisted theme preference in localStorage

### Screenshots
[Before/After 스크린샷]

### Testing
- [ ] Light mode works
- [ ] Dark mode works
- [ ] Theme persists on refresh
- [ ] Responsive on mobile

### Checklist
- [x] Code works locally
- [x] Tests added
- [x] No breaking changes
- [x] Docs updated
```

### Bugfix PR

```markdown
## Fix: Sync Timeout Issue (#123)

### Problem
API sync fails with timeout after 30 seconds on large repos

### Solution
- Increased timeout to 60s
- Added retry logic
- Improved error messages

### Testing
Tested with:
- Small repo (10 commits) ✅
- Large repo (1000 commits) ✅

### Related
Closes #123
```

---

## 🚦 Branch Protection Rules

### main

```
✅ Require pull request reviews (2 approvals)
✅ Require status checks to pass
✅ Require branches to be up to date
✅ Include administrators
✅ Require signed commits
```

### develop

```
✅ Require pull request reviews (1 approval)
✅ Require status checks to pass
⬜ Require branches to be up to date (optional)
```

---

## 📊 Current Status

| Phase | Branch | Status | Progress |
|-------|--------|--------|----------|
| Phase 1 | `feature/phase1-*` | 🟡 In Progress | 0% |
| Phase 2 | - | ⬜ Not Started | 0% |
| Phase 3 | - | ⬜ Not Started | 0% |

---

## 🎯 Next Steps

1. ✅ Create `develop` branch
2. ✅ Setup branch protection rules
3. ✅ Create PR template
4. ⬜ Create first feature branch: `feature/phase1-nextjs-setup`
5. ⬜ Setup CI/CD workflows

---

**Ready to start Phase 1!** 🚀
