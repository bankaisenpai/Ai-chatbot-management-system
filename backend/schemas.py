from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

# -------------------------------------------------
# User Schemas
# -------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------------------------------------------------
# Bot Schemas
# -------------------------------------------------
class BotCreate(BaseModel):
    name: str
    model: str
    description: Optional[str] = None
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7
    config: Dict = {}

# -------------------------------------------------
# Message Schemas
# -------------------------------------------------
class MessageIn(BaseModel):
    message: str

class ConversationOut(BaseModel):
    id: int
    session_id: str
    started_at: str