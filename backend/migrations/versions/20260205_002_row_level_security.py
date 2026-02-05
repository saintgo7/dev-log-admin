"""Add Row Level Security policies

Revision ID: 002_rls
Revises: 001_initial
Create Date: 2026-02-05

Row Level Security (RLS) ensures data isolation at database level:
- Projects: Only team members can access
- Commits: Access follows project access
- Team members: Only team members can see other members
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "002_rls"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: RLS requires the application to set a session variable
    # with the current user_id. This is done via:
    # SET LOCAL app.current_user_id = 'user-uuid';

    # Enable RLS on tables
    op.execute("ALTER TABLE projects ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE commits ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;")

    # Projects: User can access if public OR member of the project's team
    op.execute("""
        CREATE POLICY projects_select_policy ON projects
        FOR SELECT
        USING (
            visibility = 'public'
            OR team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = current_setting('app.current_user_id', true)::uuid
                AND is_active = true
            )
        );
    """)

    # Projects: User can insert/update/delete if team member with write access
    op.execute("""
        CREATE POLICY projects_modify_policy ON projects
        FOR ALL
        USING (
            team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = current_setting('app.current_user_id', true)::uuid
                AND is_active = true
                AND role IN ('owner', 'admin', 'member')
            )
        );
    """)

    # Commits: Follow project access
    op.execute("""
        CREATE POLICY commits_select_policy ON commits
        FOR SELECT
        USING (
            project_id IN (
                SELECT id FROM projects
                WHERE visibility = 'public'
                OR team_id IN (
                    SELECT team_id FROM team_members
                    WHERE user_id = current_setting('app.current_user_id', true)::uuid
                    AND is_active = true
                )
            )
        );
    """)

    op.execute("""
        CREATE POLICY commits_modify_policy ON commits
        FOR ALL
        USING (
            project_id IN (
                SELECT id FROM projects
                WHERE team_id IN (
                    SELECT team_id FROM team_members
                    WHERE user_id = current_setting('app.current_user_id', true)::uuid
                    AND is_active = true
                    AND role IN ('owner', 'admin', 'member')
                )
            )
        );
    """)

    # Team members: Only team members can see other members
    op.execute("""
        CREATE POLICY team_members_select_policy ON team_members
        FOR SELECT
        USING (
            team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = current_setting('app.current_user_id', true)::uuid
                AND is_active = true
            )
        );
    """)

    # Team members: Only admins can modify
    op.execute("""
        CREATE POLICY team_members_modify_policy ON team_members
        FOR ALL
        USING (
            team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = current_setting('app.current_user_id', true)::uuid
                AND is_active = true
                AND role IN ('owner', 'admin')
            )
        );
    """)

    # Create a function to set user context
    op.execute("""
        CREATE OR REPLACE FUNCTION set_current_user_id(user_id UUID)
        RETURNS VOID AS $$
        BEGIN
            PERFORM set_config('app.current_user_id', user_id::text, true);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS set_current_user_id(UUID);")

    # Drop policies
    op.execute("DROP POLICY IF EXISTS team_members_modify_policy ON team_members;")
    op.execute("DROP POLICY IF EXISTS team_members_select_policy ON team_members;")
    op.execute("DROP POLICY IF EXISTS commits_modify_policy ON commits;")
    op.execute("DROP POLICY IF EXISTS commits_select_policy ON commits;")
    op.execute("DROP POLICY IF EXISTS projects_modify_policy ON projects;")
    op.execute("DROP POLICY IF EXISTS projects_select_policy ON projects;")

    # Disable RLS
    op.execute("ALTER TABLE team_members DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE commits DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE projects DISABLE ROW LEVEL SECURITY;")
