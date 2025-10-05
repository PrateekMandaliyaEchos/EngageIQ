"""Data models for campaign planning."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class PlanStatus(Enum):
    """Campaign plan execution status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(Enum):
    """Individual step execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """Represents a single step in the execution plan."""
    step: int
    description: str
    agent_name: str
    active_form: str
    status: str = StepStatus.PENDING.value
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step": self.step,
            "description": self.description,
            "agent": self.agent_name,
            "active_form": self.active_form,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


@dataclass
class CampaignPlan:
    """Represents a complete campaign execution plan."""
    campaign_id: str
    campaign_name: str
    goal: str
    created_at: datetime
    status: str = PlanStatus.PENDING.value
    steps: List[PlanStep] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "goal": self.goal,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "steps": [step.to_dict() for step in self.steps],
            "error": self.error
        }

    def get_step(self, step_num: int) -> Optional[PlanStep]:
        """Get a specific step by number."""
        for step in self.steps:
            if step.step == step_num:
                return step
        return None
