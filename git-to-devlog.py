#!/usr/bin/env python3
"""
Generate dev-logs.json from Git commit history
"""
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path("/Users/saint/01_DEV")

# Projects to generate dev-log from Git
TARGET_PROJECTS = [
    "WebErpMes-v2",
    "web-music-heartlib",
    "app-hospital-yoyang",
    "26-SmartFactotyAX_Support",
    "SmartFactoryAX_v0.1.2",
    "SmartFactoryAX_v0.1.1",
]

# Limit commits for large repos
MAX_COMMITS = 100


def run_git(project_path: Path, command: list):
    """Run git command"""
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"   ⚠️  Git error: {e}")
    return None


def parse_commit_type(message: str) -> str:
    """Extract commit type from message"""
    # Conventional commits: type(scope): message
    match = re.match(r'^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.+?\))?: ', message.lower())
    if match:
        return match.group(1)

    # Common keywords
    msg_lower = message.lower()
    if any(k in msg_lower for k in ['add', 'create', 'new', '추가', '생성']):
        return 'feat'
    if any(k in msg_lower for k in ['fix', 'bug', 'resolve', '수정', '해결']):
        return 'fix'
    if any(k in msg_lower for k in ['update', 'change', 'modify', '변경', '업데이트']):
        return 'refactor'
    if any(k in msg_lower for k in ['doc', 'readme', '문서']):
        return 'docs'
    if any(k in msg_lower for k in ['test', '테스트']):
        return 'test'
    if any(k in msg_lower for k in ['deploy', '배포', 'release']):
        return 'ci'
    if any(k in msg_lower for k in ['clean', 'remove', 'delete', '삭제', '정리']):
        return 'chore'

    return 'feat'  # Default


def get_commit_stats(project_path: Path, commit_hash: str) -> tuple:
    """Get files changed, lines added/deleted for a commit"""
    output = run_git(project_path, ["show", "--stat", "--oneline", commit_hash])
    if not output:
        return 0, 0, 0

    lines = output.split('\n')
    files_changed = 0
    lines_added = 0
    lines_deleted = 0

    for line in lines[1:]:  # Skip first line (commit message)
        if '|' in line:
            files_changed += 1
        elif 'changed' in line:
            # Example: " 5 files changed, 123 insertions(+), 45 deletions(-)"
            match = re.search(r'(\d+) file', line)
            if match:
                files_changed = int(match.group(1))
            match = re.search(r'(\d+) insertion', line)
            if match:
                lines_added = int(match.group(1))
            match = re.search(r'(\d+) deletion', line)
            if match:
                lines_deleted = int(match.group(1))

    return files_changed, lines_added, lines_deleted


def generate_devlog_from_git(project_name: str, max_commits: int = MAX_COMMITS):
    """Generate dev-logs.json from Git history"""
    project_path = BASE_DIR / project_name

    if not (project_path / ".git").exists():
        print(f"⚠️  {project_name}: Not a git repository")
        return False

    print(f"\n📁 {project_name}")

    # Get commit log
    format_str = "%H|%an|%ae|%ad|%s"
    log_output = run_git(project_path, [
        "log",
        f"-{max_commits}",
        f"--format={format_str}",
        "--date=format:%Y-%m-%d %H:%M"
    ])

    if not log_output:
        print(f"   ⚠️  No commits found")
        return False

    commits = log_output.strip().split('\n')
    print(f"   Found {len(commits)} commits")

    logs = []
    for i, commit_line in enumerate(commits, 1):
        parts = commit_line.split('|', 4)
        if len(parts) != 5:
            continue

        commit_hash, author_name, author_email, date, message = parts

        # Parse commit
        log = {
            "log_number": str(len(commits) - i + 1).zfill(3),  # Reverse order
            "commit": commit_hash[:8],
            "type": parse_commit_type(message),
            "title": message[:100],
            "author": {
                "name": author_name,
                "email": author_email
            },
            "date": date,
            "files_changed": 0,
            "lines_added": 0,
            "lines_deleted": 0,
            "full_content": f"# {message}\n\n**Date**: {date}\n**Author**: {author_name} <{author_email}>\n**Commit**: {commit_hash[:8]}\n\nAuto-generated from Git history."
        }

        # Get stats (can be slow for large repos)
        if len(commits) < 50:  # Only for small repos
            files, added, deleted = get_commit_stats(project_path, commit_hash)
            log["files_changed"] = files
            log["lines_added"] = added
            log["lines_deleted"] = deleted

        logs.append(log)

    # Reverse to chronological order
    logs.reverse()

    # Calculate statistics
    type_counts = defaultdict(int)
    total_files = 0
    total_added = 0
    total_deleted = 0

    for log in logs:
        type_counts[log["type"]] += 1
        total_files += log["files_changed"]
        total_added += log["lines_added"]
        total_deleted += log["lines_deleted"]

    statistics = {
        "total_logs": len(logs),
        "total_files_changed": total_files,
        "total_lines_added": total_added,
        "total_lines_deleted": total_deleted,
        "commits_by_type": dict(type_counts),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "git-history"
    }

    output = {
        "statistics": statistics,
        "logs": logs
    }

    # Create directories
    json_dir = project_path / "docs" / "html" / "data"
    json_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON
    json_path = json_dir / "dev-logs.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Generated: {json_path}")
    print(f"   📊 {len(logs)} logs, Types: {dict(type_counts)}")

    return True


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚀 Generate Dev-Log from Git History")
    print("="*60)

    success_count = 0
    for project in TARGET_PROJECTS:
        try:
            if generate_devlog_from_git(project):
                success_count += 1
        except Exception as e:
            print(f"❌ {project}: Error - {e}")

    print("\n" + "="*60)
    print(f"✅ Success: {success_count}/{len(TARGET_PROJECTS)} projects")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. cd ~/dev-log-admin")
    print("   2. python3 auto-discover.py --yes")
    print("   3. python3 sync.py")
    print("   4. open http://localhost:8100")


if __name__ == "__main__":
    main()
