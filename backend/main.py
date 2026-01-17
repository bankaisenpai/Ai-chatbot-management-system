from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(title="AI Chatbot Management System")

# -------------------------------------------------
# Middleware
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DB & Seed (IMPORT ONLY — DO NOT EXECUTE HERE)
# -------------------------------------------------
from .db import init_db


# -------------------------------------------------
# Routers
# -------------------------------------------------
from .routes import auth, bots, messages

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(messages.router, tags=["Messages"])

# -------------------------------------------------
# Startup (RUN ONCE PER WORKER)
# -------------------------------------------------
# -------------------------------------------------
# Preflight (CORS)
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
    print("[ERROR]", exc)
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# -------------------------------------------------
# Health checks
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "AI Chatbot API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
