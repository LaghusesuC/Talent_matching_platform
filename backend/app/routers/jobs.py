from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.models.job import Job
from app.models.match import MatchResult, Shortlist
from app.schemas.platform import JobCreate, JobOut, CandidateOut, ShortlistCreate, ShortlistOut
from app.services.llm import extract_jd_info, generate_interview_questions
from app.services.parser import extract_text
from app.services.matcher import compute_match

router = APIRouter(prefix="/jobs", tags=["Jobs & Recruiter"])


def _get_recruiter(current_user: User, db: Session) -> Recruiter:
    rec = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")
    return rec


@router.post("", response_model=JobOut, status_code=201)
def create_job(
    data: JobCreate,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    rec = _get_recruiter(current_user, db)
    jd_info = extract_jd_info(data.description)
    skills = data.skills_required or jd_info.get("required_skills", [])

    job = Job(
        recruiter_id=rec.id,
        title=data.title,
        company_name=data.company_name or rec.company_name,
        description=data.description,
        skills_required=skills,
        parsed_json=jd_info,
    )
    db.add(job)
    db.flush()

    # Compute matches against all existing students
    students = db.query(Student).filter(Student.resume_text != None).all()
    for student in students:
        resume_info = student.parsed_json or {}
        scores = compute_match(student.resume_text or "", data.description, resume_info, jd_info, run_llm=False)

        mr = MatchResult(
            student_id=student.id,
            job_id=job.id,
            **{k: scores[k] for k in ["rule_score", "semantic_score", "llm_score", "final_score",
                                       "matched_skills", "missing_skills", "explanation",
                                       "ats_score", "improvement_suggestions"]},
        )
        db.add(mr)

    db.commit()
    db.refresh(job)
    return job


@router.post("/upload", response_model=JobOut, status_code=201)
async def create_job_from_file(
    title: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    rec = _get_recruiter(current_user, db)
    contents = await file.read()
    jd_text = extract_text(contents, file.filename)
    jd_info = extract_jd_info(jd_text)
    skills = jd_info.get("required_skills", [])

    job = Job(
        recruiter_id=rec.id,
        title=title,
        description=jd_text,
        skills_required=skills,
        parsed_json=jd_info,
    )
    db.add(job)
    db.flush()

    students = db.query(Student).filter(Student.resume_text != None).all()
    for student in students:
        resume_info = student.parsed_json or {}
        scores = compute_match(student.resume_text or "", jd_text, resume_info, jd_info)
        mr = MatchResult(student_id=student.id, job_id=job.id,
                         **{k: scores[k] for k in ["rule_score", "semantic_score", "llm_score",
                                                    "final_score", "matched_skills", "missing_skills",
                                                    "explanation", "ats_score", "improvement_suggestions"]})
        db.add(mr)

    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/candidates", response_model=List[CandidateOut])
def ranked_candidates(
    job_id: int,
    current_user: User = Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    results = (
        db.query(MatchResult)
        .filter(MatchResult.job_id == job_id)
        .order_by(MatchResult.final_score.desc())
        .all()
    )

    candidates = []
    for rank, mr in enumerate(results, start=1):
        mr.rank = rank
        student = mr.student
        user = student.user
        candidates.append(CandidateOut(
            student_id=student.id,
            name=user.name,
            email=user.email,
            department=student.department,
            cgpa=student.cgpa,
            final_score=mr.final_score,
            rule_score=mr.rule_score,
            semantic_score=mr.semantic_score,
            llm_score=mr.llm_score,
            rank=rank,
            matched_skills=mr.matched_skills or [],
            missing_skills=mr.missing_skills or [],
            explanation=mr.explanation or "",
            ats_score=mr.ats_score,
            match_id=mr.id,
        ))
    db.commit()
    return candidates


@router.post("/{job_id}/shortlist", response_model=ShortlistOut, status_code=201)
def shortlist_candidate(
    job_id: int,
    data: ShortlistCreate,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    existing = db.query(Shortlist).filter(
        Shortlist.job_id == job_id,
        Shortlist.student_id == data.student_id,
    ).first()
    if existing:
        existing.status = data.status
        db.commit()
        db.refresh(existing)
        return existing

    sl = Shortlist(job_id=job_id, student_id=data.student_id, status=data.status)
    db.add(sl)
    db.commit()
    db.refresh(sl)
    return sl


@router.get("/{job_id}/shortlists", response_model=List[ShortlistOut])
def get_shortlists(
    job_id: int,
    current_user: User = Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    return db.query(Shortlist).filter(Shortlist.job_id == job_id).all()
