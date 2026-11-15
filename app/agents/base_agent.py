import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_client import ai_client
from app.core.config import settings
from app.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

FALLBACK_ERROR_MESSAGE = (
    "I'm sorry, I ran into a problem while processing your request. "
    "Please try again in a moment."
)
EMPTY_RESPONSE_MESSAGE = "I'm sorry, I couldn't generate a response. Could you rephrase your question?"


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

    @property
    @abstractmethod
    def description(self) -> str:
        """What this agent handles"""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System instructions for the AI"""

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """List of tools available to this agent"""

    async def process(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.

        Args:
            message: User's message
            conversation_history: Previous messages for context

        Returns:
            Dict with response and metadata
        """
        conversation_history = conversation_history or []

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(conversation_history[-settings.MAX_CONTEXT_MESSAGES:])
        messages.append({"role": "user", "content": message})

        try:
            tools = self.get_tools()
            tool_schemas = [tool.to_openai_tool() for tool in tools]

            response = await self.ai_client.chat.completions.create(
                model=settings.ai_model,
                messages=messages,
                tools=tool_schemas or None,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )

            assistant_message = response.choices[0].message

            if assistant_message.tool_calls:
                return await self._handle_tool_calls(assistant_message, messages, tools)

            return {
                "content": assistant_message.content or EMPTY_RESPONSE_MESSAGE,
                "agent": self.name,
                "tool_calls": None
            }

        except Exception as e:
            logger.exception("Agent '%s' failed to process message", self.name)
            return {
                "content": FALLBACK_ERROR_MESSAGE,
                "agent": self.name,
                "error": str(e)
            }

    async def _execute_tool_call(self, tool_call: Any, tools: List[BaseTool]) -> Dict[str, Any]:
        """
        Execute a single tool call requested by the model.

        Returns the `tool` role message to feed back to the model, plus the
        parsed arguments (empty when they could not be parsed).
        Never raises: failures are reported back to the model as tool errors.
        """
        function_name = tool_call.function.name

        def tool_message(payload: Any) -> Dict[str, Any]:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": payload if isinstance(payload, str) else json.dumps(payload, default=str)
            }

        tool = next((t for t in tools if t.name == function_name), None)
        if not tool:
            return {
                "message": tool_message(f"Error: Tool {function_name} not found"),
                "arguments": {}
            }

        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
            if not isinstance(arguments, dict):
                raise ValueError("arguments must be a JSON object")
        except (json.JSONDecodeError, ValueError):
            return {
                "message": tool_message("Error: Invalid tool arguments"),
                "arguments": {}
            }

        try:
            result: ToolResult = await tool.execute(**arguments)
        except TypeError:
            logger.warning("Tool '%s' called with unexpected arguments: %s", function_name, arguments)
            return {
                "message": tool_message("Error: Invalid tool arguments"),
                "arguments": arguments
            }
        except Exception:
            logger.exception("Tool '%s' failed", function_name)
            return {
                "message": tool_message("Error: Tool execution failed"),
                "arguments": arguments
            }

        return {"message": tool_message(result.model_dump()), "arguments": arguments}

    async def _handle_tool_calls(
        self,
        assistant_message: Any,
        messages: List[Dict[str, Any]],
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

        executed_calls = []
        for tool_call in assistant_message.tool_calls:
            outcome = await self._execute_tool_call(tool_call, tools)
            messages.append(outcome["message"])
            executed_calls.append({
                "tool": tool_call.function.name,
                "arguments": outcome["arguments"]
            })

        # Get final response from AI with tool results
        final_response = await self.ai_client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )

        return {
            "content": final_response.choices[0].message.content or EMPTY_RESPONSE_MESSAGE,
            "agent": self.name,
            "tool_calls": executed_calls
        }
