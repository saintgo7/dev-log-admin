#!/usr/bin/env python3
"""
SQLite Database Schema for Dev Log Admin
"""
import sqlite3
from pathlib import Path as _Path

DB_PATH = str(_Path(__file__).parent / "devlog.db")

def init_db():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            repository_url TEXT,
            tech_stack TEXT,  -- JSON string
            html_url TEXT,
            last_synced_at TEXT,
            total_commits INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- Commits table
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            log_number INTEGER,
            commit_hash TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            author_name TEXT,
            author_email TEXT,
            date TEXT NOT NULL,
            files_changed INTEGER DEFAULT 0,
            lines_added INTEGER DEFAULT 0,
            lines_deleted INTEGER DEFAULT 0,
            full_content TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_commits_project_id ON commits(project_id);
        CREATE INDEX IF NOT EXISTS idx_commits_date ON commits(date DESC);
        CREATE INDEX IF NOT EXISTS idx_commits_type ON commits(type);
        CREATE INDEX IF NOT EXISTS idx_commits_title ON commits(title);
        CREATE INDEX IF NOT EXISTS idx_commits_project_date ON commits(project_id, date DESC);
    """)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

if __name__ == "__main__":
    init_db()
