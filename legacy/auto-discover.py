#!/usr/bin/env python3
"""
Auto-discover projects with dev-log in /Users/saint/01_DEV
and update config.json
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

BASE_DIR = Path("/Users/saint/01_DEV")
CONFIG_FILE = Path(__file__).parent / "config.json"

# Files to detect tech stack
TECH_STACK_INDICATORS = {
    "package.json": "Node.js",
    "go.mod": "Go",
    "go.sum": "Go",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "Pipfile": "Python",
    "Cargo.toml": "Rust",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "pom.xml": "Java",
    "build.gradle": "Java",
    "pubspec.yaml": "Flutter/Dart",
    "docker-compose.yml": "Docker",
    "Dockerfile": "Docker",
}

FRAMEWORK_INDICATORS = {
    "next.config.js": "Next.js",
    "nuxt.config.js": "Nuxt.js",
    "angular.json": "Angular",
    "vue.config.js": "Vue.js",
    "svelte.config.js": "Svelte",
    "main.py": "FastAPI",
    "manage.py": "Django",
    "app.py": "Flask",
    "gin.go": "Gin",
    "echo.go": "Echo",
}


def get_git_remote(project_path: Path) -> Optional[str]:
    """Get git remote URL"""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def detect_tech_stack(project_path: Path) -> List[str]:
    """Detect tech stack from project files"""
    tech_stack = set()

    # Check for tech stack indicator files
    for file_name, tech in TECH_STACK_INDICATORS.items():
        if (project_path / file_name).exists():
            tech_stack.add(tech)

    # Check for framework indicators
    for file_name, framework in FRAMEWORK_INDICATORS.items():
        if (project_path / file_name).exists():
            tech_stack.add(framework)

    # Check for database files
    if (project_path / "prisma").is_dir():
        tech_stack.add("Prisma")
    if (project_path / "alembic").is_dir():
        tech_stack.add("Alembic")

    # Check package.json for frameworks
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

                if "next" in deps:
                    tech_stack.add("Next.js")
                if "react" in deps:
                    tech_stack.add("React")
                if "vue" in deps:
                    tech_stack.add("Vue.js")
                if "svelte" in deps:
                    tech_stack.add("Svelte")
                if "express" in deps:
                    tech_stack.add("Express")
                if "fastify" in deps:
                    tech_stack.add("Fastify")
        except Exception:
            pass

    # Check requirements.txt for frameworks
    requirements = project_path / "requirements.txt"
    if requirements.exists():
        try:
            content = requirements.read_text()
            if "fastapi" in content.lower():
                tech_stack.add("FastAPI")
            if "django" in content.lower():
                tech_stack.add("Django")
            if "flask" in content.lower():
                tech_stack.add("Flask")
            if "sqlalchemy" in content.lower():
                tech_stack.add("SQLAlchemy")
        except Exception:
            pass

    # Detect databases
    if (project_path / "docker-compose.yml").exists():
        try:
            content = (project_path / "docker-compose.yml").read_text()
            if "postgres" in content.lower():
                tech_stack.add("PostgreSQL")
            if "mysql" in content.lower() or "mariadb" in content.lower():
                tech_stack.add("MySQL")
            if "mongodb" in content.lower():
                tech_stack.add("MongoDB")
            if "redis" in content.lower():
                tech_stack.add("Redis")
        except Exception:
            pass

    return sorted(list(tech_stack))


def slugify(name: str) -> str:
    """Convert project name to slug"""
    return name.lower().replace("_", "-").replace(" ", "-")


def find_projects() -> List[Dict]:
    """Find all projects with dev-log"""
    projects = []

    print(f"\n🔍 Scanning {BASE_DIR}...")
    print("=" * 60)

    # Scan all directories
    for project_dir in sorted(BASE_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        # Skip hidden, node_modules, venv, etc
        if project_dir.name.startswith("."):
            continue
        if project_dir.name in ["node_modules", "venv", "__pycache__", "dist", "build"]:
            continue

        # Check for dev-logs.json
        json_path = project_dir / "docs" / "html" / "data" / "dev-logs.json"
        devlog_dir = project_dir / "docs" / "dev-log"

        # Only add if dev-logs.json exists (required for sync)
        if json_path.exists():
            print(f"\n✅ Found: {project_dir.name}")

            # Get git info
            git_remote = get_git_remote(project_dir)
            if git_remote:
                print(f"   Git: {git_remote}")

            # Detect tech stack
            tech_stack = detect_tech_stack(project_dir)
            if tech_stack:
                print(f"   Tech: {', '.join(tech_stack)}")

            # Create project config
            slug = slugify(project_dir.name)
            name = project_dir.name.replace("-", " ").replace("_", " ").title()

            project = {
                "slug": slug,
                "name": name,
                "description": f"{name} project",
                "repository_url": git_remote or "",
                "tech_stack": tech_stack,
                "json_path": str(json_path),
                "html_url": f"file://{json_path.parent.parent / 'index.html'}"
            }

            projects.append(project)
        elif devlog_dir.exists() and devlog_dir.is_dir():
            # dev-log directory exists but no JSON yet
            print(f"\n⚠️  Skipped: {project_dir.name} (dev-log exists, but no dev-logs.json)")
            print(f"    Run './scripts/update-html.sh' to generate JSON")

    print("\n" + "=" * 60)
    print(f"✅ Found {len(projects)} projects with dev-log\n")

    return projects


def update_config(new_projects: List[Dict]):
    """Update config.json with new projects"""
    # Load existing config
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {"projects": []}

    existing_slugs = {p["slug"] for p in config["projects"]}

    # Add new projects
    added = 0
    for project in new_projects:
        if project["slug"] not in existing_slugs:
            config["projects"].append(project)
            added += 1
            print(f"➕ Added: {project['name']}")

    # Save config
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Config updated: {added} new projects added")
    print(f"📊 Total projects: {len(config['projects'])}")


def main():
    """Main function"""
    import sys

    print("\n" + "🚀 Auto-Discover Dev-Log Projects ".center(60, "="))

    # Find projects
    projects = find_projects()

    if not projects:
        print("⚠️  No projects with dev-log found")
        return

    # Show summary
    print("\n📋 Project Summary:")
    print("=" * 60)
    for i, project in enumerate(projects, 1):
        print(f"{i:2d}. {project['name']}")
        print(f"    Tech: {', '.join(project['tech_stack']) or 'N/A'}")
        print(f"    Slug: {project['slug']}")

    # Check for --yes flag or auto-update
    auto_update = "--yes" in sys.argv or "-y" in sys.argv

    if auto_update:
        print("\n" + "=" * 60)
        print("🔄 Auto-updating config.json...")
        update_config(projects)
        print("\n✅ Done! Run 'python3 sync.py' to sync to database.")
    else:
        # Ask for confirmation
        print("\n" + "=" * 60)
        try:
            response = input("\n❓ Update config.json? (y/N): ")
            if response.lower() == "y":
                update_config(projects)
                print("\n✅ Done! Run 'python3 sync.py' to sync to database.")
            else:
                print("\n❌ Cancelled")
        except (EOFError, KeyboardInterrupt):
            print("\n\n💡 Tip: Use '--yes' flag to auto-update without prompt")
            print("   Example: python3 auto-discover.py --yes")
            sys.exit(0)


if __name__ == "__main__":
    main()
