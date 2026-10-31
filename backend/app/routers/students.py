import os
import time
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.student import Student
from app.models.job import Job
from app.models.match import MatchResult
from app.schemas.platform import StudentProfile, MatchOut
from app.services.parser import extract_text
from app.services.llm import extract_resume_info, generate_interview_questions
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me", response_model=StudentProfile)
def get_my_profile(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    profile = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    t_start = time.perf_counter()

    # Validate file type
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX and TXT files are supported")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"student_{current_user.id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Parse text (cached by content hash — instant on repeated uploads)
    t_parse = time.perf_counter()
    resume_text = extract_text(contents, file.filename)
    parse_ms = round((time.perf_counter() - t_parse) * 1000, 1)

    # Extract structured info with LLM (cached — skips LLM on same resume)
    t_llm = time.perf_counter()
    parsed = extract_resume_info(resume_text)
    llm_ms = round((time.perf_counter() - t_llm) * 1000, 1)

    # Update student profile
    profile = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not profile:
        profile = Student(user_id=current_user.id)
        db.add(profile)

    profile.resume_path = file_path
    profile.resume_text = resume_text
    profile.parsed_json = parsed

    # Re-run match computations for this student (fast path: no LLM)
    from app.services.matcher import compute_match
    from app.models.match import MatchResult

    t_match = time.perf_counter()
    jobs = db.query(Job).all()
    for job in jobs:
        jd_info = job.parsed_json or {"required_skills": job.skills_required or []}
        scores = compute_match(resume_text, job.description, parsed, jd_info, run_llm=False)

        mr = db.query(MatchResult).filter(
            MatchResult.student_id == profile.id,
            MatchResult.job_id == job.id,
        ).first()
        if not mr:
            mr = MatchResult(student_id=profile.id, job_id=job.id)
            db.add(mr)

        mr.rule_score = scores["rule_score"]
        mr.semantic_score = scores["semantic_score"]
        mr.llm_score = scores["llm_score"]
        mr.final_score = scores["final_score"]
        mr.matched_skills = scores["matched_skills"]
        mr.missing_skills = scores["missing_skills"]
        mr.explanation = scores["explanation"]
        mr.ats_score = scores["ats_score"]
        mr.improvement_suggestions = scores["improvement_suggestions"]

    match_ms = round((time.perf_counter() - t_match) * 1000, 1)
    db.commit()
    total_ms = round((time.perf_counter() - t_start) * 1000, 1)

    return {
        "message": "Resume uploaded and processed successfully",
        "skills_extracted": len(parsed.get("skills", [])),
        "parsed_info": parsed,
        "performance": {
            "text_extraction_ms": parse_ms,
            "llm_parsing_ms": llm_ms,
            "job_matching_ms": match_ms,
            "total_ms": total_ms,
        },
    }


@router.get("/me/matches", response_model=List[MatchOut])
def get_my_matches(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    profile = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    results = (
        db.query(MatchResult)
        .filter(MatchResult.student_id == profile.id)
        .order_by(MatchResult.final_score.desc())
        .all()
    )
    return results


@router.get("/me/suggestions/{job_id}")
def get_suggestions(
    job_id: int,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    profile = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    mr = db.query(MatchResult).filter(
        MatchResult.student_id == profile.id,
        MatchResult.job_id == job_id,
    ).first()
    if not mr:
        raise HTTPException(status_code=404, detail="No match result for this job")

    job = db.query(Job).filter(Job.id == job_id).first()

    return {
        "job_title": job.title if job else "",
        "ats_score": mr.ats_score,
        "final_score": mr.final_score,
        "matched_skills": mr.matched_skills or [],
        "missing_skills": mr.missing_skills or [],
        "explanation": mr.explanation or "",
        "improvement_suggestions": mr.improvement_suggestions or [],
    }
