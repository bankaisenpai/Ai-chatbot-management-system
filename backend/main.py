from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# App (MUST COME BEFORE ROUTERS)
# -------------------------------------------------
app = FastAPI(title="AI Chatbot Management System")
@app.post("/api/test-chat")
def test_chat():
    return {
        "success": True,
        "chat_id": "manual-test-123",
        "message": "Backend is working"
    }
# -------------------------------------------------
# Middleware
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-chatbot-management-system.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DB
# -------------------------------------------------
from backend.db import init_db

# -------------------------------------------------
# Routers (IMPORT AFTER app IS DEFINED)
# -------------------------------------------------
from backend.routes import auth, bots, messages

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(messages.router, tags=["Messages"])

print("✅ Routers loaded")

# -------------------------------------------------
# Startup
# -------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("🔹 Initializing database...")
    init_db()
    print("✅ Database ready")

# -------------------------------------------------
# Health
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "AI Chatbot API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# Exception handlers
# -------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    import traceback
    print("[ERROR]", exc)
    print(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
