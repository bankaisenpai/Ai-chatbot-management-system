from datetime import datetime
from sqlmodel import select, Session

from .models import User, Bot


def create_user(session: Session, email: str, password_hash: str):
    """Create a new user with hashed password"""
    user = User(
        email=email,
        password_hash=password_hash,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str):
    """Get user by email"""
    return session.exec(
        select(User).where(User.email == email)
    ).first()


def create_bot(
    session: Session,
    owner_id: int,
    name: str,
    model: str,
    description: str | None,
    system_prompt: str,
    temperature: float,
    config: dict | None = None,
):
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
