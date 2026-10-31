from sqlalchemy import Column, Integer, Float, ForeignKey, Text, JSON, String
from sqlalchemy.orm import relationship
from app.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    rule_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    llm_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    matched_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    ats_score = Column(Float, default=0.0)
    improvement_suggestions = Column(JSON, nullable=True)

    student = relationship("Student", backref="match_results")
    job = relationship("Job", backref="match_results")


class Shortlist(Base):
    __tablename__ = "shortlists"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String, default="shortlisted")  # shortlisted, rejected, hired

    job = relationship("Job", backref="shortlists")
    student = relationship("Student", backref="shortlists")
