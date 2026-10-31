from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token
from app.models.user import User
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    role = data.role if data.role in ("student", "recruiter", "admin") else "student"
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.flush()

    if role == "student":
        profile = Student(
            user_id=user.id,
            department=data.department,
            cgpa=data.cgpa,
        )
        db.add(profile)
    elif role == "recruiter":
        profile = Recruiter(
            user_id=user.id,
            company_name=data.company_name,
        )
        db.add(profile)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, role=user.role, user_id=user.id, name=user.name)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, role=user.role, user_id=user.id, name=user.name)
