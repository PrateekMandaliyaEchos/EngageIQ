"""Campaign management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.services import CampaignService

router = APIRouter()
campaign_service = CampaignService()


class Campaign(BaseModel):
    """Response model for campaign details."""
    campaign_id: str
    name: str
    goal: str
    target_criteria: Dict[str, Any]
    segment_size: int
    created_at: str
    status: str


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


@router.get("/all", response_model=List[Campaign])
async def get_all_campaigns() -> List[Campaign]:
    """
    Get all existing campaigns.

    Returns:
        List of all campaigns with their details

    Example Response:
    ```json
    [
        {
            "campaign_id": "CAM001",
            "name": "Q4 High-Value Focus",
            "goal": "Target high-NPS agents with declining sales for Q4 boost",
            "target_criteria": {
                "nps_score": "high",
                "sales_trend": "declining"
            },
            "segment_size": 150,
            "created_at": "2025-09-15T10:30:00Z",
            "status": "completed"
        }
    ]
    ```
    """
    try:
        return campaign_service.get_all_campaigns()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaigns: {str(e)}"
        )

@router.post("/create")
async def create_campaign(request: CampaignRequest) -> Dict[str, Any]:
    """
    Create a new marketing campaign.

    Args:
        request: Campaign creation request with goal

    Returns:
        Campaign creation result with execution plan and results
    """
