#!/usr/bin/env python3
"""
Dev Log Admin API Server - SQLite Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from typing import Optional, List
from contextlib import contextmanager
import json
import subprocess
import os
from pathlib import Path

app = FastAPI(title="Dev Log Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DB_PATH = str(Path(__file__).parent / "devlog.db")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ==========================================
# API Endpoints
# ==========================================

@app.get("/api/projects")
def list_projects():
    """Get all projects"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, slug, name, description, repository_url, tech_stack, html_url,
                   total_commits, last_synced_at
            FROM projects
            ORDER BY name
        """).fetchall()

        return [
            {
                "id": row["id"],
                "slug": row["slug"],
                "name": row["name"],
                "description": row["description"],
                "repository_url": row["repository_url"],
                "tech_stack": json.loads(row["tech_stack"]) if row["tech_stack"] else [],
                "html_url": row["html_url"],
                "total_commits": row["total_commits"],
                "last_synced_at": row["last_synced_at"]
            }
            for row in rows
        ]

@app.get("/api/projects/{slug}")
def get_project(slug: str):
    """Get project details"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT id, slug, name, description, repository_url, tech_stack, html_url,
                   total_commits, last_synced_at, created_at, updated_at
            FROM projects
            WHERE slug = ?
        """, (slug,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get type statistics for this project
        type_stats = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM commits
            WHERE project_id = ?
            GROUP BY type
        """, (row["id"],)).fetchall()

        return {
            "id": row["id"],
            "slug": row["slug"],
            "name": row["name"],
            "description": row["description"],
            "repository_url": row["repository_url"],
            "tech_stack": json.loads(row["tech_stack"]) if row["tech_stack"] else [],
            "html_url": row["html_url"],
            "total_commits": row["total_commits"],
            "last_synced_at": row["last_synced_at"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "type_stats": {stat["type"]: stat["count"] for stat in type_stats}
        }

@app.get("/api/projects/{slug}/commits")
def get_project_commits(
    slug: str,
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None,
    search: Optional[str] = None
):
    """Get commits for a project"""
    with get_db() as conn:
        # Get project ID
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (slug,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_id = project["id"]

        # Build query
        query = """
            SELECT id, log_number, commit_hash, type, title, author_name, author_email,
                   date, files_changed, lines_added, lines_deleted
            FROM commits
            WHERE project_id = ?
        """
        params = [project_id]

        if type:
            query += " AND type = ?"
            params.append(type)

        if search:
            query += " AND (title LIKE ? OR full_content LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Get total count
        count_query = query.replace("SELECT id, log_number, commit_hash, type, title, author_name, author_email, date, files_changed, lines_added, lines_deleted", "SELECT COUNT(*)")
        total = conn.execute(count_query, params).fetchone()[0]

        # Add pagination
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "commits": [dict(row) for row in rows]
        }

@app.get("/api/commits/{commit_id}")
def get_commit_detail(commit_id: int):
    """Get full commit details including content"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT c.*, p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            WHERE c.id = ?
        """, (commit_id,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Commit not found")

        return dict(row)

@app.get("/api/search")
def search_commits(
    q: str,
    project: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Search commits across all projects"""
    with get_db() as conn:
        query = """
            SELECT c.id, c.log_number, c.commit_hash, c.type, c.title,
                   c.author_name, c.date, c.files_changed, c.lines_added, c.lines_deleted,
                   p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            WHERE (c.title LIKE ? OR c.full_content LIKE ?)
        """
        params = [f"%{q}%", f"%{q}%"]

        if project:
            query += " AND p.slug = ?"
            params.append(project)

        if type:
            query += " AND c.type = ?"
            params.append(type)

        # Count total
        count_query = query.replace(
            "SELECT c.id, c.log_number, c.commit_hash, c.type, c.title, c.author_name, c.date, c.files_changed, c.lines_added, c.lines_deleted, p.slug as project_slug, p.name as project_name",
            "SELECT COUNT(*)"
        )
        total = conn.execute(count_query, params).fetchone()[0]

        # Add pagination
        query += " ORDER BY c.date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": q,
            "results": [dict(row) for row in rows]
        }

@app.get("/api/stats/overview")
def get_overview_stats():
    """Get overall statistics"""
    with get_db() as conn:
        # Basic stats
        total_projects = conn.execute("SELECT COUNT(*) as count FROM projects").fetchone()["count"]
        total_commits = conn.execute("SELECT COUNT(*) as count FROM commits").fetchone()["count"]

        # Commits by type
        type_stats = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM commits
            GROUP BY type
            ORDER BY count DESC
        """).fetchall()

        # Recent activity (last 20 commits)
        recent = conn.execute("""
            SELECT c.id, c.log_number, c.title, c.type, c.date,
                   p.slug as project_slug, p.name as project_name
            FROM commits c
            JOIN projects p ON c.project_id = p.id
            ORDER BY c.date DESC
            LIMIT 20
        """).fetchall()

        # Commits by project
        project_stats = conn.execute("""
            SELECT p.name, p.slug, COUNT(c.id) as commit_count
            FROM projects p
            LEFT JOIN commits c ON p.id = c.project_id
            GROUP BY p.id
            ORDER BY commit_count DESC
        """).fetchall()

        return {
            "total_projects": total_projects,
            "total_commits": total_commits,
            "commits_by_type": {stat["type"]: stat["count"] for stat in type_stats},
            "recent_activity": [dict(row) for row in recent],
            "commits_by_project": [dict(row) for row in project_stats]
        }

@app.get("/api/stats/timeline")
def get_timeline_stats(days: int = 30):
    """Get commit timeline statistics"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT
                date(date) as day,
                COUNT(*) as count,
                GROUP_CONCAT(DISTINCT type) as types
            FROM commits
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY date(date)
            ORDER BY day DESC
        """, (days,)).fetchall()

        return {
            "days": days,
            "timeline": [dict(row) for row in rows]
        }

@app.get("/api/projects/{slug}/open")
def open_project_html(slug: str):
    """Open project HTML in browser"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT html_url FROM projects WHERE slug = ?
        """, (slug,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        html_url = row["html_url"]
        if not html_url:
            raise HTTPException(status_code=400, detail="No HTML URL configured")

        # Convert file:// URL to actual path
        if html_url.startswith("file://"):
            file_path = html_url.replace("file://", "")
        else:
            file_path = html_url

        # Expand ~ to home directory
        file_path = os.path.expanduser(file_path)

        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"HTML file not found: {file_path}")

        # Open in default browser (macOS/Linux)
        try:
            subprocess.run(["open", file_path], check=True)
            return {"status": "success", "message": f"Opened {file_path}"}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Failed to open HTML: {str(e)}")
        except FileNotFoundError:
            # Try xdg-open for Linux
            try:
                subprocess.run(["xdg-open", file_path], check=True)
                return {"status": "success", "message": f"Opened {file_path}"}
            except:
                raise HTTPException(status_code=500, detail="Could not find 'open' or 'xdg-open' command")

@app.get("/api/projects/{slug}/terminal")
def open_project_terminal(slug: str):
    """Open project directory in iTerm"""
    with get_db() as conn:
        row = conn.execute("""
            SELECT html_url FROM projects WHERE slug = ?
        """, (slug,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        html_url = row["html_url"]
        if not html_url:
            raise HTTPException(status_code=400, detail="No html URL configured")

        # Get project directory from html_url
        # Example: file:///Users/saint/01_DEV/WebErpMes-v2/docs/html/index.html
        if html_url.startswith("file://"):
            file_path = html_url.replace("file://", "")
        else:
            file_path = html_url

        file_path = os.path.expanduser(file_path)
        # Remove /docs/html/index.html to get project root
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))

        if not os.path.exists(project_dir):
            raise HTTPException(status_code=404, detail=f"Project directory not found: {project_dir}")

        # Try iTerm first, fallback to Terminal.app
        try:
            # Check if iTerm is installed
            iterm_path = "/Applications/iTerm.app"
            if os.path.exists(iterm_path):
                # Use simple open command - iTerm will open in the specified directory
                subprocess.run(["open", "-a", "iTerm", project_dir], check=True)
            else:
                # Fallback to Terminal.app
                applescript = f'''
                    tell application "Terminal"
                        activate
                        do script "cd '{project_dir}' && clear"
                    end tell
                '''
                subprocess.run(["osascript", "-e", applescript], check=True, timeout=3)

            return {"status": "success", "message": f"Opened terminal at {project_dir}"}
        except subprocess.TimeoutExpired:
            # If AppleScript times out, just return success (terminal likely opened)
            return {"status": "success", "message": f"Terminal command sent to {project_dir}"}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Failed to open terminal: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    with get_db() as conn:
        try:
            conn.execute("SELECT 1").fetchone()
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": str(e)}
            )

# Mount static files (must be last)
app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "static"), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Dev Log Admin Server")
    print("="*60)
    print("📊 Dashboard: http://localhost:8100")
    print("📖 API Docs:  http://localhost:8100/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8100)
