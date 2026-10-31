from pydantic import BaseModel
from typing import Optional, Any, Dict


class StudentProfile(BaseModel):
    id: int
    user_id: int
    cgpa: Optional[float] = None
    department: Optional[str] = None
    resume_path: Optional[str] = None
    parsed_json: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    title: str
    description: str
    skills_required: Optional[list] = []
    company_name: Optional[str] = None


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    skills_required: Optional[list] = []
    recruiter_id: int
    company_name: Optional[str] = None

    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    rule_score: float
    semantic_score: float
    llm_score: float
    final_score: float
    rank: Optional[int] = None
    matched_skills: Optional[list] = []
    missing_skills: Optional[list] = []
    explanation: Optional[str] = None
    ats_score: float = 0.0
    improvement_suggestions: Optional[list] = []
    job: Optional[JobOut] = None

    model_config = {"from_attributes": True}


class CandidateOut(BaseModel):
    student_id: int
    name: str
    email: str
    department: Optional[str] = None
    cgpa: Optional[float] = None
    final_score: float
    rule_score: float
    semantic_score: float
    llm_score: float
    rank: Optional[int] = None
    matched_skills: Optional[list] = []
    missing_skills: Optional[list] = []
    explanation: Optional[str] = None
    ats_score: float = 0.0
    match_id: int

    model_config = {"from_attributes": True}


class ShortlistCreate(BaseModel):
    student_id: int
    status: str = "shortlisted"


class ShortlistOut(BaseModel):
    id: int
    job_id: int
    student_id: int
    status: str

    model_config = {"from_attributes": True}


class StudentCreate(BaseModel):
    name: str
    email: str
    department: Optional[str] = None
    cgpa: Optional[float] = None
    password: str = "student123"  # default password for bulk-added students


class StudentOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    department: Optional[str] = None
    cgpa: Optional[float] = None
    resume_path: Optional[str] = None
    skills: Optional[list] = []

    model_config = {"from_attributes": True}


class BulkStudentCreate(BaseModel):
    students: list[StudentCreate]
