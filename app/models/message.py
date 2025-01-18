from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from app.schemas.common import MessageRole, AgentType

class Message(Base):
    """
    Messagle table : conversation individula messages
    """
    __tablename__ = "messages"

    #primary key
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)

    #foreign key
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)

    #message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    #agent info
    agent_type = Column(SQLEnum(AgentType), nullable=True)

    #tool calls (agar agent ne koi tool use kiya)
    # Example: [{"tool": "fetch_order", "params": {"order_number": "12345"}}]
    tool_calls = Column(JSONB, nullable=True)

    # Metadata (confidence score, reasoning, etc.)
    extra_data = Column(JSONB, nullable=True)

    #timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    #relationship
    conversation = relationship("Conversation", back_populates="messages")


    def __repr__(self):
        return f"<Message {self.role} - {self.content[:30]}"
