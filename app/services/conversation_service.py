from typing import Dict, List, Optional, Union
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.common import ConversationStatus, MessageRole


IdLike = Union[str, uuid.UUID]


def _as_uuid(value: IdLike) -> uuid.UUID:
    """Accept either a UUID or its string form (raises ValueError if malformed)"""
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class ConversationService:
    """Service for managing conversations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(
        self, 
        user_id: IdLike,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=_as_uuid(user_id),
            title=title or "New Conversation",
            status=ConversationStatus.ACTIVE
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation
    
    async def get_conversation(self, conversation_id: IdLike) -> Optional[Conversation]:
        """Get conversation by ID"""
        stmt = select(Conversation).where(Conversation.id == _as_uuid(conversation_id))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_conversations(
        self, 
        user_id: IdLike,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == _as_uuid(user_id))
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_conversation_messages(
        self, 
        conversation_id: IdLike
    ) -> List[Message]:
        """Get all messages in a conversation"""
        stmt = (
            select(Message)
            .where(Message.conversation_id == _as_uuid(conversation_id))
            .order_by(Message.created_at)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_message_counts(
        self,
        conversation_ids: List[uuid.UUID]
    ) -> Dict[uuid.UUID, int]:
        """Get the number of messages for each of the given conversations"""
        if not conversation_ids:
            return {}

        stmt = (
            select(Message.conversation_id, func.count(Message.id))
            .where(Message.conversation_id.in_(conversation_ids))
            .group_by(Message.conversation_id)
        )
        result = await self.db.execute(stmt)
        return {conv_id: count for conv_id, count in result.all()}

    async def add_message(
        self,
        conversation_id: IdLike,
        role: MessageRole,
        content: str,
        agent_type: Optional[str] = None,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """Add a message to conversation"""
        message = Message(
            conversation_id=_as_uuid(conversation_id),
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
    
    async def delete_conversation(self, conversation_id: IdLike) -> bool:
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
        stmt = select(User).order_by(User.created_at).limit(1)
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