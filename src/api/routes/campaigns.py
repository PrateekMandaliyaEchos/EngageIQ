"""Campaign creation endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.services import CampaignService

router = APIRouter()
campaign_service = CampaignService()


class CampaignRequest(BaseModel):
    """Request model for campaign creation."""
    goal: str = Field(
        ...,
        description="Natural language campaign goal",
        example="Find high-value agents with excellent satisfaction for VIP retention"
    )


class TodoItem(BaseModel):
    """Todo item in the execution plan."""
    step: int
    description: str
    agent: str
    active_form: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class CampaignResponse(BaseModel):
    """Response model for campaign creation."""
    success: bool
    goal: str
    plan: List[TodoItem]
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/campaigns/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest):
    """
    Create a new campaign from natural language goal.

    This endpoint:
    1. Accepts a natural language campaign goal
    2. Orchestrates multi-agent workflow
    3. Returns execution plan and results

    Example Request:
    ```json
    {
        "goal": "Find high-value agents with excellent satisfaction for VIP retention"
    }
    ```

    Example Response:
    ```json
    {
        "success": true,
        "goal": "Find high-value agents...",
        "plan": [
            {
                "step": 1,
                "description": "Parse campaign goal and extract criteria",
                "agent": "GoalParser",
                "status": "completed",
                "active_form": "Parsing campaign goal"
            }
        ],
        "results": {
            "criteria": {
                "objective": "retention",
                "constraints": [...]
            }
        }
    }
    ```
    """
    try:
        # Call campaign service
        result = campaign_service.create_campaign(goal=request.goal)

        # Ensure the response includes the goal field for validation
        if not result.get('goal'):
            result['goal'] = request.goal

        return result

    except Exception as e:
        # Return a properly formatted error response
        error_response = {
            "success": False,
            "goal": request.goal,
            "plan": [],
            "error": f"Campaign creation failed: {str(e)}"
        }
        return error_response
