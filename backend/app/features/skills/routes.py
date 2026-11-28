"""
Skill endpoints:

  GET /api/skills   every skill the studio can give an agent, read from the
                    agent resources (AGENT_RESOURCES): name, description and
                    where it came from (owner only)

An agent's picks are saved on the agent (agents/routes.py); each run's
skills reach its sandbox with its setup (GET /api/runs/{id}/sandbox).
"""

from fastapi import APIRouter, Depends, HTTPException

from app.auth.owner_auth import require_owner
from app.features.skills import service
from app.features.skills.schemas import SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut], dependencies=[Depends(require_owner)])
def list_skills():
    try:
        return service.list_skills()
    except service.SkillsUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))
