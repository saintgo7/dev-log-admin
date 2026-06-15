# Commit 모델(UUID 문자열 PK)이 응답 스키마로 정상 검증되는지 확인하는 회귀 테스트
"""
Regression tests for commit response schemas.

Commit.id is a UUID string PK (UUIDPrimaryKeyMixin / GUID), so the response
schemas must declare id as str, not int. Otherwise model_validate raises a
ValidationError and the project/commit endpoints return HTTP 500.
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.models.commit import Commit
from app.schemas.commit import CommitResponse
from app.schemas.project import CommitSummary


def _make_commit() -> Commit:
    return Commit(
        id=str(uuid4()),
        project_id=str(uuid4()),
        type="feat",
        title="hello",
        author_name="tester",
        author_email="tester@example.com",
        date=datetime.now(timezone.utc),
        files_changed=0,
        lines_added=0,
        lines_deleted=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_commit_response_validates_uuid_id():
    """CommitResponse should accept a UUID string id from the model."""
    commit = _make_commit()
    response = CommitResponse.model_validate(commit)
    assert response.id == commit.id
    assert isinstance(response.id, str)


def test_commit_summary_validates_uuid_id():
    """CommitSummary should accept a UUID string id from the model."""
    commit = _make_commit()
    summary = CommitSummary.model_validate(commit)
    assert summary.id == commit.id
    assert isinstance(summary.id, str)
