import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.core.config import get_settings
from app.routers import auth, students, jobs, candidates, admin
import app.models  # ensure all models are registered

settings = get_settings()

# Create all DB tables
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Resume Screening & Talent Matching Platform",
    description="LLM-powered campus placement screening system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Resume Screening API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
