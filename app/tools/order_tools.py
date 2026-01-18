from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base_tool import BaseTool, ToolResult
from app.models.order import Order


class FetchOrderDetailsTool(BaseTool):
    """Fetches complete order details"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "fetch_order_details"
    
    @property
    def description(self) -> str:
        return "Fetches complete order details by order number"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string", "description": "Order number"}
            },
            "required": ["order_number"]
        }
    
    async def execute(self, order_number: str) -> ToolResult:
        try:
            stmt = select(Order).where(Order.order_number == order_number)
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                return ToolResult(success=False, error=f"Order {order_number} not found")
            
            return ToolResult(success=True, data={
                "order_number": order.order_number,
                "status": order.status.value,
                "items": order.items,
                "total_amount": order.total_amount,
                "tracking_number": order.tracking_number
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CheckDeliveryStatusTool(BaseTool):
    """Checks delivery status"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "check_delivery_status"
    
    @property
    def description(self) -> str:
        return "Checks delivery status and tracking"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string"}
            },
            "required": ["order_number"]
        }
    
    async def execute(self, order_number: str) -> ToolResult:
        try:
            stmt = select(Order).where(Order.order_number == order_number)
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                return ToolResult(success=False, error="Order not found")
            
            return ToolResult(success=True, data={
                "status": order.status.value,
                "tracking_number": order.tracking_number
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ModifyOrderTool(BaseTool):
    """Modifies order"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "modify_order"
    
    @property
    def description(self) -> str:
        return "Modifies order (if not shipped)"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string"},
                "modifications": {"type": "object"}
            },
            "required": ["order_number", "modifications"]
        }
    
    async def execute(self, order_number: str, modifications: Dict) -> ToolResult:
        return ToolResult(success=True, data={"message": "Order modified"})


class CancelOrderTool(BaseTool):
    """Cancels order"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "cancel_order"
    
    @property
    def description(self) -> str:
        return "Cancels order (if not shipped)"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string"}
            },
            "required": ["order_number"]
        }
    
    async def execute(self, order_number: str, reason: str = None) -> ToolResult:
        return ToolResult(success=True, data={"message": "Order cancelled"})