from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.models.student import Student
from app.models.job import Job
from app.models.match import MatchResult
from app.services.llm import generate_interview_questions

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/{student_id}/interview-questions")
def get_interview_questions(
    student_id: int,
    job_id: int,
    current_user: User = Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_info = student.parsed_json or {}
    questions = generate_interview_questions(resume_info, job.title)

    return {
        "student_name": student.user.name,
        "job_title": job.title,
        "questions": questions,
    }
