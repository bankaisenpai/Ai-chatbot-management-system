from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from ..db import engine
from ..models import User
from ..crud import create_user, get_user_by_email
from ..auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)
from ..schemas import UserCreate, Token

router = APIRouter()


def get_db():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, payload.email, get_password_hash(payload.password))
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
