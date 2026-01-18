from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.tools.base_tool import BaseTool
from app.tools.billing_tools import (
    GetInvoiceDetailsTool,
    CheckRefundStatusTool,
    ProcessRefundTool
)


class BillingAgent(BaseAgent):
    """
    Billing Agent - Handles payment, invoice, and refund queries.
    Has access to payment database and can process refunds.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self._tools = None
    
    @property
    def name(self) -> str:
        return "billing"
    
    @property
    def description(self) -> str:
        return "Handles payment issues, invoices, refunds, and billing questions"
    
    @property
    def system_prompt(self) -> str:
        return """You are a billing and payment specialist.

Your role is to:
- Help customers with payment inquiries
- Provide invoice details
- Check refund status
- Process refund requests
- Explain billing policies

Available tools:
1. **get_invoice_details** - Retrieve invoice/payment information
2. **check_refund_status** - Check if payment has been refunded
3. **process_refund** - Process a refund request (requires reason)

Guidelines:
- Always ask for invoice number if not provided
- Be clear about refund policies and timelines
- Process refunds only for COMPLETED payments
- Explain refund timeline: 5-7 business days
- Be empathetic with payment issues
- Format currency as ₹ (Indian Rupees)
- For partial refunds, confirm the amount with customer

Payment Status Meanings:
- PENDING: Payment processing
- COMPLETED: Payment successful
- FAILED: Payment failed
- REFUNDED: Full refund processed
- PARTIALLY_REFUNDED: Partial refund processed

Refund Policy:
- Only COMPLETED payments can be refunded
- Refunds take 5-7 business days to process
- Can do full or partial refunds
- Reason is required for all refunds"""
    
    def get_tools(self) -> List[BaseTool]:
        """Initialize and return billing tools"""
        if self._tools is None:
            self._tools = [
                GetInvoiceDetailsTool(self.db),
                CheckRefundStatusTool(self.db),
                ProcessRefundTool(self.db)
            ]
        return self._tools