#!/usr/bin/env python3
"""
Sync dev-logs.json to SQLite database
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = str(Path(__file__).parent / "devlog.db")

def load_config():
    """Load config.json"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def sync_project(conn, project_config):
    """Sync single project to database"""
    slug = project_config["slug"]
    name = project_config["name"]
    json_path = Path(project_config["json_path"]).expanduser()

    if not json_path.exists():
        print(f"⚠️  [SKIP] {name}: JSON not found at {json_path}")
        return 0

    # Load JSON data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ [ERROR] {name}: Failed to load JSON - {e}")
        return 0

    logs = data.get("logs", [])

    # Insert or update project
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (slug, name, description, repository_url, tech_stack, html_url, total_commits, last_synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            repository_url = excluded.repository_url,
            tech_stack = excluded.tech_stack,
            html_url = excluded.html_url,
            total_commits = excluded.total_commits,
            last_synced_at = datetime('now'),
            updated_at = datetime('now')
    """, (
        slug,
        name,
        project_config.get("description"),
        project_config.get("repository_url"),
        json.dumps(project_config.get("tech_stack", [])),
        project_config.get("html_url"),
        len(logs)
    ))

    # Get project ID
    project_id = cursor.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()[0]

    # Delete existing commits for clean sync
    cursor.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))

    # Insert commits
    for log in logs:
        cursor.execute("""
            INSERT INTO commits (
                project_id, log_number, commit_hash, type, title,
                author_name, author_email, date,
                files_changed, lines_added, lines_deleted, full_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            log.get("log_number"),
            log.get("commit"),
            log.get("type", "feat"),
            log.get("title", "Untitled"),
            log.get("author", {}).get("name") if isinstance(log.get("author"), dict) else log.get("author"),
            log.get("author", {}).get("email") if isinstance(log.get("author"), dict) else None,
            log.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            log.get("files_changed", 0),
            log.get("lines_added", 0),
            log.get("lines_deleted", 0),
            log.get("full_content", "")
        ))

    conn.commit()
    print(f"✅ [OK] {name}: {len(logs)} commits synced")
    return len(logs)

def main():
    """Main sync function"""
    config = load_config()
    conn = sqlite3.connect(DB_PATH)

    print("\n" + "="*60)
    print("🔄 Syncing dev-logs to SQLite")
    print("="*60 + "\n")

    total_commits = 0
    for project in config["projects"]:
        commits = sync_project(conn, project)
        total_commits += commits

    conn.close()

    print("\n" + "="*60)
    print(f"✅ Sync complete: {len(config['projects'])} projects, {total_commits} commits")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
