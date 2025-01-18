from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class User(Base):
    """
    User table - Customer details
    """
    __tablename__ = "users"

    #primary key
    id = Column(UUID(as_uuid = True), primary_key= True, default = uuid.uuid4)

    #user info
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    #timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (ek user ke multiple conversations ho sakte hain)
    conversations = relationship("Conversation", back_populates = "user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"