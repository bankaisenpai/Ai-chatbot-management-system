from datetime import datetime
from typing import Optional, Dict

from sqlmodel import Session, select

from .models import User, Bot, UserMemory


# ─────────────────────────────────────────────
# USER CRUD
# ─────────────────────────────────────────────

def create_user(session: Session, email: str, password_hash: str) -> User:
    """Create a new user with hashed password"""
    user = User(
        email=email,
        password_hash=password_hash,
        created_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return session.exec(
        select(User).where(User.email == email)
    ).first()


# ─────────────────────────────────────────────
# BOT CRUD
# ─────────────────────────────────────────────

def create_bot(
    session: Session,
    owner_id: int,
    name: str,
    model: str,
    description: Optional[str],
    system_prompt: str,
    temperature: float,
    config: Optional[dict] = None,
) -> Bot:
    """Create a new bot"""
    bot = Bot(
        owner_id=owner_id,
        name=name,
        model=model,
        description=description,
        system_prompt=system_prompt,
        temperature=temperature,
        settings=config or {},
        created_at=datetime.utcnow(),
    )
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot


# ─────────────────────────────────────────────
# USER MEMORY (PERSISTENT MEMORY)
# ─────────────────────────────────────────────

def save_user_memory(
    session: Session,
    user_id: int,
    bot_id: int,
    key: str,
    value: str,
) -> None:
    """
    Save or update a persistent memory for a user per bot.
    Example: key="name", value="rahul"
    """
    existing = session.exec(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.bot_id == bot_id,
            UserMemory.key == key,
        )
    ).first()

    if existing:
        existing.value = value
        existing.updated_at = datetime.utcnow()
    else:
        memory = UserMemory(
            user_id=user_id,
            bot_id=bot_id,
            key=key,
            value=value,
            created_at=datetime.utcnow(),
        )
        session.add(memory)

    session.commit()


def load_user_memory(
    session: Session,
    user_id: int,
    bot_id: int,
) -> Dict[str, str]:
    """
    Load all persistent memory for a user & bot.
    Returns: { "name": "rahul", "city": "chennai" }
    """
    memories = session.exec(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.bot_id == bot_id,
        )
    ).all()

    return {m.key: m.value for m in memories}


def delete_user_memory(
    session: Session,
    user_id: int,
    bot_id: int,
    key: str,
) -> bool:
    """
    Delete a specific memory key.
    Example: forget name
    """
    memory = session.exec(
        select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.bot_id == bot_id,
            UserMemory.key == key,
        )
    ).first()

    if not memory:
        return False

    session.delete(memory)
    session.commit()
    return True
