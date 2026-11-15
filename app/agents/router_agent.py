import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.tools.base_tool import BaseTool
from app.core.ai_client import ai_client
from app.core.config import settings

logger = logging.getLogger(__name__)

VALID_AGENTS = {"support", "order", "billing"}
DEFAULT_AGENT = "support"


class RouterAgent(BaseAgent):
    """
    Router Agent - Analyzes queries and routes to appropriate specialist agent.
    This is the 'brain' that decides which agent should handle each query.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    @property
    def name(self) -> str:
        return "router"
    
    @property
    def description(self) -> str:
        return "Analyzes customer queries and routes to appropriate specialist agent"
    
    @property
    def system_prompt(self) -> str:
        return """You are a routing agent for a customer support system.

Your job is to analyze the customer's query and determine which specialist agent should handle it:

1. **SUPPORT Agent** - For:
   - General questions and FAQs
   - Account issues
   - How-to questions
   - Policy questions
   - Anything that doesn't fit other categories

2. **ORDER Agent** - For:
   - Order status inquiries
   - Tracking information
   - Order modifications
   - Order cancellations
   - Shipping questions
   - Delivery estimates

3. **BILLING Agent** - For:
   - Payment issues
   - Invoice inquiries
   - Refund requests
   - Subscription questions
   - Pricing questions

Respond with ONLY a JSON object in this exact format:
{
    "agent": "support" | "order" | "billing",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}

Do not include any other text or markdown formatting."""
    
    def get_tools(self) -> List[BaseTool]:
        """Router doesn't use tools, it just classifies"""
        return []
    
    async def route(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze message and determine which agent should handle it.

        Args:
            message: User's message
            conversation_history: Previous messages for context

        Returns:
            Dict with routing decision
        """
        conversation_history = conversation_history or []

        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add recent context (last 5 messages)
        messages.extend(conversation_history[-5:])
        messages.append({"role": "user", "content": message})

        try:
            response = await self.ai_client.chat.completions.create(
                model=settings.ai_model,
                messages=messages,
                temperature=0.3,  # Lower temp for consistent routing
                max_tokens=200
            )

            return parse_routing_decision(response.choices[0].message.content)

        except Exception as e:
            logger.warning("Routing failed, defaulting to support agent: %s", e)
            return {
                "agent": DEFAULT_AGENT,
                "confidence": 0.5,
                "reasoning": "Routing error, defaulting to support"
            }


def parse_routing_decision(raw: Optional[str]) -> Dict[str, Any]:
    """
    Parse the router model's JSON reply into a validated routing decision.

    Tolerates markdown code fences, and falls back to the support agent when the
    reply is not valid JSON or names an unknown agent.
    """
    content = (raw or "").strip()

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return {
            "agent": DEFAULT_AGENT,
            "confidence": 0.5,
            "reasoning": "Unparseable routing response, defaulting to support"
        }

    if not isinstance(result, dict):
        result = {}

    agent = str(result.get("agent", DEFAULT_AGENT)).strip().lower()
    if agent not in VALID_AGENTS:
        agent = DEFAULT_AGENT

    try:
        confidence = min(max(float(result.get("confidence", 0.5)), 0.0), 1.0)
    except (TypeError, ValueError):
        confidence = 0.5

    return {
        "agent": agent,
        "confidence": confidence,
        "reasoning": str(result.get("reasoning", ""))
    }
