"""
API v2 Router - combines all v2 endpoints
"""
from fastapi import APIRouter

from app.api.v2.auth import router as auth_router
from app.api.v2.users import router as users_router
from app.api.v2.teams import router as teams_router
from app.api.v2.projects import router as projects_router
from app.api.v2.github import router as github_router
from app.api.v2.webhooks import router as webhooks_router


# Create main v2 router
router = APIRouter(prefix="/api/v2")

# Include all sub-routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(teams_router)
router.include_router(projects_router)
router.include_router(github_router)
router.include_router(webhooks_router)
