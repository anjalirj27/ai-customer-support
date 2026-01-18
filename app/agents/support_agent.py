from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.tools.base_tool import BaseTool
from app.tools import support_tools

class SupportAgent(BaseAgent):
    """
    Support Agent - Handles general inquiries, FAQs, and how-to questions.
    Has access to conversation history and FAQ database.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self._tools = None
    
    @property
    def name(self) -> str:
        return "support"
    
    @property
    def description(self) -> str:
        return "Handles general support inquiries, FAQs, and account questions"
    
    @property
    def system_prompt(self) -> str:
        return """You are a helpful customer support agent.

Your role is to:
- Answer general questions about policies and procedures
- Help with account-related issues
- Provide information from the FAQ database
- Assist with how-to questions
- Be friendly, professional, and concise

Available tools:
1. **search_faq** - Search FAQ database for answers to common questions
2. **query_conversation_history** - Look up previous messages in this conversation

Guidelines:
- Use search_faq when customer asks general questions
- Use conversation history to maintain context
- Be concise but friendly
- If the question is about orders or billing, politely tell them you'll transfer to a specialist
- Always aim to resolve the issue in your first response"""
    
    def get_tools(self) -> List[BaseTool]:
        """Initialize and return support tools"""
        if self._tools is None:
            self._tools = [
    support_tools.SearchFAQTool(self.db),
    support_tools.QueryConversationHistoryTool(self.db)
]
        return self._tools