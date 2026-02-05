# Contributing to Dev-Log Admin

## 🌳 Branch Strategy (Git Flow)

### Main Branches

```
main (production)
  └── develop (integration)
        ├── feature/* (new features)
        ├── bugfix/* (bug fixes)
        ├── hotfix/* (urgent fixes)
        └── release/* (release preparation)
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{phase}-{description}` | `feature/phase1-tailwind-ui` |
| Bugfix | `bugfix/{issue-number}-{description}` | `bugfix/123-fix-sync-error` |
| Hotfix | `hotfix/{issue-number}-{description}` | `hotfix/456-critical-bug` |
| Release | `release/v{version}` | `release/v2.0.0` |

### Workflow

```bash
# 1. Feature 시작
git checkout develop
git pull origin develop
git checkout -b feature/phase1-tailwind-ui

# 2. 작업 & 커밋
git add .
git commit -m "feat: add tailwind config"

# 3. Push & PR
git push -u origin feature/phase1-tailwind-ui
# GitHub에서 develop으로 PR 생성

# 4. 리뷰 & 머지 후
git checkout develop
git pull origin develop
git branch -d feature/phase1-tailwind-ui
```

---

## 📝 Commit Convention

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | 새 기능 | `feat(ui): add dark mode toggle` |
| `fix` | 버그 수정 | `fix(api): resolve sync timeout` |
| `docs` | 문서 변경 | `docs: update README` |
| `style` | 코드 포맷팅 | `style: format with prettier` |
| `refactor` | 코드 리팩토링 | `refactor(db): optimize query` |
| `perf` | 성능 개선 | `perf: add redis cache` |
| `test` | 테스트 추가 | `test: add unit tests` |
| `chore` | 빌드/설정 | `chore: update dependencies` |

### Scope

- `ui`: Frontend
- `api`: Backend API
- `db`: Database
- `auth`: Authentication
- `deploy`: Deployment
- `ci`: CI/CD

### Examples

```bash
feat(ui): add sidebar navigation with dark mode
fix(api): resolve GitHub webhook timeout issue
docs: add Phase 1 implementation guide
refactor(db): migrate SQLite to PostgreSQL
test(api): add integration tests for sync
```

---

## 🎯 Development Phases

### Phase 1: UI/UX (Current)
```bash
feature/phase1-tailwind-setup
feature/phase1-sidebar-layout
feature/phase1-dark-mode
feature/phase1-responsive-design
```

### Phase 2: Auth & Multi-user
```bash
feature/phase2-nextauth-setup
feature/phase2-user-management
feature/phase2-team-system
feature/phase2-rbac
```

### Phase 3: GitHub Integration
```bash
feature/phase3-github-oauth
feature/phase3-webhook-handler
feature/phase3-auto-sync
feature/phase3-issue-tracking
```

---

## ✅ PR Checklist

### Before Creating PR

- [ ] `git pull origin develop` (최신 상태 유지)
- [ ] 코드가 정상 작동함
- [ ] 로컬에서 테스트 완료
- [ ] Lint 에러 없음
- [ ] 커밋 메시지 규칙 준수

### PR Description

- [ ] 명확한 제목 (타입 포함)
- [ ] 변경 사항 요약
- [ ] 스크린샷 (UI 변경 시)
- [ ] 테스트 방법 설명

### After PR Creation

- [ ] CI 통과 확인
- [ ] 코드 리뷰 반영
- [ ] Conflicts 해결
- [ ] Squash & Merge

---

## 🔍 Code Review Guidelines

### Reviewer

- 24시간 내 리뷰
- 긍정적이고 건설적인 피드백
- Approve/Request Changes 명확히

### Author

- 리뷰 코멘트에 48시간 내 응답
- 변경 사항 명확히 설명
- 논의가 필요한 경우 이슈 생성

---

## 🚀 Release Process

### 1. Release Branch 생성

```bash
git checkout develop
git checkout -b release/v2.0.0
```

### 2. Version Bump

```bash
# package.json, version.py 등 업데이트
git commit -m "chore: bump version to 2.0.0"
```

### 3. Testing

```bash
# 전체 테스트 실행
npm test
pytest

# E2E 테스트
npm run test:e2e
```

### 4. Merge to Main

```bash
git checkout main
git merge --no-ff release/v2.0.0
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin main --tags
```

### 5. Merge back to Develop

```bash
git checkout develop
git merge --no-ff release/v2.0.0
git push origin develop
git branch -d release/v2.0.0
```

---

## 🐛 Hotfix Process

### 긴급 버그 수정

```bash
# main에서 hotfix 브랜치 생성
git checkout main
git checkout -b hotfix/critical-bug

# 수정 & 커밋
git commit -m "hotfix: fix critical authentication bug"

# main과 develop 둘 다 머지
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v2.0.1 -m "Hotfix 2.0.1"

git checkout develop
git merge --no-ff hotfix/critical-bug

# Push
git push origin main develop --tags
git branch -d hotfix/critical-bug
```

---

## 🛠️ Development Setup

### Prerequisites

```bash
Python 3.10+
Node.js 20+
PostgreSQL 15+ (Phase 2부터)
Redis (Phase 5부터)
```

### Local Setup

```bash
# Clone
git clone https://github.com/saintgo7/dev-log-admin.git
cd dev-log-admin

# Backend
pip install -r requirements.txt
python server.py

# Frontend (Phase 1부터)
npm install
npm run dev
```

### Environment Variables

```bash
# .env.local
DATABASE_URL=postgresql://localhost/devlog
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_secret
NEXTAUTH_SECRET=your_secret
```

---

## 📊 Project Structure

```
dev-log-admin/
├── .github/              # GitHub 설정
│   ├── workflows/        # CI/CD
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                 # 문서
│   ├── UPGRADE_PLAN.md
│   ├── CONTRIBUTING.md
│   └── dev-log/
├── backend/              # Python FastAPI (Phase 2부터 분리)
│   ├── api/
│   ├── models/
│   └── services/
├── frontend/             # Next.js (Phase 1부터)
│   ├── app/
│   ├── components/
│   └── lib/
├── static/               # 현재 프론트엔드 (Phase 1까지)
└── scripts/              # 유틸리티 스크립트
```

---

## 🎨 Code Style

### Python

```python
# Black formatter
black .

# isort
isort .

# flake8
flake8 .
```

### TypeScript

```typescript
// Prettier
npm run format

// ESLint
npm run lint
```

---

## 🧪 Testing

### Backend

```bash
pytest tests/
pytest --cov=. tests/
```

### Frontend

```bash
npm test
npm run test:watch
npm run test:coverage
```

---

## 📚 Resources

- [Upgrade Plan](./UPGRADE_PLAN.md)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Questions?** Open an issue or ask in discussions!
