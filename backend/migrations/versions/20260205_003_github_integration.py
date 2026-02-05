"""GitHub integration tables

Revision ID: 003_github_integration
Revises: 002_row_level_security
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_github_integration'
down_revision: Union[str, None] = '002_row_level_security'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create github_connections table
    op.create_table(
        'github_connections',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('github_user_id', sa.String(50), nullable=False),
        sa.Column('github_username', sa.String(255), nullable=False),
        sa.Column('github_email', sa.String(255), nullable=True),
        sa.Column('github_avatar_url', sa.Text(), nullable=True),
        sa.Column('access_token_encrypted', sa.Text(), nullable=False),
        sa.Column('refresh_token_encrypted', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scopes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_github_connections_user_id', 'github_connections', ['user_id'])
    op.create_index('ix_github_connections_user_status', 'github_connections', ['user_id', 'status'])

    # Create github_repositories table
    op.create_table(
        'github_repositories',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('github_repo_id', sa.String(50), nullable=False),
        sa.Column('owner', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(510), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('html_url', sa.Text(), nullable=False),
        sa.Column('clone_url', sa.Text(), nullable=True),
        sa.Column('ssh_url', sa.Text(), nullable=True),
        sa.Column('default_branch', sa.String(255), nullable=False, default='main'),
        sa.Column('is_private', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_fork', sa.Boolean(), nullable=False, default=False),
        sa.Column('language', sa.String(100), nullable=True),
        sa.Column('topics', sa.Text(), nullable=True),
        sa.Column('stars_count', sa.Integer(), nullable=False, default=0),
        sa.Column('forks_count', sa.Integer(), nullable=False, default=0),
        sa.Column('watchers_count', sa.Integer(), nullable=False, default=0),
        sa.Column('open_issues_count', sa.Integer(), nullable=False, default=0),
        sa.Column('sync_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('sync_commits', sa.Boolean(), nullable=False, default=True),
        sa.Column('sync_issues', sa.Boolean(), nullable=False, default=False),
        sa.Column('sync_prs', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_status', sa.String(20), nullable=True),
        sa.Column('last_sync_error', sa.Text(), nullable=True),
        sa.Column('last_commit_sha', sa.String(40), nullable=True),
        sa.Column('webhook_id', sa.String(50), nullable=True),
        sa.Column('webhook_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', name='uq_github_repositories_project_id'),
    )
    op.create_index('ix_github_repositories_project_id', 'github_repositories', ['project_id'])
    op.create_index('ix_github_repositories_owner_name', 'github_repositories', ['owner', 'name'])

    # Create sync_history table
    op.create_table(
        'sync_history',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('sync_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('commits_synced', sa.Integer(), nullable=False, default=0),
        sa.Column('issues_synced', sa.Integer(), nullable=False, default=0),
        sa.Column('prs_synced', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['repository_id'], ['github_repositories.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sync_history_repository_id', 'sync_history', ['repository_id'])

    # Create webhook_events table
    op.create_table(
        'webhook_events',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=True),
        sa.Column('delivery_id', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['repository_id'], ['github_repositories.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('delivery_id', name='uq_webhook_events_delivery_id'),
    )
    op.create_index('ix_webhook_events_repository_id', 'webhook_events', ['repository_id'])
    op.create_index('ix_webhook_events_type_processed', 'webhook_events', ['event_type', 'processed'])

    # Add url column to commits table if not exists
    op.add_column('commits', sa.Column('url', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove url column from commits
    op.drop_column('commits', 'url')

    # Drop webhook_events table
    op.drop_index('ix_webhook_events_type_processed', table_name='webhook_events')
    op.drop_index('ix_webhook_events_repository_id', table_name='webhook_events')
    op.drop_table('webhook_events')

    # Drop sync_history table
    op.drop_index('ix_sync_history_repository_id', table_name='sync_history')
    op.drop_table('sync_history')

    # Drop github_repositories table
    op.drop_index('ix_github_repositories_owner_name', table_name='github_repositories')
    op.drop_index('ix_github_repositories_project_id', table_name='github_repositories')
    op.drop_table('github_repositories')

    # Drop github_connections table
    op.drop_index('ix_github_connections_user_status', table_name='github_connections')
    op.drop_index('ix_github_connections_user_id', table_name='github_connections')
    op.drop_table('github_connections')
