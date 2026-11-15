from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter, CHAT_RATE_LIMIT
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.schemas.chat import (
    MessageCreate,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Unexpected errors propagate to the global exception handler, which logs the
# traceback and returns a generic 500 (internal details are never exposed).


@router.post("/messages", response_model=ChatResponse)
@limiter.limit(CHAT_RATE_LIMIT)
async def send_message(
    request: Request,  # required by the rate limiter
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
    chat_service = ChatService(db)

    return await chat_service.send_message(
        message=message_data.message,
        conversation_id=str(message_data.conversation_id) if message_data.conversation_id else None,
        user_id=str(message_data.user_id) if message_data.user_id else None,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation details with all messages.
    """
    conv_service = ConversationService(db)

    conversation = await conv_service.get_conversation(str(conversation_id))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await conv_service.get_conversation_messages(str(conversation_id))

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


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List all conversations for current user.
    """
    conv_service = ConversationService(db)

    # Get default user (in production, get from auth)
    user = await conv_service.get_or_create_default_user()

    conversations = await conv_service.get_user_conversations(
        user_id=str(user.id),
        limit=limit,
        offset=offset
    )
    message_counts = await conv_service.get_message_counts(
        [conv.id for conv in conversations]
    )

    return [
        {
            "id": str(conv.id),
            "user_id": str(conv.user_id),
            "title": conv.title,
            "status": conv.status.value,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": message_counts.get(conv.id, 0)
        }
        for conv in conversations
    ]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    """
    conv_service = ConversationService(db)

    success = await conv_service.delete_conversation(str(conversation_id))
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}
