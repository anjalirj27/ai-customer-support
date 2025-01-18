from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.tools.base_tool import BaseTool
from app.core.ai_client import ai_client
from app.core.config import settings


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
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze message and determine which agent should handle it.
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            
        Returns:
            Dict with routing decision
        """
        if conversation_history is None:
            conversation_history = []
        
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
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            return {
                "agent": result.get("agent", "support"),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            # Default to support agent on error
            return {
                "agent": "support",
                "confidence": 0.5,
                "reasoning": f"Routing error, defaulting to support: {str(e)}"
            }