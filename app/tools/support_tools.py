import logging
from typing import Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class QueryConversationHistoryTool(BaseTool):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "query_conversation_history"
    
    @property
    def description(self) -> str:
        return "Retrieves previous messages from conversation"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["conversation_id"]
        }
    
    async def execute(self, conversation_id: str, limit: int = 10) -> ToolResult:
        try:
            conv_id = UUID(str(conversation_id))
        except ValueError:
            return ToolResult(success=False, error="Invalid conversation_id")

        limit = max(1, min(int(limit), 50))

        try:
            # Newest first so the limit keeps the most recent messages
            stmt = (
                select(Message)
                .where(Message.conversation_id == conv_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            messages = list(reversed(result.scalars().all()))

            return ToolResult(success=True, data={
                "messages": [
                    {"role": m.role.value, "content": m.content}
                    for m in messages
                ]
            })
        except Exception:
            logger.exception("query_conversation_history failed")
            return ToolResult(success=False, error="Could not retrieve conversation history")


class SearchFAQTool(BaseTool):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @property
    def name(self) -> str:
        return "search_faq"
    
    @property
    def description(self) -> str:
        return "Searches FAQ database"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str) -> ToolResult:
        return ToolResult(success=True, data={"results": []})