"""Campaign service for managing campaign creation and orchestration."""

import json
import pandas as pd
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from src.agents import OrchestratorAgent, Message
from src.core.config import get_settings
from src.core.planner import CampaignPlanner


def _serialize_dataframes(obj: Any) -> Any:
    """
    Recursively convert any Pandas DataFrames in the object to dictionaries.
    
    Args:
        obj: Object that may contain DataFrames
        
    Returns:
        Object with DataFrames converted to dictionaries
    """
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, dict):
        return {key: _serialize_dataframes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_dataframes(item) for item in obj]
    else:
        return obj


class CampaignService:
    """
    Service layer for campaign management.

    Responsibilities:
    - Accept campaign creation requests
    - Create execution plans via CampaignPlanner
    - Orchestrate multi-agent workflow asynchronously
    - Return structured results
    """

    def __init__(self):
        """Initialize campaign service."""
        settings = get_settings()

        # Get planner singleton
        self.planner = CampaignPlanner.get_instance()

        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent(config={})

        # Thread pool for async execution
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Get the path components from configuration
        data_location = settings._config.get('connectors', {}).get('csv', {}).get('location', './data')
        campaigns_file = settings._config.get('data', {}).get('sources', {}).get('campaigns', 'campaigns.csv')

        # Construct the full path
        self._campaigns_file = Path(data_location) / campaigns_file
        self._required_fields = ['campaign_id', 'name', 'goal', 'target_criteria', 'segment_size', 'created_at', 'status']

    def _generate_campaign_name(self, goal: str) -> str:
        """
        Generate an intelligent campaign name based on the goal.
        
        Args:
            goal: The campaign goal text
            
        Returns:
            Generated campaign name
        """
        # Extract key terms from the goal for naming
        goal_lower = goal.lower()
        
        # Define patterns and their corresponding campaign name components
        patterns = {
            'retention': ['retention', 'retain', 'keep', 'maintain'],
            'acquisition': ['acquisition', 'acquire', 'new', 'recruit', 'find'],
            'upsell': ['upsell', 'upgrade', 'premium', 'enhance', 'expand'],
            'winback': ['winback', 'win back', 're-engage', 'reactivate'],
            'growth': ['growth', 'grow', 'increase', 'boost', 'improve'],
            'high-value': ['high-value', 'high value', 'premium', 'vip', 'elite'],
            'satisfaction': ['satisfaction', 'nps', 'happy', 'satisfied'],
            'performance': ['performance', 'sales', 'policies', 'productivity'],
            'q4': ['q4', 'quarter 4', 'fourth quarter'],
            'q3': ['q3', 'quarter 3', 'third quarter'],
            'q2': ['q2', 'quarter 2', 'second quarter'],
            'q1': ['q1', 'quarter 1', 'first quarter']
        }
        
        # Extract relevant terms
        detected_terms = []
        for term_type, keywords in patterns.items():
            if any(keyword in goal_lower for keyword in keywords):
                detected_terms.append(term_type)
        
        # Generate name based on detected terms
        if detected_terms:
            # Use the most relevant terms
            primary_term = detected_terms[0].title()
            secondary_term = detected_terms[1] if len(detected_terms) > 1 else ""
            
            if secondary_term:
                name = f"{primary_term} {secondary_term.title()} Campaign"
            else:
                name = f"{primary_term} Campaign"
        else:
            # Fallback to a generic name with date
            name = f"Marketing Campaign {datetime.now().strftime('%Y-%m-%d')}"
        
        # Add context if it's about agents
        if 'agent' in goal_lower:
            name = f"Agent {name}"
        
        return name

    def _persist_campaign(self, campaign_data: Dict[str, Any]) -> None:
        """
        Persist a campaign to CSV storage.
        
        Args:
            campaign_data: Campaign data to persist
            
        Raises:
            ValueError: If campaign data is missing required fields
        """
        # Validate required fields
        missing_fields = [field for field in self._required_fields if field not in campaign_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Ensure target_criteria is JSON string
        if isinstance(campaign_data['target_criteria'], dict):
            campaign_data['target_criteria'] = json.dumps(campaign_data['target_criteria'])
        
        # Create DataFrame for new campaign
        new_campaign_df = pd.DataFrame([campaign_data])
        
        if self._campaigns_file.exists():
            # Append to existing file
            new_campaign_df.to_csv(self._campaigns_file, mode='a', header=False, index=False)
        else:
            # Create new file with headers
            new_campaign_df.to_csv(self._campaigns_file, index=False)

    def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """
        Retrieve all existing campaigns.

        Returns:
            List of campaign records with their details

        Example:
            >>> service = CampaignService()
            >>> campaigns = service.get_all_campaigns()
            >>> print(f"Found {len(campaigns)} campaigns")
        """
        try:
            # Read campaigns CSV from the instance path
            if not self._campaigns_file.exists():
                return []
                
            # Read campaigns CSV with error handling
            try:
                df = pd.read_csv(
                    self._campaigns_file,
                    delimiter=',',
                    quotechar='"',
                    escapechar='\\',
                    on_bad_lines='skip',  # Skip malformed lines instead of failing
                    low_memory=False
                )
            except Exception as csv_error:
                # If pandas fails, try with more lenient settings
                df = pd.read_csv(
                    self._campaigns_file,
                    delimiter=',',
                    quotechar='"',
                    on_bad_lines='skip',
                    engine='python',  # Use Python engine for better error handling
                    low_memory=False
                )
            
            # Convert DataFrame to list of dicts
            campaigns = df.to_dict('records')
            
            # Parse JSON strings in target_criteria to actual dictionaries
            for campaign in campaigns:
                if isinstance(campaign['target_criteria'], str):
                    campaign['target_criteria'] = json.loads(campaign['target_criteria'])
            
            # Serialize any DataFrames to prevent Pydantic serialization errors
            campaigns = _serialize_dataframes(campaigns)
            
            return campaigns
        except Exception as e:
            raise Exception(f"Error reading campaigns: {str(e)}")

    def create_campaign(self, goal: str, campaign_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new campaign plan and start execution asynchronously.

        Args:
            goal: Natural language campaign goal
            campaign_name: Optional custom campaign name. If not provided, will be generated.

        Returns:
            Campaign creation response with campaign_id and plan (execution starts in background)

        Example:
            >>> service = CampaignService()
            >>> result = service.create_campaign(
            ...     goal="Find high-value agents with excellent satisfaction",
            ...     campaign_name="VIP Retention Campaign"
            ... )
            >>> print(result['campaign_id'])  # Returns immediately
            >>> print(result['status'])        # 'pending'
        """
        # Generate campaign name if not provided
        if not campaign_name or campaign_name.strip() == "":
            campaign_name = self._generate_campaign_name(goal)

        # Create plan via CampaignPlanner
        campaign_id, plan = self.planner.create_plan(goal, campaign_name)

        # Start async execution in background
        self.executor.submit(self._execute_campaign_async, campaign_id)

        # Return immediately with campaign_id and pending status
        return {
            "success": True,
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "goal": goal,
            "status": "pending",
            "created_at": plan.created_at.isoformat(),
            "plan": [step.to_dict() for step in plan.steps],
            "message": "Campaign execution started in background"
        }

    def _execute_campaign_async(self, campaign_id: str) -> None:
        """
        Execute campaign in background (called by ThreadPoolExecutor).

        Args:
            campaign_id: Campaign identifier
        """
        try:
            # Update plan status to executing
            self.planner.update_plan_status(campaign_id, "executing")

            # Create message for orchestrator with campaign_id
            message = Message(
                sender="CampaignService",
                recipient="Orchestrator",
                content={"campaign_id": campaign_id},
                message_type="execute_plan"
            )

            # Execute via orchestrator (respects BaseAgent interface)
            result = self.orchestrator.process(message)

            # If successful, persist campaign to CSV
            if result.get('success'):
                plan = self.planner.get_plan(campaign_id)
                if plan:
                    campaign_data = {
                        'campaign_id': campaign_id,
                        'name': plan.campaign_name,
                        'goal': plan.goal,
                        'target_criteria': plan.results.get('GoalParser', {}).get('criteria', {}),
                        'segment_size': plan.results.get('SegmentationAgent', {}).get('segmentation', {}).get('filtered_agents', 0),
                        'created_at': plan.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'status': 'planned'
                    }

                    try:
                        self._persist_campaign(campaign_data)
                    except Exception as e:
                        print(f"Warning: Campaign execution succeeded but persistence failed: {str(e)}")

        except Exception as e:
            # Mark plan as failed
            self.planner.update_plan_status(campaign_id, "failed", error=str(e))
            print(f"Campaign {campaign_id} execution failed: {str(e)}")

    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get current execution status of a campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Campaign status with plan details
        """
        return self.planner.get_plan_status(campaign_id)
