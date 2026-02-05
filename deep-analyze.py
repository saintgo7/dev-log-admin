#!/usr/bin/env python3
"""
Deep analyze all projects in /Users/saint/01_DEV
Find Git repositories, analyze activity, and generate comprehensive report
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

BASE_DIR = Path("/Users/saint/01_DEV")

# Skip directories
SKIP_DIRS = {
    "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
    ".next", ".nuxt", "vendor", "target", "pkg", "bin", ".git"
}


def run_git_command(project_path: Path, command: list, timeout=10):
    """Run git command safely"""
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def analyze_git_repo(project_path: Path) -> dict:
    """Analyze git repository"""
    git_dir = project_path / ".git"
    if not git_dir.exists():
        return None

    info = {
        "has_git": True,
        "remote_url": None,
        "branch": None,
        "total_commits": 0,
        "recent_commits": 0,
        "last_commit_date": None,
        "last_commit_message": None,
        "authors": [],
        "days_since_last_commit": None
    }

    # Remote URL
    remote_url = run_git_command(project_path, ["config", "--get", "remote.origin.url"])
    if remote_url:
        info["remote_url"] = remote_url

    # Current branch
    branch = run_git_command(project_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch:
        info["branch"] = branch

    # Total commits
    total = run_git_command(project_path, ["rev-list", "--count", "HEAD"])
    if total:
        info["total_commits"] = int(total)

    # Recent commits (last 30 days)
    since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    recent = run_git_command(project_path, ["rev-list", "--count", f"--since={since_date}", "HEAD"])
    if recent:
        info["recent_commits"] = int(recent)

    # Last commit info
    last_commit = run_git_command(project_path, ["log", "-1", "--format=%H|%an|%ae|%ad|%s", "--date=short"])
    if last_commit:
        parts = last_commit.split('|', 4)
        if len(parts) == 5:
            info["last_commit_date"] = parts[3]
            info["last_commit_message"] = parts[4]

            # Calculate days since last commit
            try:
                last_date = datetime.strptime(parts[3], "%Y-%m-%d")
                days_ago = (datetime.now() - last_date).days
                info["days_since_last_commit"] = days_ago
            except:
                pass

    # Get authors
    authors_output = run_git_command(project_path, ["log", "--format=%an", "--all"], timeout=15)
    if authors_output:
        author_counts = defaultdict(int)
        for author in authors_output.split('\n'):
            if author:
                author_counts[author] += 1
        info["authors"] = [{"name": name, "commits": count}
                          for name, count in sorted(author_counts.items(),
                                                   key=lambda x: x[1], reverse=True)[:5]]

    return info


def count_files(project_path: Path) -> dict:
    """Count files by extension"""
    counts = defaultdict(int)
    total = 0

    try:
        for item in project_path.rglob("*"):
            if item.is_file():
                # Skip large directories
                if any(skip in item.parts for skip in SKIP_DIRS):
                    continue

                total += 1
                ext = item.suffix.lower()
                if ext:
                    counts[ext] += 1
                else:
                    counts["[no ext]"] += 1
    except Exception:
        pass

    return {
        "total": total,
        "by_extension": dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10])
    }


def detect_project_type(project_path: Path) -> list:
    """Detect project type/category"""
    types = []

    # Check for indicators
    indicators = {
        "Web Frontend": ["package.json", "webpack.config.js", "vite.config.js"],
        "Next.js": ["next.config.js"],
        "React Native": ["app.json", "metro.config.js"],
        "Flutter": ["pubspec.yaml"],
        "Python Backend": ["requirements.txt", "pyproject.toml", "setup.py"],
        "Django": ["manage.py"],
        "FastAPI": ["main.py"],
        "Go Backend": ["go.mod"],
        "Rust": ["Cargo.toml"],
        "Mobile App": ["android/", "ios/"],
        "Docker": ["docker-compose.yml", "Dockerfile"],
    }

    for ptype, files in indicators.items():
        for file in files:
            if (project_path / file).exists() or (project_path / file.rstrip('/')).is_dir():
                if ptype not in types:
                    types.append(ptype)

    return types


def analyze_project(project_path: Path) -> dict:
    """Comprehensive project analysis"""
    project_name = project_path.name

    analysis = {
        "name": project_name,
        "path": str(project_path),
        "git": None,
        "files": None,
        "types": [],
        "has_devlog": False,
        "has_devlog_json": False,
        "devlog_count": 0,
        "score": 0  # Activity score
    }

    # Git analysis
    git_info = analyze_git_repo(project_path)
    if git_info:
        analysis["git"] = git_info

        # Calculate activity score
        score = 0
        if git_info["total_commits"] > 0:
            score += min(git_info["total_commits"] / 10, 50)  # Max 50 points
        if git_info["recent_commits"] > 0:
            score += git_info["recent_commits"] * 2  # 2 points per recent commit
        if git_info["days_since_last_commit"] is not None:
            if git_info["days_since_last_commit"] < 7:
                score += 30
            elif git_info["days_since_last_commit"] < 30:
                score += 20
            elif git_info["days_since_last_commit"] < 90:
                score += 10

        analysis["score"] = int(score)

    # File analysis
    analysis["files"] = count_files(project_path)

    # Project types
    analysis["types"] = detect_project_type(project_path)

    # Dev-log check
    devlog_dir = project_path / "docs" / "dev-log"
    if devlog_dir.exists():
        analysis["has_devlog"] = True
        md_files = list(devlog_dir.glob("*.md"))
        analysis["devlog_count"] = len(md_files)

    devlog_json = project_path / "docs" / "html" / "data" / "dev-logs.json"
    if devlog_json.exists():
        analysis["has_devlog_json"] = True

    return analysis


def main():
    """Main analysis function"""
    print("\n" + "="*70)
    print("🔍 Deep Project Analysis")
    print("="*70)
    print(f"\n📁 Scanning: {BASE_DIR}\n")

    all_projects = []
    git_projects = []
    active_projects = []
    devlog_projects = []
    no_devlog_active = []

    # Scan all directories
    for item in sorted(BASE_DIR.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        if item.name in SKIP_DIRS:
            continue

        print(f"Analyzing: {item.name}...", end=" ")

        analysis = analyze_project(item)
        all_projects.append(analysis)

        if analysis["git"]:
            git_projects.append(analysis)

            if analysis["git"]["total_commits"] > 0:
                active_projects.append(analysis)

                if analysis["has_devlog_json"]:
                    devlog_projects.append(analysis)
                else:
                    no_devlog_active.append(analysis)

        print(f"✓ (Score: {analysis['score']})")

    # Sort by score
    all_projects.sort(key=lambda x: x["score"], reverse=True)
    no_devlog_active.sort(key=lambda x: x["score"], reverse=True)

    # Print summary
    print("\n" + "="*70)
    print("📊 Analysis Summary")
    print("="*70)
    print(f"\nTotal projects: {len(all_projects)}")
    print(f"Git repositories: {len(git_projects)}")
    print(f"Active projects (with commits): {len(active_projects)}")
    print(f"Projects with dev-log JSON: {len(devlog_projects)}")
    print(f"Active without dev-log: {len(no_devlog_active)}")

    # Top active projects without dev-log
    print("\n" + "="*70)
    print("🎯 Top Active Projects WITHOUT Dev-Log")
    print("="*70)

    for i, project in enumerate(no_devlog_active[:20], 1):
        git = project["git"]
        print(f"\n{i:2d}. {project['name']}")
        print(f"    Score: {project['score']}")
        print(f"    Commits: {git['total_commits']} total, {git['recent_commits']} recent")
        if git["last_commit_date"]:
            print(f"    Last commit: {git['last_commit_date']} ({git['days_since_last_commit']} days ago)")
        if git["last_commit_message"]:
            msg = git["last_commit_message"][:60]
            print(f"    Message: {msg}")
        if project["types"]:
            print(f"    Type: {', '.join(project['types'])}")
        if git["remote_url"]:
            print(f"    Repo: {git['remote_url']}")

    # Projects with dev-log but no JSON
    has_md_no_json = [p for p in all_projects
                      if p["has_devlog"] and not p["has_devlog_json"]]

    if has_md_no_json:
        print("\n" + "="*70)
        print("📝 Projects with Markdown but NO JSON")
        print("="*70)
        for project in has_md_no_json:
            print(f"\n- {project['name']}")
            print(f"  Markdown files: {project['devlog_count']}")

    # Save detailed report
    report_path = Path(__file__).parent / "project-analysis.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_projects": len(all_projects),
                "git_repositories": len(git_projects),
                "active_projects": len(active_projects),
                "with_devlog_json": len(devlog_projects),
                "without_devlog": len(no_devlog_active)
            },
            "projects": all_projects
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Detailed report saved: {report_path}")

    # Recommendations
    print("\n" + "="*70)
    print("💡 Recommendations")
    print("="*70)
    print(f"\n1. Generate dev-log from Git history for top {min(len(no_devlog_active), 10)} active projects")
    print(f"2. Run batch-generate-json.py for {len(has_md_no_json)} projects with markdown")
    print(f"3. Total potential: {len(no_devlog_active) + len(has_md_no_json)} additional projects")

    return no_devlog_active


if __name__ == "__main__":
    main()
