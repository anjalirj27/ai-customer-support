from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Request schema for creating a new message"""
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=5000)
    user_id: Optional[str] = None  # For future authentication


class MessageResponse(BaseModel):
    """Response schema for a single message"""
    id: str
    conversation_id: str
    role: str
    content: str
    agent_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


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
    id: str
    user_id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Response schema for conversation with messages"""
    id: str
    user_id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True