import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.job import Job
from app.models.recruiter import Recruiter
from app.models.user import User
from app.models.student import Student
from app.models.match import MatchResult
from app.core.security import hash_password
from app.routers.admin import PREDEFINED_JOBS
from app.services.matcher import compute_match
import app.services.embeddings as emb

# Pre-set model_failed so it doesn't wait for network timeouts in sandbox
emb._model_failed = True

def run():
    db = SessionLocal()
    try:
        # Update first 3 jobs if they don't have company_name
        j1 = db.query(Job).filter(Job.id == 1).first()
        if j1 and not j1.company_name:
            j1.company_name = "Zoho"
        j2 = db.query(Job).filter(Job.id == 2).first()
        if j2 and not j2.company_name:
            j2.company_name = "TCS"
        j3 = db.query(Job).filter(Job.id == 3).first()
        if j3 and not j3.company_name:
            j3.company_name = "Infosys"
        db.commit()

        # Seed PREDEFINED_JOBS
        created_count = 0
        skipped_count = 0

        for job_data in PREDEFINED_JOBS:
            company = job_data["company_name"]
            title = job_data["title"]

            exists = db.query(Job).filter(
                Job.title == title,
                Job.company_name == company
            ).first()
            if exists:
                skipped_count += 1
                continue

            # Find or create recruiter
            recruiter = db.query(Recruiter).filter(Recruiter.company_name == company).first()
            if not recruiter:
                email_slug = company.lower().replace(" ", "").replace("&", "")[:12]
                rec_email = f"hr@{email_slug}.com"
                rec_user = db.query(User).filter(User.email == rec_email).first()
                if not rec_user:
                    rec_user = User(
                        name=f"{company} HR",
                        email=rec_email,
                        password_hash=hash_password("recruiter123"),
                        role="recruiter",
                    )
                    db.add(rec_user)
                    db.flush()

                recruiter = Recruiter(user_id=rec_user.id, company_name=company)
                db.add(recruiter)
                db.flush()

            job = Job(
                recruiter_id=recruiter.id,
                title=title,
                company_name=company,
                description=job_data["description"],
                skills_required=job_data["skills_required"],
                parsed_json={
                    "required_skills": job_data["skills_required"],
                    "preferred_skills": [],
                    "keywords": job_data["skills_required"],
                },
            )
            db.add(job)
            db.flush()

            # Match with existing students with resumes
            students = db.query(Student).filter(Student.resume_text.isnot(None)).all()
            for student in students:
                resume_info = student.parsed_json or {}
                jd_info = job.parsed_json
                scores = compute_match(
                    student.resume_text or "",
                    job_data["description"],
                    resume_info,
                    jd_info,
                    run_llm=False,
                )
                mr = MatchResult(
                    student_id=student.id,
                    job_id=job.id,
                    rule_score=scores["rule_score"],
                    semantic_score=scores["semantic_score"],
                    llm_score=scores["llm_score"],
                    final_score=scores["final_score"],
                    matched_skills=scores["matched_skills"],
                    missing_skills=scores["missing_skills"],
                    explanation=scores["explanation"],
                    ats_score=scores["ats_score"],
                    improvement_suggestions=scores["improvement_suggestions"],
                )
                db.add(mr)

            created_count += 1
            print(f"[{created_count}] Created: {company} - {title}")

        db.commit()
        print(f"\nDone! Created: {created_count}, Skipped: {skipped_count}")

        # Summary of jobs by company
        jobs = db.query(Job).all()
        print(f"Total jobs in DB: {len(jobs)}")

    finally:
        db.close()

if __name__ == "__main__":
    run()
