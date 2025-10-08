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
        print("🔍 Getting campaigns from service...")
        campaigns_data = campaign_service.get_all_campaigns()
        print(f"📊 Retrieved {len(campaigns_data) if campaigns_data else 0} campaigns from service")
        
        # Handle case where no campaigns exist
        if not campaigns_data:
            print("ℹ️  No campaigns found, returning empty list")
            return []
        
        # Convert dictionaries to Pydantic models
        campaigns = []
        for i, campaign_dict in enumerate(campaigns_data):
            try:
                print(f"🔄 Processing campaign {i+1}: {campaign_dict.get('campaign_id', 'Unknown ID')}")
                
                # Ensure proper type conversion for numeric fields
                if 'segment_size' in campaign_dict:
                    campaign_dict['segment_size'] = int(campaign_dict['segment_size'])
                
                # Convert datetime objects to strings
                if 'created_at' in campaign_dict and hasattr(campaign_dict['created_at'], 'isoformat'):
                    campaign_dict['created_at'] = campaign_dict['created_at'].isoformat()
                if 'updated_at' in campaign_dict and hasattr(campaign_dict['updated_at'], 'isoformat'):
                    campaign_dict['updated_at'] = campaign_dict['updated_at'].isoformat()
                
                # Ensure target_criteria is a dict (should already be parsed by service)
                if isinstance(campaign_dict.get('target_criteria'), str):
                    import json
                    campaign_dict['target_criteria'] = json.loads(campaign_dict['target_criteria'])
                
                campaign = Campaign(**campaign_dict)
                campaigns.append(campaign)
                print(f"✅ Successfully processed campaign {i+1}")
            except Exception as validation_error:
                # Log the validation error but continue with other campaigns
                print(f"❌ Warning: Skipping invalid campaign data: {validation_error}")
                print(f"📋 Campaign data: {campaign_dict}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"🎉 Successfully processed {len(campaigns)} campaigns")
        return campaigns
    except Exception as e:
        print(f"❌ Error retrieving campaigns: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print(f"🔍 Getting campaign result for: {campaign_id}")
        
        # Get campaign data from database (replacing campaign_service approach)
        from src.core.config import get_settings
        from src.connectors.factory import create_connector
        
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Get campaign from database
        campaigns = connector.get_campaigns()
        campaign_data = next((c for c in campaigns if c['campaign_id'] == campaign_id), None)
        
        if not campaign_data:
            print(f"❌ Campaign not found in database: {campaign_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Campaign {campaign_id} not found"
            )
        
        print(f"✅ Campaign found in database: {campaign_id}")
        
        # Check if execution is complete (treat "planned" as completed for now)
        campaign_status = campaign_data.get('status', 'unknown')
        if campaign_status not in ['planned', 'completed']:
            return {
                "success": False,
                "message": f"Campaign execution in progress (status: {campaign_status})",
                "status": campaign_status
            }

        # Get the actual LLM-generated results from the campaign_results table
        campaign_result = connector.get_campaign_result(campaign_id)
        
        if not campaign_result:
            return {
                "success": False,
                "message": "Campaign LLM results not found. Campaign may not be completed yet.",
                "status": campaign_status
            }
        
        llm_results = campaign_result.get('llm_results', {})

        # Debug: Print what we're getting (preserving your original debug logic)
        import json
        print(f"DEBUG - Campaign data from DB: {json.dumps(campaign_data, indent=2, default=str)}")
        print(f"DEBUG - LLM results keys: {llm_results.keys()}")
        print(f"DEBUG - CampaignStrategistAgent result: {llm_results.get('CampaignStrategistAgent', {})}")

        strategist_result = llm_results.get('CampaignStrategistAgent', {})

        # Unwrap if wrapped in 'strategy' key (from orchestrator)
        if 'strategy' in strategist_result:
            strategist_result = strategist_result['strategy']

        # Check if we have segment-based strategies or unified strategy (preserving your original logic)
        if 'segment_strategies' in strategist_result:
            # New per-segment strategy format
            segment_strategies = strategist_result.get('segment_strategies', {})
            
            # Calculate total agents by summing agent_count from all segments
            total_agents = 0
            for segment_name, segment_data in segment_strategies.items():
                if isinstance(segment_data, dict) and 'agent_count' in segment_data:
                    total_agents += segment_data.get('agent_count', 0)
            
            return {
                "success": True,
                "objective": strategist_result.get('objective', 'unknown'),
                "total_agents": total_agents,
                "segment_strategies": segment_strategies,
                "confidence_score": strategist_result.get('confidence_score', 0.0)
            }
        else:
            # Legacy unified strategy format
            return {
                "success": True,
                "campaign_strategy": strategist_result.get('campaign_strategy', {}),
                "confidence_score": strategist_result.get('confidence_score', 0.0)
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaign results: {str(e)}"
        )


@router.get("/{campaign_id}/agent_profiles")
async def get_campaign_agent_profiles(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the agent profiles generated for a specific campaign.
    
    Args:
        campaign_id: The ID of the campaign
        
    Returns:
        JSON response with agent profiles list
        
    Example Response:
    ```json
    {
        "campaign_id": "CAM123",
        "total_agents": 150,
        "agent_profiles": [
            {
                "agent_id": "12345",
                "name": "John Doe",
                "segment": "Independent Agents",
                "aum": 2500000.0,
                "nps_score": 8.5,
                "tenure": 5.2,
                "policies_sold": 12,
                "age": 45,
                "city": "New York",
                "education": "BACHELOR",
                "premium_amount": 7500.0,
                "nps_feedback": "Great service and support"
            }
        ]
    }
    ```
    """
    try:
        from src.core.config import get_settings
        from src.connectors.factory import create_connector
        
        # Get connector from settings
        settings = get_settings()
        connector_type = settings.data_connector
        connector_config = settings.get_connector_config(connector_type)
        connector = create_connector(connector_type, connector_config)
        
        # Check if we're using PostgreSQL connector
        if hasattr(connector, 'get_agent_profiles'):
            # Get from database
            try:
                agent_profiles = connector.get_agent_profiles(campaign_id)
                if not agent_profiles:
                    # Return a more specific error that the frontend can handle
                    raise HTTPException(
                        status_code=202,  # Accepted but not ready yet
                        detail=f"Agent profiles are being generated for campaign {campaign_id}. Please try again in a few moments."
                    )
                
                # Format response to match expected structure
                agent_profiles_data = {
                    "campaign_id": campaign_id,
                    "total_agents": len(agent_profiles),
                    "agent_profiles": agent_profiles
                }
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as db_error:
                # For other database errors, return a 500 but with a more user-friendly message
                print(f"❌ Database error in agent_profiles: {str(db_error)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Agent profiles are temporarily unavailable. Please try again in a few moments."
                )
        else:
            # Fallback to JSON file
            # Get agent profiles file path
            agent_profiles_file = f"agent_profiles/{campaign_id}.json"
            
            # Check if agent profiles file exists
            if not connector.file_exists(agent_profiles_file):
                raise HTTPException(
                    status_code=404,
                    detail=f"Agent profiles not found for campaign {campaign_id}. Campaign may not be completed yet."
                )
            
            # Read agent profiles from JSON file
            try:
                agent_profiles_data = connector.read_json(agent_profiles_file)
            except Exception as json_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error reading agent profiles file: {str(json_error)}"
                )
        
        # Validate the data structure
        if not isinstance(agent_profiles_data, dict) or 'agent_profiles' not in agent_profiles_data:
            raise HTTPException(
                status_code=500,
                detail="Invalid agent profiles data format"
            )
        
        return {
            "campaign_id": campaign_id,
            "total_agents": len(agent_profiles_data.get('agent_profiles', [])),
            "agent_profiles": agent_profiles_data.get('agent_profiles', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent profiles: {str(e)}"
        )
