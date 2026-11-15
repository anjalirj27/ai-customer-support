from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageCreate(BaseModel):
    """Request schema for creating a new message"""
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=5000)
    user_id: Optional[UUID] = None  # For future authentication

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value


class MessageResponse(BaseModel):
    """Response schema for a single message"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    agent_type: Optional[str] = None
    created_at: datetime


class ChatResponse(BaseModel):
    """Response schema for chat completion"""
    message_id: str
    conversation_id: str
    content: str
    agent: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    routing: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response schema for conversation"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0


class ConversationDetailResponse(BaseModel):
    """Response schema for conversation with messages"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
    messages: List[MessageResponse]
