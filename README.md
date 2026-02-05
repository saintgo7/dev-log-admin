# Dev Log Admin - SQLite Backend

개발 로그 통합 관리 시스템

## 구조

```
dev-log-admin/
├── database.py          # SQLite 스키마
├── sync.py              # JSON → SQLite 동기화
├── server.py            # FastAPI 서버
├── config.json          # 프로젝트 설정
├── devlog.db            # SQLite 데이터베이스 (생성됨)
└── static/              # 프론트엔드
    ├── index.html       # 대시보드
    ├── search.html      # 검색
    ├── app.js           # Dashboard JavaScript
    ├── search.js        # Search JavaScript
    └── styles.css       # 스타일
```

## 설치

```bash
pip install fastapi uvicorn
```

## 실행 방법

### 1. 데이터베이스 초기화

```bash
cd ~/dev-log-admin
python database.py
```

### 2. 데이터 동기화

```bash
python sync.py
```

### 3. 서버 실행

```bash
python server.py
```

서버가 실행되면 다음 주소로 접속:
- 대시보드: http://localhost:8100
- API 문서: http://localhost:8100/docs

## 프로젝트 추가

### 자동 스캔 (권장)

`/Users/saint/01_DEV` 디렉토리를 자동으로 스캔하여 dev-log가 있는 프로젝트를 찾습니다:

```bash
python auto-discover.py --yes
python sync.py
```

**자동 감지 기능:**
- dev-logs.json 파일 존재 여부 확인
- Git remote URL 추출
- 기술 스택 자동 감지 (package.json, go.mod, requirements.txt 등)
- config.json 자동 업데이트

### 수동 추가

`config.json` 파일에 새 프로젝트 추가:

```json
{
  "projects": [
    {
      "slug": "project-slug",
      "name": "Project Name",
      "description": "프로젝트 설명",
      "repository_url": "https://github.com/...",
      "tech_stack": ["Python", "FastAPI"],
      "json_path": "~/path/to/dev-logs.json",
      "html_url": "file:///path/to/index.html"
    }
  ]
}
```

그 다음 동기화:

```bash
python sync.py
```

## API 엔드포인트

- `GET /api/projects` - 프로젝트 목록
- `GET /api/projects/{slug}` - 프로젝트 상세
- `GET /api/projects/{slug}/commits` - 프로젝트 커밋 목록
- `GET /api/commits/{id}` - 커밋 상세
- `GET /api/search?q={query}` - 통합 검색
- `GET /api/stats/overview` - 전체 통계
- `GET /api/stats/timeline?days=30` - 타임라인 통계
- `GET /health` - 헬스 체크

## 자동 동기화 (cron)

매 10분마다 자동 동기화:

```bash
crontab -e
```

다음 추가:

```
*/10 * * * * cd ~/dev-log-admin && /usr/local/bin/python3 sync.py >> sync.log 2>&1
```

## 기술 스택

- Backend: FastAPI, SQLite
- Frontend: Vanilla JavaScript, CSS
- 총 코드량: ~1000줄

## 특징

- SQLite 사용으로 가벼움
- 빠른 검색 (인덱스 활용)
- 복잡한 쿼리 지원
- 실시간 통계
- 반응형 디자인
