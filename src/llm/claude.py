"""Claude LLM provider implementation using LangChain."""

import json
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

from .base_provider import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Claude (Anthropic) LLM provider using LangChain."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Claude provider.

        Args:
            config: Provider configuration from config.yaml
        """
        super().__init__(config)
        self.validate_config()

        # Initialize LangChain ChatAnthropic
        self.client = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

    def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Send a query to Claude and get response.

        Args:
            prompt: The prompt to send
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Claude's response as string
        """
        # Create a new client instance with overridden parameters if provided
        client = self.client
        if temperature is not None or max_tokens is not None:
            client = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )

        # Build messages
        messages = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))

        # Invoke the model
        response = client.invoke(messages)

        return response.content

    def query_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a query expecting JSON response using LangChain's JSON parser.

        Args:
            prompt: The prompt to send
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response as dictionary
        """
        # Create client with JSON output parser
        client = self.client
        if temperature is not None or max_tokens is not None:
            client = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )

        # Create JSON output parser
        json_parser = JsonOutputParser()

        # Create chain: client | parser
        chain = client | json_parser

        # Build messages
        messages = []
        if system:
            messages.append(SystemMessage(content=system))

        # Add format instructions from parser
        format_instructions = json_parser.get_format_instructions()
        full_prompt = f"{prompt}\n\n{format_instructions}"
        messages.append(HumanMessage(content=full_prompt))

        # Invoke chain
        result = chain.invoke(messages)

        return result
