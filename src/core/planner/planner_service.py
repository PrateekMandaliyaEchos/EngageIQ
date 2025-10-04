"""Campaign planner for managing campaign execution plans."""

import threading
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.planner.models import CampaignPlan, PlanStep, PlanStatus, StepStatus


class CampaignPlanner:
    """
    Singleton planner for creating and managing campaign execution plans.

    Responsibilities:
    - Generate unique campaign IDs
    - Create execution plans (5 steps)
    - Store plans in memory
    - Track execution status
    - Thread-safe access to plans
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the campaign planner."""
        if self._initialized:
            return

        self.campaign_plans: Dict[str, CampaignPlan] = {}
        self.access_lock = threading.Lock()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'CampaignPlanner':
        """Get the singleton instance."""
        return cls()

    def create_plan(self, goal: str, campaign_name: Optional[str] = None) -> Tuple[str, CampaignPlan]:
        """
        Create a new campaign execution plan.

        Args:
            goal: Natural language campaign goal
            campaign_name: Optional campaign name

        Returns:
            Tuple of (campaign_id, plan)
        """
        # Generate unique campaign ID
        campaign_id = self._generate_campaign_id()

        # Generate campaign name if not provided
        if not campaign_name:
            campaign_name = f"Campaign {datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create plan steps
        steps = [
            PlanStep(
                step=1,
                description="Parse campaign goal and extract criteria",
                agent_name="GoalParser",
                active_form="Parsing campaign goal"
            ),
            PlanStep(
                step=2,
                description="Load agent population data from CSV files",
                agent_name="DataLoader",
                active_form="Loading agent data"
            ),
            PlanStep(
                step=3,
                description="Filter agents based on parsed criteria",
                agent_name="SegmentationAgent",
                active_form="Segmenting agent population"
            ),
            PlanStep(
                step=4,
                description="Generate comprehensive agent profiles and insights",
                agent_name="ProfileGeneratorAgent",
                active_form="Analyzing segment characteristics"
            ),
            PlanStep(
                step=5,
                description="Develop comprehensive campaign strategy and recommendations",
                agent_name="CampaignStrategistAgent",
                active_form="Creating campaign strategy"
            )
        ]

        # Create campaign plan
        plan = CampaignPlan(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            goal=goal,
            created_at=datetime.now(),
            status=PlanStatus.PENDING.value,
            steps=steps
        )

        # Store in memory
        with self.access_lock:
            self.campaign_plans[campaign_id] = plan

        return campaign_id, plan

    def get_plan(self, campaign_id: str) -> Optional[CampaignPlan]:
        """
        Get a campaign plan by ID.

        Args:
            campaign_id: Campaign identifier

        Returns:
            CampaignPlan if found, None otherwise
        """
        with self.access_lock:
            return self.campaign_plans.get(campaign_id)

    def update_step_status(
        self,
        campaign_id: str,
        step_num: int,
        status: str,
        result: Any = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update the status of a specific step.

        Args:
            campaign_id: Campaign identifier
            step_num: Step number (1-5)
            status: New status (pending, in_progress, completed, failed)
            result: Optional result data from step execution
            error: Optional error message if step failed

        Returns:
            True if updated successfully, False otherwise
        """
        with self.access_lock:
            plan = self.campaign_plans.get(campaign_id)
            if not plan:
                return False

            step = plan.get_step(step_num)
            if not step:
                return False

            # Update step status
            step.status = status

            if status == StepStatus.IN_PROGRESS.value:
                step.started_at = datetime.now()
            elif status in [StepStatus.COMPLETED.value, StepStatus.FAILED.value]:
                step.completed_at = datetime.now()

            if result is not None:
                step.result = result
                # Also store in plan-level results for easy access
                plan.results[step.agent_name] = result

            if error:
                step.error = error

            # Update plan status based on steps
            self._update_plan_status(plan)

            return True

    def update_plan_status(
        self,
        campaign_id: str,
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """
        Update the overall plan status.

        Args:
            campaign_id: Campaign identifier
            status: New status (pending, executing, completed, failed)
            error: Optional error message

        Returns:
            True if updated successfully, False otherwise
        """
        with self.access_lock:
            plan = self.campaign_plans.get(campaign_id)
            if not plan:
                return False

            plan.status = status
            if error:
                plan.error = error

            return True

    def get_plan_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get current status of a campaign plan.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Dictionary with plan status and details
        """
        with self.access_lock:
            plan = self.campaign_plans.get(campaign_id)
            if not plan:
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }

            return {
                "success": True,
                "campaign_id": plan.campaign_id,
                "campaign_name": plan.campaign_name,
                "goal": plan.goal,
                "status": plan.status,
                "created_at": plan.created_at.isoformat(),
                "steps": [step.to_dict() for step in plan.steps],
                "results": plan.results,
                "error": plan.error
            }

    def _generate_campaign_id(self) -> str:
        """Generate a unique campaign ID."""
        return f"CAM{str(uuid.uuid4())[:8].upper()}"

    def _update_plan_status(self, plan: CampaignPlan) -> None:
        """
        Update plan status based on step statuses.

        Args:
            plan: Campaign plan to update
        """
        # Check if any step is in progress
        if any(step.status == StepStatus.IN_PROGRESS.value for step in plan.steps):
            plan.status = PlanStatus.EXECUTING.value
            return

        # Check if any step failed
        if any(step.status == StepStatus.FAILED.value for step in plan.steps):
            plan.status = PlanStatus.FAILED.value
            return

        # Check if all steps completed
        if all(step.status == StepStatus.COMPLETED.value for step in plan.steps):
            plan.status = PlanStatus.COMPLETED.value
            return

        # Otherwise, it's still pending
        plan.status = PlanStatus.PENDING.value
