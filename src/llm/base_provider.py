"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LLM provider with configuration.

        Args:
            config: Provider configuration from config.yaml
        """
        self.config = config
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', '')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)

    @abstractmethod
    def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a query to the LLM and get response.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM response as string
        """
        pass

    @abstractmethod
    def query_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a query expecting JSON response.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters

        Returns:
            Parsed JSON response as dictionary
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid
        """
        if not self.api_key:
            raise ValueError(f"API key not configured for {self.__class__.__name__}")
        if not self.model:
            raise ValueError(f"Model not configured for {self.__class__.__name__}")
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
