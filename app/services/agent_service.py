from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import RouterAgent, SupportAgent, OrderAgent, BillingAgent

class AgentService:
    """
    Agent Service - Orchestrates multi-agent system.
    Routes queries to appropriate agents and manages conversation flow.
    """

    def __init__(self, db:AsyncSession):
        self.db = db
        self.router = RouterAgent(db)
        self.agents = {
            "support":SupportAgent(db),
            "order":OrderAgent(db),
            "billing":BillingAgent(db)
        }
    async def process_message(self,message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process user message through multi-agent system.
        
        Flow:
        1. Router analyzes query
        2. Routes to appropriate specialist agent
        3. Specialist agent processes with tools
        4. Returns response
        
        Args:
            message: User's message
            conversation_history: Previous messages
            
        Returns:
            Response dict with content and metadata
        """

        try:
            #step 1: route the query
            routing_decision = await self.router.route(message, conversation_history)
            agent_type = routing_decision["agent"]
            confidence = routing_decision["confidence"]
            reasoning = routing_decision["reasoning"]

            #step 2: get the appropriate agent
            agent = self.agents.get(agent_type, self.agents["support"])

            #step 3: process wih specialist agent
            response = await agent.process(message, conversation_history)

            #step4: add routing metadata
            response["routing"] = {
                "selected_agent": agent_type,
                "confidence":confidence,
                "reasoning":reasoning
            }

            return response

        
        except Exception as e:
            #fallback to support agent on error
            return {
                "content": "I apologize, but I encountered an error processing your request. How can I help you?",
                "agent": "support",
                "error": str(e),
                "routing": {
                    "selected_agent": "support",
                    "confidence": 0.0,
                    "reasoning": "Error fallback"
                }
            
            }
    
    def get_agent_info(self, agent_type: str = None) -> Dict[str, Any]:
        """
        Get information about available agents.
        
        Args:
            agent_type: Specific agent or None for all
            
        Returns:
            Agent information
        """
        if agent_type:
            agent = self.agents.get(agent_type)
            if not agent:
                return {"error":f"Agent {agent_type} not found"}
            return {
                "name":agent.name,
                "description":agent.description,
                "tools": [tool.name for tool in agent.get_tools()]
            }

        #return all agents
        return {
            "agents":[
                {
                    "name":agent.name,
                    "description":agent.description,
                    "tools":[tool.name for tool in agent.get_tools()]
                }
                for agent in self.agents.values()
            ]
        }