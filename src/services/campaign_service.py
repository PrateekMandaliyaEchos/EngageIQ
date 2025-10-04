"""Campaign service for managing campaign creation and orchestration."""

import json
import pandas as pd
import uuid
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from src.agents import OrchestratorAgent, Message
from src.core.config import get_settings


class CampaignService:
    """
    Service layer for campaign management.

    Responsibilities:
    - Accept campaign creation requests
    - Orchestrate multi-agent workflow
    - Return structured results
    """

    def __init__(self):
        """Initialize campaign service."""
        self.orchestrator = OrchestratorAgent(config={})
        self._campaigns_file = Path(get_settings().data.connectors.csv.location) / get_settings().data.sources.campaigns
        self._required_fields = ['campaign_id', 'name', 'goal', 'target_criteria', 'segment_size', 'created_at', 'status']

    def _generate_campaign_id(self) -> str:
        """Generate a unique campaign ID."""
        # Get existing campaign IDs
        existing_ids = set()
        if self._campaigns_file.exists():
            df = pd.read_csv(self._campaigns_file)
            existing_ids = set(df['campaign_id'].values)
        
        # Generate new ID until we find an unused one
        while True:
            new_id = f"CAM{str(uuid.uuid4())[:6].upper()}"
            if new_id not in existing_ids:
                return new_id

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
        settings = get_settings()
        campaigns_file = f"{settings.data.connectors.csv.location}/{settings.data.sources.campaigns}"
        
        try:
            # Read campaigns CSV
            df = pd.read_csv(campaigns_file)
            
            # Convert DataFrame to list of dicts
            campaigns = df.to_dict('records')
            
            # Parse JSON strings in target_criteria to actual dictionaries
            for campaign in campaigns:
                if isinstance(campaign['target_criteria'], str):
                    campaign['target_criteria'] = json.loads(campaign['target_criteria'])
            
            return campaigns
        except Exception as e:
            raise Exception(f"Error reading campaigns: {str(e)}")

    def create_campaign(self, goal: str) -> Dict[str, Any]:
        """
        Create a new campaign from user goal and persist it.

        Args:
            goal: Natural language campaign goal

        Returns:
            Campaign creation result with plan and results

        Example:
            >>> service = CampaignService()
            >>> result = service.create_campaign(
            ...     goal="Find high-value agents with excellent satisfaction"
            ... )
            >>> print(result['success'])
            >>> print(result['plan'])
            >>> print(result['results'])
        """
        # Create message for orchestrator
        message = Message(
            sender="CampaignService",
            recipient="Orchestrator",
            content={"goal": goal},
            message_type="create_campaign"
        )

        # Execute orchestration and get results
        result = self.orchestrator.process(message)
        
        if result.get('success'):
            # Prepare campaign data for persistence
            campaign_data = {
                'campaign_id': self._generate_campaign_id(),
                'name': result.get('name', f"Campaign {datetime.now().strftime('%Y-%m-%d')}"),
                'goal': goal,
                'target_criteria': result.get('results', {}).get('criteria', {}),
                'segment_size': result.get('results', {}).get('segment_size', 0),
                'created_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'status': 'completed' if result.get('success') else 'failed'
            }
            
            try:
                self._persist_campaign(campaign_data)
                result['campaign_id'] = campaign_data['campaign_id']
            except Exception as e:
                result['warning'] = f"Campaign created but persistence failed: {str(e)}"
        
        return result
