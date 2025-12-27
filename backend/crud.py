from sqlmodel import select
from .models import User, Bot, Conversation, Message, TrainingDataset
from .models import Bot

def create_user(session, email, password_hash):
    """Create a new user with hashed password"""
    user = User(
        email=email, 
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session, email):
    """Get user by email"""
    return session.exec(select(User).where(User.email == email)).first()

def create_bot(
    session,
    owner_id: int,
    name: str,
    model: str,
    description: str | None,
    config: dict,
):
    bot = Bot(
        owner_id=owner_id,
        name=name,
        model=model,          # ✅ FIX
        description=description,
        settings=config,      # ✅ FIX (settings, not config)
    )
    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot