from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Standardized result from tool execution"""
    success: bool
    data: Any = None
    error: str = None


class BaseTool(ABC):
    """Abstract base class for all agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """What the tool does"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute tool functionality"""
        pass
    
    def to_openai_tool(self) -> Dict[str, Any]:
        """Convert to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema()
            }
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema for parameters"""
        pass