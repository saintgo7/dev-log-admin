#!/usr/bin/env python3
"""
Generate HTML only (skip parse-devlog.py)
"""
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/saint/01_DEV")

TARGET_PROJECTS = [
    "26-full-dev-log",
    "26-web-skyair-TS",
    "SaaS_erp_clone-260116",
    "app-passport-reserve",
]

HTML_GENERATORS = [
    "generate-html.py",
    "generate-timeline.py",
    "generate-heatmap.py",
    "generate-stats.py",
    "generate-files-history.py",
    "generate-commit-size.py",
    "generate-time-analysis.py",
    "generate-deployment.py",
]


def generate_html(project_name: str):
    """Generate HTML for a project"""
    project_path = BASE_DIR / project_name
    scripts_dir = project_path / "scripts"

    if not scripts_dir.exists():
        print(f"⚠️  {project_name}: No scripts directory")
        return False

    print(f"\n📁 {project_name}")

    for generator in HTML_GENERATORS:
        script_path = scripts_dir / generator
        if not script_path.exists():
            continue

        try:
            subprocess.run(
                ["python3", str(script_path)],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
        except Exception as e:
            print(f"   ⚠️  {generator}: {e}")

    print(f"   ✅ HTML generated")
    return True


def main():
    print("\n" + "="*60)
    print("🚀 Generate HTML Only (Skip parse-devlog.py)")
    print("="*60)

    success_count = 0
    for project in TARGET_PROJECTS:
        try:
            if generate_html(project):
                success_count += 1
        except Exception as e:
            print(f"❌ {project}: Error - {e}")

    print("\n" + "="*60)
    print(f"✅ Success: {success_count}/{len(TARGET_PROJECTS)} projects")
    print("="*60)


if __name__ == "__main__":
    main()
