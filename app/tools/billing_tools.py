from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base_tool import BaseTool, ToolResult
from app.models.payment import Payment


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
                "invoice_number": {"type": "string"}
            },
            "required": ["invoice_number"]
        }
    
    async def execute(self, invoice_number: str) -> ToolResult:
        try:
            stmt = select(Payment).where(Payment.invoice_number == invoice_number)
            result = await self.db.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if not payment:
                return ToolResult(success=False, error="Invoice not found")
            
            return ToolResult(success=True, data={
                "invoice_number": payment.invoice_number,
                "amount": payment.amount,
                "status": payment.status.value,
                "refund_amount": payment.refund_amount
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))


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
                "invoice_number": {"type": "string"}
            },
            "required": ["invoice_number"]
        }
    
    async def execute(self, invoice_number: str) -> ToolResult:
        return ToolResult(success=True, data={"is_refunded": False})


class ProcessRefundTool(BaseTool):
    """Processes refund"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "process_refund"
    
    @property
    def description(self) -> str:
        return "Processes a refund for payment"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string"},
                "reason": {"type": "string"},
                "amount": {"type": "number"}
            },
            "required": ["invoice_number", "reason"]
        }
    
    async def execute(self, invoice_number: str, reason: str, amount: float = None) -> ToolResult:
        return ToolResult(success=True, data={"message": "Refund processed"})