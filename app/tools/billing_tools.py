import logging
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.common import PaymentStatus
from app.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


async def _get_payment(db: AsyncSession, invoice_number: str) -> Optional[Payment]:
    result = await db.execute(select(Payment).where(Payment.invoice_number == invoice_number))
    return result.scalar_one_or_none()


class GetInvoiceDetailsTool(BaseTool):
    """Gets invoice details"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def name(self) -> str:
        return "get_invoice_details"

    @property
    def description(self) -> str:
        return "Fetches invoice/payment details"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string", "description": "Invoice number"}
            },
            "required": ["invoice_number"]
        }

    async def execute(self, invoice_number: str) -> ToolResult:
        try:
            payment = await _get_payment(self.db, invoice_number)

            if not payment:
                return ToolResult(success=False, error="Invoice not found")

            return ToolResult(success=True, data={
                "invoice_number": payment.invoice_number,
                "amount": payment.amount,
                "status": payment.status.value,
                "payment_method": payment.payment_method,
                "refund_amount": payment.refund_amount
            })
        except Exception:
            logger.exception("get_invoice_details failed for %s", invoice_number)
            return ToolResult(success=False, error="Could not retrieve invoice details")


class CheckRefundStatusTool(BaseTool):
    """Checks refund status"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def name(self) -> str:
        return "check_refund_status"

    @property
    def description(self) -> str:
        return "Checks if payment has been refunded"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string", "description": "Invoice number"}
            },
            "required": ["invoice_number"]
        }

    async def execute(self, invoice_number: str) -> ToolResult:
        try:
            payment = await _get_payment(self.db, invoice_number)

            if not payment:
                return ToolResult(success=False, error="Invoice not found")

            return ToolResult(success=True, data={
                "is_refunded": payment.status in (
                    PaymentStatus.REFUNDED,
                    PaymentStatus.PARTIALLY_REFUNDED
                ),
                "status": payment.status.value,
                "refund_amount": payment.refund_amount or 0.0,
                "refund_reason": payment.refund_reason
            })
        except Exception:
            logger.exception("check_refund_status failed for %s", invoice_number)
            return ToolResult(success=False, error="Could not retrieve refund status")


class ProcessRefundTool(BaseTool):
    """Processes refund"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    def name(self) -> str:
        return "process_refund"

    @property
    def description(self) -> str:
        return (
            "Processes a full or partial refund for a COMPLETED payment. "
            "Omit amount for a full refund."
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string", "description": "Invoice number"},
                "reason": {"type": "string", "description": "Reason for the refund"},
                "amount": {"type": "number", "description": "Amount to refund (optional)"}
            },
            "required": ["invoice_number", "reason"]
        }

    async def execute(
        self,
        invoice_number: str,
        reason: str,
        amount: Optional[float] = None
    ) -> ToolResult:
        try:
            payment = await _get_payment(self.db, invoice_number)

            if not payment:
                return ToolResult(success=False, error="Invoice not found")

            refundable_states = (PaymentStatus.COMPLETED, PaymentStatus.PARTIALLY_REFUNDED)
            if payment.status not in refundable_states:
                return ToolResult(
                    success=False,
                    error=f"Payment cannot be refunded because it is {payment.status.value}"
                )

            already_refunded = payment.refund_amount or 0.0
            remaining = round(payment.amount - already_refunded, 2)
            refund = remaining if amount is None else amount

            if refund <= 0:
                return ToolResult(success=False, error="Refund amount must be greater than zero")
            if refund > remaining:
                return ToolResult(
                    success=False,
                    error=f"Refund amount exceeds the refundable balance of {remaining}"
                )

            payment.refund_amount = round(already_refunded + refund, 2)
            payment.refund_reason = reason
            payment.status = (
                PaymentStatus.REFUNDED
                if payment.refund_amount >= payment.amount
                else PaymentStatus.PARTIALLY_REFUNDED
            )
            await self.db.commit()

            return ToolResult(success=True, data={
                "message": "Refund processed",
                "invoice_number": payment.invoice_number,
                "refunded_amount": refund,
                "total_refunded": payment.refund_amount,
                "status": payment.status.value
            })
        except Exception:
            await self.db.rollback()
            logger.exception("process_refund failed for %s", invoice_number)
            return ToolResult(success=False, error="Could not process the refund")
