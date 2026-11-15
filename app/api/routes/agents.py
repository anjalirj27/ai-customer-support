from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.get("/")
async def list_agents(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    List all available agents and their capabilities.
    """
    return AgentService(db).get_agent_info()


@router.get("/{agent_type}/capabilities")
async def get_agent_capabilities(
    agent_type: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get capabilities of a specific agent.

    Args:
        agent_type: "support", "order", or "billing"
    """
    info = AgentService(db).get_agent_info(agent_type)

    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])

    return info
