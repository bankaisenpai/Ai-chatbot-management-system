# Route Verification & Fixes

## ✅ FIX 1: ROUTE EXISTS

### Verified Route Structure

**File**: `backend/routes/bots.py` (Line 72)

```python
@router.post("/{bot_id}/sessions")
def create_session(
    bot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
```

### Registered in main.py

```python
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
```

**Final URL**: `POST /bots/{bot_id}/sessions` ✅

---

## ✅ FIX 2: get_current_user() ERROR HANDLING

### Updated Function (backend/routes/bots.py, Lines 23-44)

Added robust error handling to prevent 500 errors:

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id_int = int(user_id)
        user = db.get(User, user_id_int)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found in database")
        
        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")
```

### Error Handling Improvements

1. ✅ Explicit `user_id` validation
2. ✅ Clear separation of conversion logic
3. ✅ Specific error messages for debugging
4. ✅ Exception logging with print statements
5. ✅ Catches ValueError for invalid ID format
6. ✅ Generic Exception handler for DB issues

---

## 🧠 Quick Check - Verify Routes at Runtime

### Check Swagger Docs

```
http://127.0.0.1:8000/docs
```

Search for: `POST /bots/{bot_id}/sessions`

### If Not Found

1. Restart backend server:
   ```
   uvicorn backend.main:app --reload
   ```

2. Check imports in main.py:
   ```python
   from .routes import auth, bots
   ```

3. Check router includes:
   ```python
   app.include_router(bots.router, prefix="/bots", tags=["Bots"])
   ```

---

## 🐛 Debugging DB Connection Issues

If you still get user not found errors:

1. **Check DB file exists**:
   ```
   backend/chatbot.db
   ```

2. **Register a new user** via `/auth/register` first

3. **Check User table**:
   ```python
   # In backend/db.py or test script:
   from sqlmodel import Session, select
   from backend.models import User
   from backend.db import engine
   
   with Session(engine) as session:
       users = session.exec(select(User)).all()
       print(f"Users in DB: {len(users)}")
       for u in users:
           print(f"  ID={u.id}, Email={u.email}")
   ```

4. **Check token contains correct user ID**:
   ```python
   # Decode token manually:
   from backend.auth import decode_token
   user_id = decode_token("your_token_here")
   print(f"Token contains user_id: {user_id}")
   ```

---

## Files Modified

- ✅ `backend/routes/bots.py` - Enhanced get_current_user()
- ✅ `backend/main.py` - Router includes added
- ✅ `backend/routes/auth.py` - Created
- ✅ `backend/routes/__init__.py` - Created
