"""Goal Parser Agent - Extracts structured criteria from natural language campaign goals."""

from typing import Dict, Any

from src.agents.base_agent import BaseAgent, Message
from src.core.config import get_settings
from src.llm import ClaudeProvider


class GoalParserAgent(BaseAgent):
    """
    Goal Parser Agent that converts natural language campaign goals
    into structured criteria for segmentation.

    Input: Natural language goal (e.g., "Find high-value agents with good satisfaction")
    Output: Structured criteria with constraints, objective, target size
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize goal parser agent.

        Args:
            config: Agent configuration from config.yaml
        """
        settings = get_settings()
        agent_config = settings.get_agent_config('goal_parser')
        super().__init__("GoalParser", agent_config)

        # Get LLM provider configuration
        llm_provider_name = agent_config.get('provider', settings.llm_default_provider)
        llm_config = settings.get_llm_config(llm_provider_name)

        # Override temperature if specified in agent config
        if 'temperature' in agent_config:
            llm_config['temperature'] = agent_config['temperature']

        # Initialize LLM provider
        self.llm = ClaudeProvider(llm_config)

    def process(self, message: Message) -> Dict[str, Any]:
        """
        Parse natural language goal into structured criteria.

        Args:
            message: Message containing 'goal' in content

        Returns:
            Dictionary with structured criteria
        """
        goal = message.content.get('goal', '')

        if not goal:
            raise ValueError("No goal provided in message")

        # Create prompt for LLM
        prompt = self._build_prompt(goal)

        # Query LLM for structured output
        criteria = self.llm.query_json(
            prompt=prompt,
            system="You are an expert at analyzing marketing campaign goals and extracting structured criteria for customer segmentation."
        )

        return criteria

    def _build_prompt(self, goal: str) -> str:
        """
        Build prompt for LLM to extract structured criteria.

        Args:
            goal: Natural language campaign goal

        Returns:
            Formatted prompt
        """
        prompt = f"""
Analyze this campaign goal and extract structured segmentation criteria:

GOAL: "{goal}"

Extract the following information and return as JSON:

1. **objective**: The campaign type (retention, acquisition, upsell, winback, engagement)
2. **constraints**: Array of filtering criteria with:
   - field: The data field to filter on (e.g., AUM_SELFREPORTED, NPS_SCORE, AGENT_TENURE)
   - operator: Comparison operator (>, >=, <, <=, ==, !=)
   - value: The threshold value (number or string)
3. **target_size**: Desired segment size (number or range)
4. **priority**: Preference for segment quality (quality_over_quantity, balanced, quantity_over_quality)

Available fields for constraints:
- AUM_SELFREPORTED (numeric): Assets under management
- NPS_SCORE (numeric 0-10): Net Promoter Score
- AGENT_TENURE (numeric): Years with company
- NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS (numeric): Policies sold
- COMPLAINTS_LAST_12_MONTHS (numeric): Number of complaints
- PREMIUM_AMOUNT (numeric): Premium amount generated
- Age (numeric): Agent age
- Segment (string): Agent segment (Independent Agents, Emerging Experts, etc.)

Guidelines for interpretation:
- "high-value" or "top performers" → AUM > 75th percentile
- "good/excellent satisfaction" → NPS_SCORE >= 8
- "poor satisfaction" or "at-risk" → NPS_SCORE <= 6
- "active" or "productive" → NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS >= 5
- "veteran" or "experienced" → AGENT_TENURE >= 10
- "new" or "recent" → AGENT_TENURE < 2
- "high premium" or "premium generators" → PREMIUM_AMOUNT > 75th percentile
- "low premium" or "underperforming" → PREMIUM_AMOUNT < 25th percentile

Return ONLY valid JSON with this structure:
{{
  "objective": "retention|acquisition|upsell|winback|engagement",
  "constraints": [
    {{"field": "FIELD_NAME", "operator": ">", "value": NUMBER}},
    {{"field": "FIELD_NAME", "operator": ">=", "value": NUMBER}}
  ],
  "target_size": 100,
  "priority": "quality_over_quantity|balanced|quantity_over_quality"
}}
"""
        return prompt
