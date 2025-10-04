"""Campaign management endpoints."""

from fastapi import APIRouter, HTTPException, Path
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
    campaign_name: Optional[str] = Field(
        None,
        description="Optional custom campaign name. If not provided, a name will be generated based on the goal.",
        example="Q4 High-Value Retention Campaign"
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
    campaign_id: str
    goal: str
    campaign_name: str
    created_at: str
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
        campaigns_data = campaign_service.get_all_campaigns()
        
        # Handle case where no campaigns exist
        if not campaigns_data:
            return []
        
        # Convert dictionaries to Pydantic models
        campaigns = []
        for campaign_dict in campaigns_data:
            try:
                # Ensure proper type conversion for numeric fields
                if 'segment_size' in campaign_dict:
                    campaign_dict['segment_size'] = int(campaign_dict['segment_size'])
                
                # Ensure target_criteria is a dict (should already be parsed by service)
                if isinstance(campaign_dict.get('target_criteria'), str):
                    import json
                    campaign_dict['target_criteria'] = json.loads(campaign_dict['target_criteria'])
                
                campaign = Campaign(**campaign_dict)
                campaigns.append(campaign)
            except Exception as validation_error:
                # Log the validation error but continue with other campaigns
                print(f"Warning: Skipping invalid campaign data: {validation_error}")
                print(f"Campaign data: {campaign_dict}")
                continue
        
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaigns: {str(e)}"
        )

@router.post("/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest) -> CampaignResponse:
    """
    Create a new marketing campaign (returns immediately, executes in background).

    Args:
        request: Campaign creation request with goal and optional campaign name

    Returns:
        Campaign creation response with campaign_id and pending status
    """
    try:
        result = campaign_service.create_campaign(
            goal=request.goal,
            campaign_name=request.campaign_name
        )

        # Return immediately with pending status
        return CampaignResponse(
            success=result.get('success', False),
            campaign_id=result.get('campaign_id', ''),
            goal=result.get('goal', request.goal),
            campaign_name=result.get('campaign_name', 'Unnamed Campaign'),
            created_at=result.get('created_at', ''),
            plan=result.get('plan', []),
            results=None,  # Not available yet (executing in background)
            error=result.get('error')
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating campaign: {str(e)}"
        )


@router.get("/{campaign_id}/plan")
async def get_campaign_plan(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the execution plan for a specific campaign with current status.

    Args:
        campaign_id: The ID of the campaign

    Returns:
        Plan with step statuses
    """
    try:
        status = campaign_service.get_campaign_status(campaign_id)

        if not status.get('success'):
            raise HTTPException(
                status_code=404,
                detail=status.get('error', 'Campaign not found')
            )

        return status.get('steps', [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaign plan: {str(e)}"
        )


@router.get("/{campaign_id}/status")
async def get_campaign_status(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the current execution status of a campaign.

    Args:
        campaign_id: The ID of the campaign

    Returns:
        Campaign status (pending, executing, completed, failed)
    """
    try:
        status = campaign_service.get_campaign_status(campaign_id)

        if not status.get('success'):
            raise HTTPException(
                status_code=404,
                detail=status.get('error', 'Campaign not found')
            )

        return {
            "campaign_id": status.get('campaign_id'),
            "status": status.get('status'),
            "created_at": status.get('created_at'),
            "error": status.get('error')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaign status: {str(e)}"
        )


@router.get("/{campaign_id}/result")
async def get_campaign_result(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the results summary for a specific campaign.

    Args:
        campaign_id: The ID of the campaign

    Returns:
        Campaign results (only available when status=completed)
    """
    try:
        status = campaign_service.get_campaign_status(campaign_id)

        if not status.get('success'):
            raise HTTPException(
                status_code=404,
                detail=status.get('error', 'Campaign not found')
            )

        # Check if execution is complete
        if status.get('status') != 'completed':
            return {
                "success": False,
                "message": f"Campaign execution in progress (status: {status.get('status')})",
                "status": status.get('status')
            }

        # Return results
        results = status.get('results', {})

        # Format results to match expected structure
        strategy = results.get('CampaignStrategistAgent', {}).get('strategy', {})

        return {
            "success": True,
            "campaign_strategy": strategy.get('campaign_strategy', {}),
            "confidence_score": strategy.get('confidence_score', 0.0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaign results: {str(e)}"
        )
