from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel
from typing import Optional, Dict

class BotCreate(SQLModel):
    name: str
    model: str = "gemini-2.5-flash"   # ✅ DEFAULT MODEL
    description: Optional[str] = None
    config: Dict = {}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class BotCreate(BaseModel):
    name: str
    model: str               # ✅ REQUIRED
    description: Optional[str] = None
    config: Dict = {}

class MessageIn(BaseModel):
    message: str

class ConversationOut(BaseModel):
    id: int
    session_id: str
    started_at: str
