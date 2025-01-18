from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base_tool import BaseTool
from app.core.ai_client import ai_client
from app.core.config import settings


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Every agent must implement:
    - name: Agent identifier
    - description: What this agent handles
    - system_prompt: Instructions for the AI
    - tools: List of tools this agent can use
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_client = ai_client
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """What this agent handles"""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System instructions for the AI"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """List of tools available to this agent"""
        pass
    
    async def process(
        self, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.
        
        Args:
            message: User's message
            conversation_history: Previous messages for context
            
        Returns:
            Dict with response and metadata
        """
        if conversation_history is None:
            conversation_history = []
        
        # Build messages for AI
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last 10 messages)
        messages.extend(conversation_history[-10:])
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        try:
            # Get tools for this agent
            tools = self.get_tools()
            tool_schemas = [tool.to_openai_tool() for tool in tools]
            
            # Call AI with tool support
            response = await self.ai_client.chat.completions.create(
                model=settings.ai_model,
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            assistant_message = response.choices[0].message
            
            # Check if AI wants to use tools
            if assistant_message.tool_calls:
                return await self._handle_tool_calls(
                    assistant_message,
                    messages,
                    tools
                )
            
            # No tool calls, return response directly
            return {
                "content": assistant_message.content,
                "agent": self.name,
                "tool_calls": None
            }
            
        except Exception as e:
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "agent": self.name,
                "error": str(e)
            }
    
    async def _handle_tool_calls(
        self,
        assistant_message: Any,
        messages: List[Dict[str, str]],
        tools: List[BaseTool]
    ) -> Dict[str, Any]:
        """
        Handle tool calls from AI.
        
        Args:
            assistant_message: Message with tool calls
            messages: Conversation history
            tools: Available tools
            
        Returns:
            Final response after tool execution
        """
        # Add assistant's tool call to messages
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })
        
        # Execute each tool call
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            
            # Find the tool
            tool = next((t for t in tools if t.name == function_name), None)
            
            if not tool:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": f"Error: Tool {function_name} not found"
                })
                continue
            
            # Parse arguments
            import json
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": "Error: Invalid tool arguments"
                })
                continue
            
            # Execute tool
            result = await tool.execute(**arguments)
            
            # Add result to messages
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result.dict())
            })
        
        # Add tool results to messages
        messages.extend(tool_results)
        
        # Get final response from AI with tool results
        final_response = await self.ai_client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        return {
            "content": final_response.choices[0].message.content,
            "agent": self.name,
            "tool_calls": [
                {
                    "tool": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                }
                for tc in assistant_message.tool_calls
            ]
        }