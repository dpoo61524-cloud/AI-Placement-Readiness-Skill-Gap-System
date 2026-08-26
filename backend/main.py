import os
import sys
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add workspace root to python path dynamically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database components
from backend.db.session import engine, Base
from backend.db.models import SubmissionCache

# Router import
from backend.routers import analysis

# Recommendation preload logic
from src.recommendation import initialize_rag_index

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy Tables
Base.metadata.create_all(bind=engine)

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from backend.limiter import limiter
from fastapi import Request, Response

app = FastAPI(
    title="AI Placement Readiness & Skill Gap System API",
    description="Backend API services supporting student resume evaluations, eligibility predictions, explainability, and learning recommendations.",
    version="1.0.0"
)

# Slowapi configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom middleware to add security headers and sanitize production errors
@app.middleware("http")
async def add_security_headers_and_harden_errors(request: Request, call_next):
    response = await call_next(request)
    # Add Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# CORS Setup
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://localhost:3000"]')
try:
    origins = json.loads(cors_origins_str)
except Exception:
    # Fallback to splitting by comma if it's a comma-separated list
    if cors_origins_str:
        origins = [origin.strip() for origin in cors_origins_str.split(",")]
    else:
        origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload RAG FAISS Vector Database on server startup asynchronously
import threading

@app.on_event("startup")
def startup_event():
    print("FastAPI Backend: Startup event triggered. Preloading ML and RAG models in background thread...", flush=True)
    def _preload():
        try:
            initialize_rag_index(resources_path="data/learning_resources.json")
            print("FastAPI Backend: ML and RAG models preloaded successfully.", flush=True)
        except Exception as e:
            print(f"Warning during server startup: Failed to initialize FAISS index: {str(e)}", flush=True)
            
    threading.Thread(target=_preload, daemon=True).start()

# Root endpoint
@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to the AI Placement Readiness & Skill Gap System API!",
        "docs_url": "http://localhost:8000/docs",
        "health_check": "http://localhost:8000/health",
        "frontend_url": "http://localhost:5173"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": str(engine.url)}

# Register routers directly at root
app.include_router(analysis.router, tags=["Analysis"])

if __name__ == "__main__":
    import uvicorn
    # If run directly as a script
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
