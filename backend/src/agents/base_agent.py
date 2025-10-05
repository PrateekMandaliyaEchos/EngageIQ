"""Base agent class for EngageIQ multi-agent system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Message:
    """Message passed between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    message_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"Message(from={self.sender}, to={self.recipient}, type={self.message_type})"


class BaseAgent(ABC):
    """Abstract base class for all agents in EngageIQ."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent.

        Args:
            name: Agent name/identifier
            config: Agent configuration from config.yaml
        """
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)

    @abstractmethod
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Process a message and return result.

        Args:
            message: Input message to process

        Returns:
            Processing result as dictionary
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
