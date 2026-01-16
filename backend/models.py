from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.types import JSON
from typing import Optional, List, Dict
from datetime import datetime, timezone


def get_utcnow():
    return datetime.now(timezone.utc)


# -------------------------
# USER
# -------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    bots: List["Bot"] = Relationship(back_populates="owner")



# -------------------------
# BOT
# -------------------------
class Bot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")

    name: str
    model: str = Field(nullable=False)
    description: Optional[str] = None
    system_prompt: str = Field(default="You are a helpful assistant.")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    settings: Dict = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="bots")
    conversations: List["Conversation"] = Relationship(back_populates="bot")


# -------------------------
# CONVERSATION
# -------------------------
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id")
    session_id: str = Field(index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    meta_data: Dict = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )

    bot: Optional[Bot] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


# -------------------------
# MESSAGE
# -------------------------
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")

    role: str  # "user" or "bot"
    text: str
    latency_ms: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# -------------------------
# TRAINING DATASET
# -------------------------
class TrainingDataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    data: Dict = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
