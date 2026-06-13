#!/usr/bin/env python3
"""
SQLite to PostgreSQL Data Migration Script

Migrates existing data from SQLite (devlog.db) to PostgreSQL.
Creates a default team and assigns all projects to it.

Usage:
    python scripts/migrate_sqlite_to_postgres.py [--dry-run] [--sqlite-path PATH]

Options:
    --dry-run       Show what would be migrated without actually migrating
    --sqlite-path   Path to SQLite database (default: ../devlog.db)
"""
import argparse
import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4

import asyncpg

# Default paths
DEFAULT_SQLITE_PATH = Path(__file__).parent.parent.parent / "legacy" / "devlog.db"


class MigrationError(Exception):
    """Migration error"""
    pass


class SQLiteReader:
    """Reads data from SQLite database"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Connect to SQLite database"""
        if not self.db_path.exists():
            raise MigrationError(f"SQLite database not found: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close connection"""
        if self.conn:
            self.conn.close()

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        cursor = self.conn.execute("""
            SELECT id, slug, name, description, repository_url, tech_stack,
                   html_url, last_synced_at, total_commits, created_at, updated_at
            FROM projects
            ORDER BY id
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_commits(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all commits for a project"""
        cursor = self.conn.execute("""
            SELECT id, project_id, log_number, commit_hash, type, title,
                   author_name, author_email, date, files_changed,
                   lines_added, lines_deleted, full_content, created_at
            FROM commits
            WHERE project_id = ?
            ORDER BY id
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, int]:
        """Get migration statistics"""
        projects = self.conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        commits = self.conn.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
        return {"projects": projects, "commits": commits}


class PostgresMigrator:
    """Migrates data to PostgreSQL"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

        # ID mappings (old SQLite ID -> new UUID)
        self.project_id_map: Dict[int, str] = {}

    async def connect(self) -> None:
        """Connect to PostgreSQL"""
        self.pool = await asyncpg.create_pool(self.database_url)

    async def close(self) -> None:
        """Close connection"""
        if self.pool:
            await self.pool.close()

    async def create_default_admin(self) -> str:
        """Create default admin user and return ID"""
        user_id = str(uuid4())
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (id, email, name, role, is_active, is_verified, auth_provider, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
                ON CONFLICT (email) DO UPDATE SET updated_at = EXCLUDED.updated_at
                RETURNING id
            """, user_id, "admin@devlog.local", "Admin", "admin", True, True, "local", datetime.now(timezone.utc))
        print(f"  Created/updated admin user: admin@devlog.local")
        return user_id

    async def create_default_team(self, owner_id: str) -> str:
        """Create default team and return ID"""
        team_id = str(uuid4())
        async with self.pool.acquire() as conn:
            # Create team
            await conn.execute("""
                INSERT INTO teams (id, name, slug, description, plan, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $6)
                ON CONFLICT (slug) DO UPDATE SET updated_at = EXCLUDED.updated_at
                RETURNING id
            """, team_id, "Default Team", "default", "Migrated from SQLite", "free", datetime.now(timezone.utc))

            # Add owner as team member
            await conn.execute("""
                INSERT INTO team_members (team_id, user_id, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $5)
                ON CONFLICT (team_id, user_id) DO NOTHING
            """, team_id, owner_id, "owner", True, datetime.now(timezone.utc))

        print(f"  Created/updated default team: default")
        return team_id

    async def migrate_project(self, project: Dict[str, Any], team_id: str) -> str:
        """Migrate a single project"""
        project_uuid = str(uuid4())
        self.project_id_map[project["id"]] = project_uuid

        # Parse timestamps
        created_at = self._parse_timestamp(project.get("created_at"))
        updated_at = self._parse_timestamp(project.get("updated_at"))
        last_synced = self._parse_timestamp(project.get("last_synced_at"))

        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO projects (
                    id, slug, name, description, repository_url, tech_stack,
                    html_url, last_synced_at, total_commits, team_id, visibility,
                    created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = EXCLUDED.updated_at
            """,
                project_uuid,
                project["slug"],
                project["name"],
                project.get("description"),
                project.get("repository_url"),
                project.get("tech_stack"),
                project.get("html_url"),
                last_synced,
                project.get("total_commits", 0),
                team_id,
                "private",
                created_at,
                updated_at
            )

        return project_uuid

    async def migrate_commits(self, commits: List[Dict[str, Any]], project_uuid: str) -> int:
        """Migrate commits for a project"""
        if not commits:
            return 0

        migrated = 0
        async with self.pool.acquire() as conn:
            for commit in commits:
                # Parse timestamp
                date = self._parse_timestamp(commit["date"])
                created_at = self._parse_timestamp(commit.get("created_at")) or date

                try:
                    await conn.execute("""
                        INSERT INTO commits (
                            project_id, log_number, commit_hash, type, title,
                            author_name, author_email, date, files_changed,
                            lines_added, lines_deleted, full_content, created_at, updated_at
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $13)
                    """,
                        project_uuid,
                        commit.get("log_number"),
                        commit.get("commit_hash"),
                        commit["type"],
                        commit["title"],
                        commit.get("author_name"),
                        commit.get("author_email"),
                        date,
                        commit.get("files_changed", 0),
                        commit.get("lines_added", 0),
                        commit.get("lines_deleted", 0),
                        commit.get("full_content"),
                        created_at
                    )
                    migrated += 1
                except Exception as e:
                    print(f"    Warning: Failed to migrate commit {commit.get('id')}: {e}")

        return migrated

    @staticmethod
    def _parse_timestamp(value: Any) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value

        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(str(value), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        return datetime.now(timezone.utc)


async def run_migration(
    sqlite_path: Path,
    postgres_url: str,
    dry_run: bool = False
) -> None:
    """Run the migration"""
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)

    # Read from SQLite
    print(f"\nSource: {sqlite_path}")
    reader = SQLiteReader(sqlite_path)
    reader.connect()

    stats = reader.get_stats()
    print(f"Found: {stats['projects']} projects, {stats['commits']} commits")

    if dry_run:
        print("\n[DRY RUN] Would migrate the following projects:")
        for project in reader.get_projects():
            commits = reader.get_commits(project["id"])
            print(f"  - {project['slug']}: {len(commits)} commits")
        reader.close()
        print("\n[DRY RUN] No changes made.")
        return

    # Write to PostgreSQL
    print(f"\nTarget: PostgreSQL")
    migrator = PostgresMigrator(postgres_url)
    await migrator.connect()

    try:
        # Create default admin and team
        print("\nCreating default admin and team...")
        admin_id = await migrator.create_default_admin()
        team_id = await migrator.create_default_team(admin_id)

        # Migrate projects
        print("\nMigrating projects...")
        projects = reader.get_projects()
        total_commits = 0

        for project in projects:
            project_uuid = await migrator.migrate_project(project, team_id)
            commits = reader.get_commits(project["id"])
            migrated = await migrator.migrate_commits(commits, project_uuid)
            total_commits += migrated
            print(f"  - {project['slug']}: {migrated} commits")

        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print(f"Projects migrated: {len(projects)}")
        print(f"Commits migrated: {total_commits}")
        print(f"Default team: default")
        print(f"Admin user: admin@devlog.local")

    finally:
        await migrator.close()
        reader.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without actually migrating"
    )
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=DEFAULT_SQLITE_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_SQLITE_PATH})"
    )
    parser.add_argument(
        "--postgres-url",
        type=str,
        default="postgresql://localhost/devlog",
        help="PostgreSQL connection URL"
    )

    args = parser.parse_args()

    asyncio.run(run_migration(
        sqlite_path=args.sqlite_path,
        postgres_url=args.postgres_url,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
