# Dev Log Admin - Quick Start Guide

## 빠른 시작

### 1. 명령어로 실행 (권장)

터미널 재시작 후 어디서든 사용 가능:

```bash
# 서버 시작 및 브라우저 열기
devlog-admin

# 서버 중지
devlog-stop

# 상태 확인
devlog-status

# 데이터 동기화
devlog-sync

# 로그 보기
devlog-logs
```

### 2. 스크립트로 실행

```bash
# 시작
~/dev-log-admin/start.sh

# 중지
~/dev-log-admin/stop.sh

# 상태 확인
~/dev-log-admin/status.sh
```

---

## 상세 사용법

### 서버 시작

```bash
devlog-admin
```

**동작**:
1. 서버가 이미 실행 중인지 확인
2. 실행 중이면 브라우저만 열기
3. 실행 중이 아니면 서버 시작 후 브라우저 열기

**출력**:
```
==========================================
📊 Dev Log Admin - Starting...
==========================================

🚀 Starting server...
⏳ Waiting for server to start...
✅ Server started successfully (PID: 12345)

==========================================
📊 Dev Log Admin Dashboard
==========================================

🌐 URL: http://localhost:8100
📖 API Docs: http://localhost:8100/docs
📝 Logs: ~/dev-log-admin/server.log
```

### 서버 중지

```bash
devlog-stop
```

**동작**:
1. PID 파일에서 프로세스 ID 읽기
2. SIGTERM으로 graceful shutdown 시도
3. 10초 후에도 종료되지 않으면 SIGKILL

### 상태 확인

```bash
devlog-status
```

**출력**:
```
==========================================
📊 Dev Log Admin - Status
==========================================

✅ Server is running
   PID: 12345
   URL: http://localhost:8100
   Memory: 37.3 MB
   Started: 2026년 2월 5일 19시 25분

📝 Recent logs (last 5 lines):
----------------------------------------
[최근 로그 5줄 표시]

📊 Statistics:
   Projects: 3
   Commits: 37
```

### 데이터 동기화

```bash
devlog-sync
```

**동작**:
- config.json의 모든 프로젝트 읽기
- 각 프로젝트의 dev-logs.json 파싱
- SQLite 데이터베이스 업데이트

**출력**:
```
============================================================
🔄 Syncing dev-logs to SQLite
============================================================

✅ [OK] PamOut Workstation Manager: 17 commits synced
✅ [OK] Fire Abada KR v2: 19 commits synced
✅ [OK] Dev Log System: 1 commits synced

============================================================
✅ Sync complete: 3 projects, 37 commits
============================================================
```

### 로그 실시간 보기

```bash
devlog-logs
```

Ctrl+C로 종료

---

## 자동 시작 설정 (선택)

### macOS - launchd

1. plist 파일 생성:

```bash
cat > ~/Library/LaunchAgents/com.devlog.admin.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devlog.admin</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/dev-log-admin && python3 server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/saint/dev-log-admin/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/saint/dev-log-admin/launchd.err</string>
</dict>
</plist>
EOF
```

2. 활성화:

```bash
launchctl load ~/Library/LaunchAgents/com.devlog.admin.plist
```

3. 비활성화:

```bash
launchctl unload ~/Library/LaunchAgents/com.devlog.admin.plist
```

---

## 문제 해결

### 서버가 시작되지 않을 때

1. 포트 확인:
```bash
lsof -i :8100
```

2. 로그 확인:
```bash
tail -50 ~/dev-log-admin/server.log
```

3. Python 패키지 확인:
```bash
pip3 install fastapi uvicorn
```

### 서버가 중지되지 않을 때

```bash
# 강제 종료
pkill -9 -f "python3.*server.py"

# PID 파일 삭제
rm -f ~/dev-log-admin/.server.pid
```

### Alias가 작동하지 않을 때

```bash
# Shell 재시작
source ~/.zshrc

# 또는 새 터미널 창 열기
```

---

## 주요 파일

| 파일 | 설명 |
|------|------|
| `start.sh` | 서버 시작 스크립트 |
| `stop.sh` | 서버 중지 스크립트 |
| `status.sh` | 상태 확인 스크립트 |
| `server.py` | FastAPI 서버 |
| `sync.py` | 데이터 동기화 스크립트 |
| `config.json` | 프로젝트 설정 |
| `devlog.db` | SQLite 데이터베이스 |
| `.server.pid` | 서버 PID 파일 |
| `server.log` | 서버 로그 |

---

## URL

- **Dashboard**: http://localhost:8100
- **API Docs**: http://localhost:8100/docs
- **Health Check**: http://localhost:8100/health

---

## API 예제

### 프로젝트 목록

```bash
curl http://localhost:8100/api/projects
```

### 프로젝트 상세

```bash
curl http://localhost:8100/api/projects/saas-ws
```

### 커밋 검색

```bash
curl "http://localhost:8100/api/search?q=feat"
```

### 통계

```bash
curl http://localhost:8100/api/stats/overview
```

---

**Happy Logging!** 📊
