from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from app.schemas.common import OrderStatus


class Order(Base):
    """
    Order table - Customer orders (mock data ke liye)
    """

    __tablename__  = "orders"

    #primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    #foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    #order details
    order_number = Column(String(50), unique=True, nullable=False,index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

      # Items (JSON format)
    # Example: [{"name": "Laptop", "quantity": 1, "price": 50000}]
    items = Column(JSONB, nullable=False)

    total_amount = Column(Float, nullable=False)

    #shipping info
    shipping_address = Column(JSONB, nullable=False)
    tracking_number = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)

    #timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"