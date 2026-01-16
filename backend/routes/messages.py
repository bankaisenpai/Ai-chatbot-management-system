from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
import time

from ..db import engine
from ..models import User, Bot, Conversation, Message
from ..auth import decode_token
from ..schemas import MessageIn
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/sessions/{session_id}/messages")
def send_message(
    session_id: str,
    payload: MessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a conversation and get bot response"""
    # Get conversation
    conversation = db.exec(
        select(Conversation).where(Conversation.session_id == session_id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check authorization
    bot = db.get(Bot, conversation.bot_id)
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        text=payload.message
    )
    db.add(user_message)
    db.commit()
    
    # Generate bot response (placeholder for now)
    start_time = time.time()
    
    # TODO: Integrate with Groq API here
    bot_response_text = f"Echo: {payload.message}"
    
    latency = int((time.time() - start_time) * 1000)
    
    # Save bot message
    bot_message = Message(
        conversation_id=conversation.id,
        role="bot",
        text=bot_response_text,
        latency_ms=latency
    )
    db.add(bot_message)
    db.commit()
    db.refresh(bot_message)
    
    return {
        "id": bot_message.id,
        "role": bot_message.role,
        "text": bot_message.text,
        "created_at": bot_message.created_at.isoformat(),
        "latency_ms": bot_message.latency_ms
    }


@router.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a conversation"""
    conversation = db.exec(
        select(Conversation).where(Conversation.session_id == session_id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")
    
    bot = db.get(Bot, conversation.bot_id)
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "text": msg.text,
            "created_at": msg.created_at.isoformat(),
            "latency_ms": msg.latency_ms
        }
        for msg in messages
    ]