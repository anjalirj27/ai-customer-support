from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.schemas.chat import (
    MessageCreate,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/messages", response_model=ChatResponse)
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and get AI response.
    
    This endpoint:
    1. Creates or uses existing conversation
    2. Saves user message
    3. Routes to appropriate agent
    4. Returns AI response
    """
    try:
        chat_service = ChatService(db)
        
        response = await chat_service.send_message(
            message=message_data.message,
            conversation_id=message_data.conversation_id,
            user_id=message_data.user_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation details with all messages.
    """
    try:
        conv_service = ConversationService(db)
        
        # Get conversation
        conversation = await conv_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages = await conv_service.get_conversation_messages(conversation_id)
        
        return {
            "id": str(conversation.id),
            "user_id": str(conversation.user_id),
            "title": conversation.title,
            "status": conversation.status.value,
            "created_at": conversation.created_at,
            "messages": [
                {
                    "id": str(msg.id),
                    "conversation_id": str(msg.conversation_id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "agent_type": msg.agent_type.value if msg.agent_type else None,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all conversations for current user.
    """
    try:
        conv_service = ConversationService(db)
        
        # Get default user (in production, get from auth)
        user = await conv_service.get_or_create_default_user()
        
        # Get conversations
        conversations = await conv_service.get_user_conversations(
            user_id=str(user.id),
            limit=limit,
            offset=offset
        )
        
        return [
            {
                "id": str(conv.id),
                "user_id": str(conv.user_id),
                "title": conv.title,
                "status": conv.status.value,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": 0  # Can add count query if needed
            }
            for conv in conversations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    """
    try:
        conv_service = ConversationService(db)
        
        success = await conv_service.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )