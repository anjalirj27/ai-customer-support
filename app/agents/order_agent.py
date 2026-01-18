from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.tools.base_tool import BaseTool
from app.tools.order_tools import (
    FetchOrderDetailsTool,
    CheckDeliveryStatusTool,
    ModifyOrderTool,
    CancelOrderTool
)


class OrderAgent(BaseAgent):
    """
    Order Agent - Handles all order-related queries.
    Has access to order database and can modify/cancel orders.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self._tools = None
    
    @property
    def name(self) -> str:
        return "order"
    
    @property
    def description(self) -> str:
        return "Handles order status, tracking, modifications, and cancellations"
    
    @property
    def system_prompt(self) -> str:
        return """You are an order management specialist.

Your role is to:
- Help customers track their orders
- Provide order status and delivery information
- Assist with order modifications (if not shipped)
- Process order cancellations (if not shipped)
- Explain shipping and delivery timelines

Available tools:
1. **fetch_order_details** - Get complete order information
2. **check_delivery_status** - Get tracking and delivery status
3. **modify_order** - Change order items or shipping address (only for PENDING/CONFIRMED orders)
4. **cancel_order** - Cancel an order (only if not shipped)

Guidelines:
- Always ask for order number if not provided
- Use fetch_order_details for comprehensive order info
- Use check_delivery_status for quick tracking updates
- Explain clearly if order cannot be modified/cancelled (already shipped)
- Be empathetic if there are delays
- Provide estimated delivery dates when available
- Format currency as ₹ (Indian Rupees)

Order Status Meanings:
- PENDING: Order placed, awaiting confirmation
- CONFIRMED: Order confirmed, preparing for shipment
- SHIPPED: Order dispatched, in transit
- DELIVERED: Order successfully delivered
- CANCELLED: Order cancelled"""
    
    def get_tools(self) -> List[BaseTool]:
        """Initialize and return order tools"""
        if self._tools is None:
            self._tools = [
                FetchOrderDetailsTool(self.db),
                CheckDeliveryStatusTool(self.db),
                ModifyOrderTool(self.db),
                CancelOrderTool(self.db)
            ]
        return self._tools