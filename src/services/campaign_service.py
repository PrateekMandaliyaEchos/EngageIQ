"""Campaign service for managing campaign creation and orchestration."""

from typing import Dict, Any

from src.agents import OrchestratorAgent, Message


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

    def create_campaign(self, goal: str) -> Dict[str, Any]:
        """
        Create a new campaign from user goal.

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

        # Execute orchestration and return results
        return self.orchestrator.process(message)
