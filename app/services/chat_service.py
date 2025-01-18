from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_service import AgentService
from app.services.conversation_service import ConversationService
from app.schemas.common import MessageRole, AgentType


class ChatService:
    """Main service for handling chat interactions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agent_service = AgentService(db)
        self.conversation_service = ConversationService(db)
    
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the multi-agent system.
        
        Args:
            message: User's message
            conversation_id: Existing conversation or None for new
            user_id: User ID or None for default user
            
        Returns:
            Dict with response and metadata
        """
        # Get or create user
        if not user_id:
            user = await self.conversation_service.get_or_create_default_user()
            user_id = str(user.id)
        
        # Get or create conversation
        if conversation_id:
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                conversation = await self.conversation_service.create_conversation(
                    user_id=user_id,
                    title="New Chat"
                )
        else:
            conversation = await self.conversation_service.create_conversation(
                user_id=user_id,
                title=message[:50]  # Use first 50 chars as title
            )
        
        conversation_id = str(conversation.id)
        
        # Save user message
        user_message = await self.conversation_service.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message
        )
        
        # Get conversation history for context
        messages = await self.conversation_service.get_conversation_messages(conversation_id)
        
        # Format history for AI (exclude current message)
        conversation_history = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages[:-1]  # Exclude the message we just added
        ]
        
        # Process through agents
        agent_response = await self.agent_service.process_message(
            message=message,
            conversation_history=conversation_history
        )
        
        # Determine agent type
        agent_type_str = agent_response.get("agent", "support")
        agent_type_map = {
            "router": AgentType.ROUTER,
            "support": AgentType.SUPPORT,
            "order": AgentType.ORDER,
            "billing": AgentType.BILLING
        }
        agent_type = agent_type_map.get(agent_type_str, AgentType.SUPPORT)
        
        # Save assistant message
        assistant_message = await self.conversation_service.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=agent_response["content"],
            agent_type=agent_type,
            tool_calls=agent_response.get("tool_calls")
        )
        
        return {
            "message_id": str(assistant_message.id),
            "conversation_id": conversation_id,
            "content": agent_response["content"],
            "agent": agent_response["agent"],
            "tool_calls": agent_response.get("tool_calls"),
            "routing": agent_response.get("routing")
        }