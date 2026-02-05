#!/usr/bin/env python3
"""
Batch generate dev-logs.json from markdown files for multiple projects
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path("/Users/saint/01_DEV")

# Projects with dev-log but no JSON
PROJECTS = [
    "26-full-dev-log",
    "26-web-skyair-TS",
    "SaaS_erp_clone-260116",
    "app-passport-reserve",
    "saas-crew",
    "saas-erpmes-2601",
    "saas-iso",
    "saas-orak",
    "01-template",
]


def parse_devlog_markdown(md_path: Path) -> dict:
    """Parse a single dev-log markdown file"""
    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception:
        return None

    log = {
        "log_number": "",
        "type": "feat",
        "title": "Untitled",
        "date": "",
        "author": {"name": "", "email": ""},
        "files_changed": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "full_content": content
    }

    # Extract log number from filename
    filename = md_path.stem
    match = re.match(r'^(\d+)', filename)
    if match:
        log["log_number"] = match.group(1)

    # Extract from filename pattern: NN-YYYY-MM-DD-HHMM-description.md
    filename_match = re.match(r'(\d+)-(\d{4}-\d{2}-\d{2})-(\d{4})-(.+)', filename)
    if filename_match:
        log["log_number"] = filename_match.group(1)
        date_str = filename_match.group(2)
        time_str = filename_match.group(3)
        log["date"] = f"{date_str} {time_str[:2]}:{time_str[2:]}"

    # Extract from content
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Title from first # header
        if line.startswith('# ') and not log["title"]:
            log["title"] = line[2:].strip()

        # Type from title or content
        if 'type' in line.lower() or 'Type:' in line:
            for t in ['feat', 'fix', 'refactor', 'docs', 'test', 'chore', 'ci', 'perf', 'setup']:
                if t in line.lower():
                    log["type"] = t
                    break

        # Date
        if 'Date:' in line or '**Date**' in line:
            date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', line)
            if date_match:
                log["date"] = date_match.group(1).replace('/', '-')

        # Author
        if 'Author:' in line:
            author_match = re.search(r'Author:\s*(.+?)(?:\s*<(.+?)>)?$', line)
            if author_match:
                log["author"]["name"] = author_match.group(1).strip()
                if author_match.group(2):
                    log["author"]["email"] = author_match.group(2).strip()

        # Files changed
        if 'Files Changed' in line or 'Files Modified' in line or '변경된 파일' in line:
            num_match = re.search(r'(\d+)', line)
            if num_match:
                log["files_changed"] = int(num_match.group(1))

        # Lines added/deleted
        if 'Lines Added' in line or '추가된 라인' in line:
            num_match = re.search(r'(\d+)', line)
            if num_match:
                log["lines_added"] = int(num_match.group(1))

        if 'Lines Deleted' in line or '삭제된 라인' in line:
            num_match = re.search(r'(\d+)', line)
            if num_match:
                log["lines_deleted"] = int(num_match.group(1))

    # Default date if not found
    if not log["date"]:
        log["date"] = datetime.fromtimestamp(md_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

    return log


def generate_json_for_project(project_name: str):
    """Generate dev-logs.json for a single project"""
    project_path = BASE_DIR / project_name
    devlog_dir = project_path / "docs" / "dev-log"

    if not devlog_dir.exists():
        print(f"⚠️  {project_name}: No dev-log directory")
        return False

    # Find all markdown files
    md_files = sorted(devlog_dir.glob("*.md"))
    if not md_files:
        print(f"⚠️  {project_name}: No markdown files")
        return False

    print(f"\n📁 {project_name}")
    print(f"   Found {len(md_files)} markdown files")

    # Parse all files
    logs = []
    for md_file in md_files:
        log = parse_devlog_markdown(md_file)
        if log:
            logs.append(log)

    # Sort by log number
    logs.sort(key=lambda x: int(x.get("log_number", 0) or 0))

    # Calculate statistics
    type_counts = defaultdict(int)
    total_files = 0
    total_added = 0
    total_deleted = 0

    for log in logs:
        type_counts[log["type"]] += 1
        total_files += log.get("files_changed", 0)
        total_added += log.get("lines_added", 0)
        total_deleted += log.get("lines_deleted", 0)

    statistics = {
        "total_logs": len(logs),
        "total_files_changed": total_files,
        "total_lines_added": total_added,
        "total_lines_deleted": total_deleted,
        "commits_by_type": dict(type_counts),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Create output structure
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
    print(f"   📊 {len(logs)} logs, {sum(type_counts.values())} commits")

    return True


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚀 Batch Generate dev-logs.json")
    print("="*60)

    success_count = 0
    for project in PROJECTS:
        try:
            if generate_json_for_project(project):
                success_count += 1
        except Exception as e:
            print(f"❌ {project}: Error - {e}")

    print("\n" + "="*60)
    print(f"✅ Success: {success_count}/{len(PROJECTS)} projects")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. cd ~/dev-log-admin")
    print("   2. python3 auto-discover.py --yes")
    print("   3. python3 sync.py")


if __name__ == "__main__":
    main()
