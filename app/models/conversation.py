from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from app.schemas.common import ConversationStatus

class Conversation(Base):
    """
    Conversation table between customer and AI
    """

    __tablename__ = "conversations"

    #primary key
    id = Column(UUID(as_uuid = True),primary_key = True, default=uuid.uuid4)

    #foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    #conversation info
    title = Column(String(255), nullable=True)
    status = Column(
        SQLEnum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )

    # Metadata (extra info JSON format mein)
    # Example: {"sentiment": "positive", "agent_switches": 2}

    extra_data = Column(JSONB, nullable=True)

    #timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate = datetime.utcnow)

    #relationship
    user = relationship("User",back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Conversation {self.id} - {self.status}>"