from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from uuid import uuid4
import time
import os

from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from ..db import engine
from ..models import User, Bot, Conversation, Message
from ..schemas import BotCreate
from ..crud import (
    create_bot,
    save_user_memory,
    load_user_memory,
    delete_user_memory,
)
from ..auth import decode_token
from ..utils.memory import extract_user_memory

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ─────────────────────────────────────────────
# DB + AUTH HELPERS
# ─────────────────────────────────────────────

def get_db():
    with Session(engine) as session:
        yield session


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ─────────────────────────────────────────────
# BOTS
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# SESSIONS
# ─────────────────────────────────────────────

@router.post("/{bot_id}/sessions")
def create_session(
    bot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(f"[DEBUG] create_session called with bot_id={bot_id}")

    bot = db.exec(select(Bot).where(Bot.id == bot_id)).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    if bot.owner_id is not None and bot.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    session_uuid = str(uuid4())

    conv = Conversation(
        bot_id=bot_id,
        session_id=session_uuid,
    )

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return {
        "conversation_id": conv.id,
        "session_id": conv.session_id,
    }


# ─────────────────────────────────────────────
# SEND MESSAGE (WITH 🧠 PERSISTENT MEMORY)
# ─────────────────────────────────────────────

@router.post("/{bot_id}/sessions/{session_id}/message")
def send_message(
    bot_id: int,
    session_id: str,
    message: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(f"[DEBUG] send_message: bot={bot_id}, session={session_id}, msg={message}")

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    start_time = time.time()

    # Load bot
    bot = db.exec(select(Bot).where(Bot.id == bot_id)).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

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

    # ─────────────────────────────────────────────
    # Save USER message
    # ─────────────────────────────────────────────
    db.add(
        Message(
            conversation_id=conv.id,
            role="user",
            text=message,
        )
    )
    db.commit()

    # ─────────────────────────────────────────────
    # 🧠 Extract memory (OVERWRITE MODE)
    # ─────────────────────────────────────────────
    memory_to_save, memory_to_delete = extract_user_memory(message)

    # 🗑️ Delete memory
    for key in memory_to_delete:
        delete_user_memory(
            db,
            user_id=user.id,
            bot_id=bot_id,
            key=key,
        )

    # 💾 Save / overwrite memory
    for key, value in memory_to_save.items():
        save_user_memory(
            db,
            user_id=user.id,
            bot_id=bot_id,
            key=key,
            value=value,
        )

    # ─────────────────────────────────────────────
    # 🧠 Load persistent memory
    # ─────────────────────────────────────────────
    user_memory = load_user_memory(
        db,
        user_id=user.id,
        bot_id=bot_id,
    )

    memory_prompt = ""
    if user_memory:
        memory_prompt = "User memory:\n"
        for k, v in user_memory.items():
            memory_prompt += f"- {k}: {v}\n"

    system_prompt = f"""
{bot.system_prompt}

{memory_prompt}
"""

    print("🧠 MEMORY INJECTED:")
    print(memory_prompt)

    # ─────────────────────────────────────────────
    # Conversation history (last 10)
    # ─────────────────────────────────────────────
    history = db.exec(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
        .limit(10)
    ).all()

    chat_messages = [
        {"role": "system", "content": system_prompt}
    ]

    for m in history:
        chat_messages.append({
            "role": "assistant" if m.role == "bot" else "user",
            "content": m.text,
        })

    # ─────────────────────────────────────────────
    # GROQ CALL
    # ─────────────────────────────────────────────
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=chat_messages,
            temperature=bot.temperature,
            max_tokens=512,
        )

        reply_text = response.choices[0].message.content

    except Exception as e:
        print("❌ Groq error:", e)
        reply_text = "⚠️ AI is temporarily unavailable."

    latency_ms = int((time.time() - start_time) * 1000)

    # ─────────────────────────────────────────────
    # Save BOT reply
    # ─────────────────────────────────────────────
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
