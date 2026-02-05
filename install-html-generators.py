#!/usr/bin/env python3
"""
Install HTML generation scripts to all projects with dev-logs.json
"""
import shutil
from pathlib import Path
import subprocess

BASE_DIR = Path("/Users/saint/01_DEV")
TEMPLATE_DIR = Path.home() / "dev-log-template"

# Projects that need HTML generators - ALL projects with dev-logs.json
TARGET_PROJECTS = [
    "WebErpMes-v2",
    "web-music-heartlib",
    "app-hospital-yoyang",
    "26-SmartFactotyAX_Support",
    "SmartFactoryAX_v0.1.2",
    "SmartFactoryAX_v0.1.1",
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


def install_scripts(project_name: str):
    """Install HTML generation scripts to a project"""
    project_path = BASE_DIR / project_name
    json_path = project_path / "docs" / "html" / "data" / "dev-logs.json"

    if not json_path.exists():
        print(f"⚠️  {project_name}: No dev-logs.json found")
        return False

    print(f"\n📁 {project_name}")

    # Create directories
    scripts_dir = project_path / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    html_dir = project_path / "docs" / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    # Copy scripts from template
    scripts_to_copy = [
        "parse-devlog.py",
        "generate-html.py",
        "generate-timeline.py",
        "generate-heatmap.py",
        "generate-stats.py",
        "generate-files-history.py",
        "generate-commit-size.py",
        "generate-time-analysis.py",
        "generate-deployment.py",
        "update-html.sh",
    ]

    copied = 0
    for script in scripts_to_copy:
        src = TEMPLATE_DIR / "scripts" / script
        dst = scripts_dir / script

        if src.exists():
            shutil.copy2(src, dst)
            if script.endswith('.sh'):
                dst.chmod(0o755)
            copied += 1

    # Copy static files
    static_files = ["styles.css", "scripts.js"]
    for static_file in static_files:
        src = TEMPLATE_DIR / static_file
        dst = html_dir / static_file
        if src.exists():
            shutil.copy2(src, dst)
            copied += 1

    print(f"   ✅ Installed {copied} files")

    # Generate HTML
    print(f"   🔄 Generating HTML...")
    update_script = scripts_dir / "update-html.sh"
    if update_script.exists():
        try:
            result = subprocess.run(
                ["bash", str(update_script)],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(f"   ✅ HTML generated successfully")
                return True
            else:
                print(f"   ⚠️  HTML generation had issues (check output)")
                return True  # Still success for script installation
        except Exception as e:
            print(f"   ⚠️  HTML generation error: {e}")
            return True

    return True


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🚀 Install HTML Generators to All Projects")
    print("="*60)

    if not TEMPLATE_DIR.exists():
        print(f"❌ Template directory not found: {TEMPLATE_DIR}")
        return

    success_count = 0
    for project in TARGET_PROJECTS:
        try:
            if install_scripts(project):
                success_count += 1
        except Exception as e:
            print(f"❌ {project}: Error - {e}")

    print("\n" + "="*60)
    print(f"✅ Success: {success_count}/{len(TARGET_PROJECTS)} projects")
    print("="*60)
    print("\n💡 Next: Refresh Dashboard and try Open HTML again")
    print("   URL: http://localhost:8100")


if __name__ == "__main__":
    main()
