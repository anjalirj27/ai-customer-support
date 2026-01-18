from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from app.schemas.common import PaymentStatus


class Payment(Base):
    """
    Payment table - Billing/payment info (mock data)
    """
    __tablename__ = "payments"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Payment Details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(String(50), nullable=False)  # "credit_card", "upi", etc.
    description = Column(String(500), nullable=True)
    
    # Refund Info
    refund_amount = Column(Float, nullable=True, default=0.0)
    refund_reason = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.invoice_number} - {self.status}>"