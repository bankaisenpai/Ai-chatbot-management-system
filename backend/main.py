from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from dotenv import load_dotenv
from uuid import uuid4
import os
import time
import json
import csv
import io

# -------------------------------------------------
# Load ENV
# -------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

# -------------------------------------------------
# OAuth2 (THIS ENABLES 🔒 IN SWAGGER)
# -------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -------------------------------------------------
# Gemini (NEW SDK)
# -------------------------------------------------
from google import genai

genai_client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------------------------
# Local imports
# -------------------------------------------------
from .db import init_db, engine
from .models import User, Bot, Conversation, Message, TrainingDataset
from .crud import create_user, get_user_by_email, create_bot
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)
from .schemas import UserCreate, Token, BotCreate

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(title="AI Chatbot Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DB init
# -------------------------------------------------
init_db()

def get_db():
    with Session(engine) as session:
        yield session

# -------------------------------------------------
# AUTH
# -------------------------------------------------
@app.post("/auth/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(payload.password)
    user = create_user(db, payload.email, hashed)
    token = create_access_token(subject=str(user.id))

    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


# -------------------------------------------------
# CURRENT USER (CORRECT WAY)
# -------------------------------------------------
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

# -------------------------------------------------
# BOTS
# -------------------------------------------------
@app.post("/bots")
def create_bot_api(
    payload: BotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_bot(
        db,
        owner_id=user.id,
        name=payload.name,
        model=payload.model,          # ✅ PASS MODEL
        description=payload.description,
        config=payload.config,
    )



@app.get("/bots")
def list_bots(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.exec(select(Bot).where(Bot.owner_id == user.id)).all()

# -------------------------------------------------
# CHAT
# -------------------------------------------------

@app.post("/bots/{bot_id}/sessions")
def create_session(
    bot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = Conversation(
        bot_id=bot_id,
        session_id=str(uuid4())
    )

    db.add(conv)
    db.commit()
    # ❌ DO NOT call db.refresh(conv) with SQLite

    return {
        "conversation_id": conv.id,
        "session_id": conv.session_id,
    }



@app.post("/bots/{bot_id}/sessions/{session_id}/message")
def send_message(
    bot_id: int,
    session_id: str,
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    conv = db.exec(
        select(Conversation).where(Conversation.session_id == session_id)
    ).first()

    if not conv:
        conv = Conversation(bot_id=bot_id, session_id=session_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    db.add(
        Message(
            conversation_id=conv.id,
            role="user",
            text=message,
        )
    )
    db.commit()

    # ✅ ADDED ERROR HANDLING HERE
    t0 = time.time()
    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
        )
        reply_text = response.text
        latency_ms = int((time.time() - t0) * 1000)
    except Exception as e:
        # Log the error for debugging
        print(f"Gemini API Error: {e}")
        
        # Fallback response when API fails
        reply_text = "Sorry, the AI service is temporarily unavailable. Please try again in a moment. 🤖"
        latency_ms = int((time.time() - t0) * 1000)

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

# -------------------------------------------------
# CONVERSATION EXPORT
# -------------------------------------------------
@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).all()

    return [
        {
            "role": m.role,
            "text": m.text,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]

# -------------------------------------------------
# TRAINING DATA
# -------------------------------------------------
@app.post("/bots/{bot_id}/upload-training")
async def upload_training(
    bot_id: int,
    file: bytes = Form(...),
    db: Session = Depends(get_db),
):
    text = file.decode("utf-8")

    if text.strip().startswith("{") or text.strip().startswith("["):
        data = json.loads(text)
    else:
        data = list(csv.DictReader(io.StringIO(text)))

    ds = TrainingDataset(
        bot_id=bot_id,
        name=f"upload_{bot_id}",
        data={"raw": data},
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)

    return {"status": "uploaded", "dataset_id": ds.id}

# -------------------------------------------------
# ANALYTICS
# -------------------------------------------------
@app.get("/analytics/{bot_id}")
def analytics(
    bot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv_ids = [
        c[0]
        for c in db.exec(
            select(Conversation.id).where(Conversation.bot_id == bot_id)
        ).all()
    ]

    msgs = (
        db.exec(select(Message).where(Message.conversation_id.in_(conv_ids))).all()
        if conv_ids
        else []
    )

    bot_latencies = [m.latency_ms for m in msgs if m.role == "bot" and m.latency_ms]

    return {
        "messages": len(msgs),
        "conversations": len(conv_ids),
        "avg_latency_ms": (
            sum(bot_latencies) / len(bot_latencies) if bot_latencies else None
        ),
    }

# -------------------------------------------------
# HEALTH
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}