from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from uuid import uuid4
import time
from fastapi.security import OAuth2PasswordBearer

from ..db import engine
from ..models import User, Bot, Conversation, Message
from ..crud import create_bot
from ..schemas import BotCreate
from ..auth import decode_token  # ✅ Fixed import

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/")
def create_bot_api(
    payload: BotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_bot(
        db,
        owner_id=user.id,
        name=payload.name,
        model=payload.model,
        description=payload.description,
        config=payload.config,
        system_prompt=payload.system_prompt,
        temperature=payload.temperature,
    )


@router.get("/")
def list_bots(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.exec(select(Bot).where(Bot.owner_id == user.id)).all()


@router.post("/{bot_id}/sessions")
def create_session(
    bot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(f"[DEBUG] create_session called with bot_id={bot_id}")  # ✅ Added debug log
    """Create a new chat session for a bot"""
    # Validate bot exists (owner_id can be None for public bots, or match user for private bots)
    bot = db.exec(
    select(Bot).where(Bot.id == bot_id)
).first()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Allow access if: bot is public (owner_id = None) OR user is the owner
    if bot.owner_id is not None and bot.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    session_uuid = str(uuid4())

    conv = Conversation(
        bot_id=bot_id,
        session_id=session_uuid,
    )

    db.add(conv)
    db.commit()
    db.refresh(conv)  # Refresh to get the generated ID

    # Extract data before session closes
    conversation_id = conv.id
    session_id = conv.session_id

    return {
        "conversation_id": conversation_id,
        "session_id": session_id,
    }


@router.post("/{bot_id}/sessions/{session_id}/message")
def send_message(
    bot_id: int,
    session_id: str,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(f"[DEBUG] send_message called with bot_id={bot_id}, session_id={session_id}, message={message}")  # ✅ Added debug log
    """Send a message and get bot response"""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server")

    start_time = time.time()

    # Load bot with personality
    bot = db.exec(
    select(Bot).where(Bot.id == bot_id)
).first()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Validate bot access (owner_id can be None for public bots, or match user for private bots)
    if bot.owner_id is not None and bot.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Load conversation
    conv = db.exec(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.bot_id == bot_id,
        )
    ).first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    db.add(
        Message(
            conversation_id=conv.id,
            role="user",
            text=message,
        )
    )
    db.commit()

    # Load last 10 messages for memory (current conversation only)
    history = db.exec(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .limit(10)
    ).all()

    # Build messages: system prompt first, then history, then current message
    chat_messages = [
        {
            "role": "system",
            "content": bot.system_prompt,
        }
    ]

    for m in history:
        chat_messages.append({
            "role": "assistant" if m.role == "bot" else "user",
            "content": m.text,
        })

    print(f"[Bot {bot_id}] System Prompt: {bot.system_prompt}")
    print(f"[Bot {bot_id}] Conversation ID: {conv.id} | Session ID: {session_id}")
    print(f"[Bot {bot_id}] Memory: {len(history)} messages")

    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=chat_messages,
            temperature=bot.temperature,
            max_tokens=512,
        )
        reply_text = response.choices[0].message.content
        print(f"[Bot {bot_id}] Groq response received: {len(reply_text)} chars")
    except ImportError as e:
        print(f"[Bot {bot_id}] Groq module import error: {e}")
        reply_text = "⚠️ AI module not available. Please check server configuration."
    except Exception as e:
        print(f"[Bot {bot_id}] Groq API Error: {type(e).__name__}: {e}")
        reply_text = "⚠️ AI is temporarily unavailable. Please try again."

    latency_ms = int((time.time() - start_time) * 1000)

    # Save bot reply
    db.add(
        Message(
            conversation_id=conv.id,
            role="bot",
            text=reply_text,
            latency_ms=latency_ms,
        )
    )
    db.commit()

    return {
        "reply": reply_text,
        "latency_ms": latency_ms,
    }