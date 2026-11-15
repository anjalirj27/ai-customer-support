import logging
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.common import OrderStatus
from app.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

# Orders can only be changed before they ship
MODIFIABLE_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}


async def _get_order(db: AsyncSession, order_number: str) -> Optional[Order]:
    result = await db.execute(select(Order).where(Order.order_number == order_number))
    return result.scalar_one_or_none()


def _iso(value) -> Optional[str]:
    return value.isoformat() if value else None


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
            order = await _get_order(self.db, order_number)

            if not order:
                return ToolResult(success=False, error=f"Order {order_number} not found")

            return ToolResult(success=True, data={
                "order_number": order.order_number,
                "status": order.status.value,
                "items": order.items,
                "total_amount": order.total_amount,
                "tracking_number": order.tracking_number,
                "estimated_delivery": _iso(order.estimated_delivery)
            })
        except Exception:
            logger.exception("fetch_order_details failed for %s", order_number)
            return ToolResult(success=False, error="Could not retrieve order details")


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
                "order_number": {"type": "string", "description": "Order number"}
            },
            "required": ["order_number"]
        }

    async def execute(self, order_number: str) -> ToolResult:
        try:
            order = await _get_order(self.db, order_number)

            if not order:
                return ToolResult(success=False, error="Order not found")

            return ToolResult(success=True, data={
                "status": order.status.value,
                "tracking_number": order.tracking_number,
                "estimated_delivery": _iso(order.estimated_delivery)
            })
        except Exception:
            logger.exception("check_delivery_status failed for %s", order_number)
            return ToolResult(success=False, error="Could not retrieve delivery status")


class ModifyOrderTool(BaseTool):
    """Modifies order"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def name(self) -> str:
        return "modify_order"

    @property
    def description(self) -> str:
        return (
            "Updates the shipping address of an order. Only works for PENDING or "
            "CONFIRMED orders. Item changes are not supported."
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string", "description": "Order number"},
                "modifications": {
                    "type": "object",
                    "description": "Fields to change. Supported: shipping_address (object)",
                    "properties": {
                        "shipping_address": {"type": "object"}
                    }
                }
            },
            "required": ["order_number", "modifications"]
        }

    async def execute(self, order_number: str, modifications: Dict) -> ToolResult:
        try:
            order = await _get_order(self.db, order_number)

            if not order:
                return ToolResult(success=False, error=f"Order {order_number} not found")

            if order.status not in MODIFIABLE_STATUSES:
                return ToolResult(
                    success=False,
                    error=f"Order cannot be modified because it is {order.status.value}"
                )

            unsupported = set(modifications) - {"shipping_address"}
            new_address = modifications.get("shipping_address")
            if unsupported or not isinstance(new_address, dict) or not new_address:
                return ToolResult(
                    success=False,
                    error="Only shipping_address changes are supported"
                )

            # Assign a new dict so SQLAlchemy detects the JSONB change
            order.shipping_address = {**(order.shipping_address or {}), **new_address}
            await self.db.commit()

            return ToolResult(success=True, data={
                "message": "Shipping address updated",
                "order_number": order.order_number,
                "shipping_address": order.shipping_address
            })
        except Exception:
            await self.db.rollback()
            logger.exception("modify_order failed for %s", order_number)
            return ToolResult(success=False, error="Could not modify the order")


class CancelOrderTool(BaseTool):
    """Cancels order"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def name(self) -> str:
        return "cancel_order"

    @property
    def description(self) -> str:
        return "Cancels order (only if PENDING or CONFIRMED, i.e. not shipped)"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {"type": "string", "description": "Order number"},
                "reason": {"type": "string", "description": "Why the customer is cancelling"}
            },
            "required": ["order_number"]
        }

    async def execute(self, order_number: str, reason: Optional[str] = None) -> ToolResult:
        try:
            order = await _get_order(self.db, order_number)

            if not order:
                return ToolResult(success=False, error=f"Order {order_number} not found")

            if order.status == OrderStatus.CANCELLED:
                return ToolResult(success=False, error="Order is already cancelled")

            if order.status not in MODIFIABLE_STATUSES:
                return ToolResult(
                    success=False,
                    error=f"Order cannot be cancelled because it is {order.status.value}"
                )

            order.status = OrderStatus.CANCELLED
            await self.db.commit()
            logger.info("Order %s cancelled (reason: %s)", order_number, reason or "not given")

            return ToolResult(success=True, data={
                "message": "Order cancelled",
                "order_number": order.order_number,
                "status": order.status.value
            })
        except Exception:
            await self.db.rollback()
            logger.exception("cancel_order failed for %s", order_number)
            return ToolResult(success=False, error="Could not cancel the order")
