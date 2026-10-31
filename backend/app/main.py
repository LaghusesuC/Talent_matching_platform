import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base, SessionLocal
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


@app.on_event("startup")
def init_default_data():
    """Ensure demo accounts and baseline placement data exist on startup."""
    from app.models.user import User
    from app.models.student import Student
    from app.models.recruiter import Recruiter
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@test.com").first():
            # 1. Admin account
            admin_user = User(
                name="Placement Admin",
                email="admin@test.com",
                password_hash=hash_password("password123"),
                role="admin",
            )
            db.add(admin_user)

            # 2. Recruiter account
            rec_user = User(
                name="Aarthi Recruiter",
                email="recruiter@test.com",
                password_hash=hash_password("password123"),
                role="recruiter",
            )
            db.add(rec_user)
            db.flush()
            rec = Recruiter(user_id=rec_user.id, company_name="Zoho")
            db.add(rec)

            # 3. Student account
            stu_user = User(
                name="Demo Candidate",
                email="student@test.com",
                password_hash=hash_password("password123"),
                role="student",
            )
            db.add(stu_user)
            db.flush()
            stu = Student(user_id=stu_user.id, department="Computer Science", cgpa=8.8)
            db.add(stu)

            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Resume Screening API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
