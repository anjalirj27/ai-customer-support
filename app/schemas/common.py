from enum import Enum

class MessageRole(str, Enum):
    """Message kaun bhej raha hai"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AgentType(str, Enum):
    """Kaun sa agent query handle kar raha hai"""
    ROUTER = "router"
    SUPPORT = "support"
    ORDER = "order"
    BILLING = "billing"


class ConversationStatus(str, Enum):
    """Conversation ka status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class OrderStatus(str, Enum):
    """Order ka status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    """Payment ka status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"