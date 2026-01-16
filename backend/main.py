from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load env
load_dotenv()

# DB
from .db import init_db

# Routers
from .routes import auth, bots, messages

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
# Routers
# -------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(messages.router, tags=["Messages"])

# -------------------------------------------------
# Preflight
# -------------------------------------------------
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return {"message": "OK"}

# -------------------------------------------------
# Exception handlers
# -------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    import traceback
    print(f"[ERROR] {exc}")
    print(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# -------------------------------------------------
# DB init (ONCE)
# -------------------------------------------------
init_db()

# -------------------------------------------------
# Health
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "AI Chatbot API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
