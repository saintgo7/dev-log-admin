# Dev Log #001: Dev-Log Admin 시스템 구축

**Date**: 2026-02-05
**Author**: Ph.D SNT Go.
**Type**: feat

## Summary

전체 프로젝트의 개발 로그를 통합 관리하는 Admin 시스템 구축 완료. 20개 프로젝트, 348개 커밋을 통합하여 단일 대시보드에서 관리 가능하도록 구현.

## Changes Made

### Files Created

**Python Scripts:**
- `auto-discover.py`: 프로젝트 자동 검색 및 기술 스택 감지
- `deep-analyze.py`: Git 저장소 심층 분석 및 활동 점수 계산
- `git-to-devlog.py`: Git 커밋 히스토리를 dev-logs.json으로 변환
- `batch-generate-json.py`: Markdown 개발 로그를 JSON으로 변환
- `install-html-generators.py`: HTML 생성 스크립트 일괄 배포
- `generate-html-only.py`: HTML만 재생성 (parse 스킵)
- `sync.py`: dev-logs.json을 SQLite DB에 동기화
- `database.py`: 데이터베이스 스키마 정의
- `server.py`: FastAPI 백엔드 서버

**Configuration:**
- `config.json`: 20개 프로젝트 설정 (slug, name, tech_stack, paths)

**Frontend:**
- `static/index.html`: 메인 대시보드
- `static/app.js`: 프론트엔드 로직
- `static/styles.css`: 스타일시트

**Database:**
- `devlog.db`: SQLite 데이터베이스 (projects, commits 테이블)

### Key Features Implemented

1. **자동 프로젝트 검색**
   - `/Users/saint/01_DEV` 전체 스캔
   - package.json, go.mod, requirements.txt 등으로 기술 스택 자동 감지
   - Git 원격 저장소 URL 자동 추출

2. **Git 히스토리 변환**
   - 최근 100개 커밋 자동 추출
   - Conventional Commits 형식 파싱 (feat, fix, refactor 등)
   - 한글 키워드 매칭 ('추가'->feat, '수정'->fix)
   - 커밋 통계 자동 계산 (files_changed, lines_added/deleted)

3. **Markdown 변환**
   - 기존 dev-log/*.md 파일을 JSON으로 변환
   - 파일명 패턴 파싱: `NN-YYYY-MM-DD-HHMM-description.md`
   - 메타데이터 추출 (Author, Date, Type, Files Changed)

4. **HTML 칸반보드 생성**
   - index.html: 메인 대시보드
   - timeline.html: 시간순 타임라인
   - heatmap.html: 활동 히트맵
   - stats.html: 통계 차트
   - files.html: 파일 변경 히스토리
   - commit-size.html: 커밋 크기 분석
   - time-analysis.html: 시간대별 분석
   - deployment.html: 배포 히스토리

5. **Admin 대시보드**
   - FastAPI + SQLite 백엔드
   - 프로젝트 목록 및 통계
   - 커밋 타입별 분포 차트
   - 최근 활동 로그
   - 프로젝트별 상세 페이지

6. **통합 기능**
   - **View Details**: 프로젝트 상세 정보 및 커밋 목록
   - **Open HTML**: 프로젝트별 HTML 칸반보드 열기
   - **Terminal**: iTerm으로 프로젝트 폴더 바로가기

## Technical Details

### Architecture

```
dev-log-admin/
├── Python Scripts
│   ├── auto-discover.py    # 프로젝트 검색
│   ├── deep-analyze.py     # Git 분석
│   ├── git-to-devlog.py    # Git → JSON
│   ├── batch-generate-json.py  # MD → JSON
│   ├── install-html-generators.py  # HTML 배포
│   └── sync.py             # JSON → DB
├── Backend
│   ├── server.py           # FastAPI 서버
│   └── database.py         # DB 스키마
├── Frontend
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── styles.css
├── Data
│   ├── config.json         # 프로젝트 설정
│   └── devlog.db          # SQLite DB
└── docs/dev-log/          # 개발 로그
```

### Database Schema

**projects 테이블:**
- id, slug, name, description
- repository_url, tech_stack, html_url
- total_commits, last_synced_at
- created_at, updated_at

**commits 테이블:**
- id, project_id, log_number, commit_hash
- type, title, author_name, author_email
- date, files_changed, lines_added, lines_deleted
- full_content
- created_at

### API Endpoints

- `GET /api/projects`: 전체 프로젝트 목록
- `GET /api/projects/{slug}`: 프로젝트 상세 정보
- `GET /api/projects/{slug}/commits`: 프로젝트별 커밋 목록
- `GET /api/projects/{slug}/open`: HTML 칸반보드 열기
- `GET /api/projects/{slug}/terminal`: iTerm으로 폴더 열기
- `GET /api/stats/overview`: 통합 통계
- `GET /api/stats/timeline`: 타임라인 데이터
- `GET /health`: 헬스 체크

### Activity Scoring Algorithm

```python
score = min(total_commits / 10, 50)  # 최대 50점
score += recent_commits * 2          # 최근 30일 커밋당 2점
if days_since_last_commit < 7:  score += 30
elif days_since_last_commit < 30: score += 20
elif days_since_last_commit < 90: score += 10
```

## Statistics

### Projects Integrated

| Category | Count |
|----------|-------|
| Total Projects | 20 |
| Git-generated | 6 (174 commits) |
| Markdown-converted | 9 (174 commits) |
| Total Commits | 348 |

### Top Projects by Commits

1. WebErpMes-v2: 100 commits
2. app-passport-reserve: 44 commits
3. 26-web-skyair-TS: 39 commits
4. web-music-heartlib: 31 commits
5. app-hospital-yoyang: 29 commits

### Commit Types Distribution

- feat: 149 (42.8%)
- fix: 78 (22.4%)
- docs: 52 (14.9%)
- refactor: 35 (10.1%)
- chore: 18 (5.2%)
- test: 8 (2.3%)
- ci: 5 (1.4%)
- perf: 3 (0.9%)

### Tech Stack Coverage

- Node.js/JavaScript: 9 projects
- Python: 6 projects
- Go: 3 projects
- PHP: 1 project
- Docker: 11 projects
- PostgreSQL: 9 projects
- Redis: 8 projects
- React/Next.js: 7 projects

## Issues Resolved

### Issue 1: parse-devlog.py 빈 JSON 생성

**Problem**: install-html-generators.py가 update-html.sh를 실행하면서 parse-devlog.py가 빈 JSON을 생성

**Solution**:
- generate-html-only.py 생성 (parse-devlog.py 스킵)
- git-to-devlog.py로 데이터 재생성 후 HTML만 업데이트

### Issue 2: sqlite3 라이브러리 오류

**Problem**: `dyld: Library not loaded: libtinfow.6.dylib`

**Solution**: Python으로 직접 sqlite3 접근

### Issue 3: iTerm AppleScript 타임아웃

**Problem**: iTerm AppleScript가 타임아웃 발생

**Solution**:
- TimeoutExpired 예외 처리
- `open -a iTerm <directory>` 명령으로 단순화

### Issue 4: 터미널이 홈 디렉토리로 이동

**Problem**: `write text` 명령이 실행되지 않음 (엔터 누르지 않음)

**Solution**: `open -a iTerm <directory>` 사용

## Test Results

- 20개 프로젝트 HTML 생성: ✅
- 348개 커밋 DB 동기화: ✅
- Open HTML 버튼: ✅
- Terminal 버튼: ✅
- 대시보드 로딩: ✅

## Performance

- 프로젝트 자동 검색: ~10초 (56개 디렉토리)
- Git 히스토리 추출: ~5초/프로젝트 (100 commits)
- HTML 생성: ~2초/프로젝트
- DB 동기화: ~1초 (348 commits)
- 대시보드 로딩: <500ms

## Deployment

### Server Start

```bash
cd ~/dev-log-admin
python3 server.py
```

**URL**: http://localhost:8100

### Process Running

```
python3 server.py (PID: 5915)
Port: 8100
Status: Running
```

## Next Steps

- [ ] 프로젝트 검색 기능 추가
- [ ] 커밋 필터링 (날짜, 타입, 작성자)
- [ ] 대시보드 차트 개선
- [ ] 프로젝트별 통계 상세 페이지
- [ ] 자동 동기화 (cron job)
- [ ] 원격 Git 저장소 연동
- [ ] GitHub API 통합
- [ ] 배포 자동화

## Related

- Repository: (to be created)
- Dashboard: http://localhost:8100
- Projects: 20 integrated

---

**Co-Authored-By**: Claude Sonnet 4.5 <noreply@anthropic.com>
