from typing import List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.common import ConversationStatus, MessageRole


class ConversationService:
    """Service for managing conversations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(
        self, 
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation",
            status=ConversationStatus.ACTIVE
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_conversations(
        self, 
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_conversation_messages(
        self, 
        conversation_id: str
    ) -> List[Message]:
        """Get all messages in a conversation"""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        agent_type: Optional[str] = None,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """Add a message to conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_type=agent_type,
            tool_calls=tool_calls
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        conversation = await self.get_conversation(conversation_id)
        
        if not conversation:
            return False
        
        await self.db.delete(conversation)
        await self.db.commit()
        
        return True
    
    async def get_or_create_default_user(self) -> User:
        """Get or create a default user for testing"""
        # Try to find existing user
        stmt = select(User).limit(1)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        # Create default user
        user = User(
            email="demo@example.com",
            name="Demo User"
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user