"""
LLM service using Gemini Flash API.
Falls back to a keyword-based extractor if the API key is not configured.
"""
import json
import re
import hashlib
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# Cache for parsed resume info to avoid redundant LLM calls
_resume_info_cache: dict[str, dict] = {}

# Lazy-init the Gemini model
_gemini_model = None


def _get_gemini():
    global _gemini_model
    if _gemini_model is None and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel("gemini-3.8-flash")
        except Exception:
            _gemini_model = None
    return _gemini_model


def _call_llm(prompt: str) -> Optional[str]:
    model = _get_gemini()
    if model is None:
        return None
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return None


def _parse_json_from_text(text: str) -> dict:
    """Extract the first valid JSON object from an LLM response.
    Handles markdown fences (```json ... ```) and Gemini 2.5 thinking output.
    """
    if not text:
        return {}

    # 1. Strip ```json ... ``` or ``` ... ``` fences first
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except Exception:
            pass

    # 2. Walk brackets to find the outermost { ... }
    try:
        start = text.index("{")
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start: i + 1])
    except (ValueError, json.JSONDecodeError):
        pass

    return {}


def extract_resume_info(resume_text: str) -> dict:
    """Extract skills, education, experience, projects from a resume.
    Results are cached by content hash to avoid redundant LLM calls."""
    # Check cache first
    text_hash = hashlib.md5(resume_text.encode()).hexdigest()
    if text_hash in _resume_info_cache:
        return _resume_info_cache[text_hash]

    prompt = f"""You are an expert resume parser. Extract structured information from the following resume text.

Return ONLY a JSON object with these keys:
- "skills": list of technical and soft skills
- "education": list of education entries (degree, institution, year, cgpa)
- "experience": list of work experience entries (company, role, duration, description)
- "projects": list of projects (name, description, technologies_used)
- "certifications": list of certifications
- "summary": a 2-sentence professional summary

Resume text:
\"\"\"
{resume_text[:4000]}
\"\"\"

Return ONLY the JSON object, no markdown, no explanation."""

    raw = _call_llm(prompt)
    if raw:
        data = _parse_json_from_text(raw)
        if data:
            _resume_info_cache[text_hash] = data
            return data

    # Fallback: basic keyword extraction
    result = _fallback_extract(resume_text)
    _resume_info_cache[text_hash] = result
    return result


def _fallback_extract(text: str) -> dict:
    """Simple keyword-based fallback extractor."""
    common_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "React", "Vue", "Angular", "Node.js", "FastAPI", "Django", "Flask", "Spring Boot",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Git",
        "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch",
        "Data Science", "Pandas", "NumPy", "Scikit-learn",
        "HTML", "CSS", "REST API", "GraphQL",
        "Agile", "Scrum", "Communication", "Leadership"
    ]
    found_skills = [s for s in common_skills if s.lower() in text.lower()]
    return {
        "skills": found_skills,
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "summary": "Resume parsed without LLM (fallback mode)."
    }


def extract_jd_info(jd_text: str) -> dict:
    """Extract required skills, responsibilities and qualifications from a JD."""
    prompt = f"""You are an expert at parsing job descriptions. Extract structured information.

Return ONLY a JSON object with:
- "required_skills": list of required technical skills
- "preferred_skills": list of nice-to-have skills
- "responsibilities": list of main responsibilities
- "qualifications": list of required qualifications (education, experience years)
- "keywords": important ATS keywords from the JD

Job description:
\"\"\"
{jd_text[:4000]}
\"\"\"

Return ONLY the JSON object."""

    raw = _call_llm(prompt)
    if raw:
        data = _parse_json_from_text(raw)
        if data:
            return data

    return {"required_skills": [], "preferred_skills": [], "responsibilities": [], "qualifications": [], "keywords": []}


def llm_match_analysis(resume_text: str, jd_text: str, resume_info: dict, jd_info: dict) -> dict:
    """
    Ask the LLM to compare a resume with a JD and return:
    - matched_skills, missing_skills, strengths, suitability_score (0-100), explanation
    """
    prompt = f"""You are a professional hiring assistant. Compare this candidate's resume with the job description and provide a detailed analysis.

Candidate skills: {resume_info.get('skills', [])}
Job required skills: {jd_info.get('required_skills', [])}

Resume summary:
{resume_text[:2000]}

Job description summary:
{jd_text[:2000]}

Return ONLY a JSON object with:
- "matched_skills": list of skills the candidate has that match the JD
- "missing_skills": list of required skills the candidate lacks
- "strengths": list of candidate strengths relevant to this role
- "suitability_score": integer from 0-100 representing overall fit
- "explanation": 3-4 sentence explanation of the match
- "improvement_suggestions": list of 3-5 actionable suggestions to improve the resume for this job"""

    raw = _call_llm(prompt)
    if raw:
        data = _parse_json_from_text(raw)
        if data:
            return data

    # Fallback match
    req_skills = [s.lower() for s in jd_info.get("required_skills", [])]
    cand_skills = [s.lower() for s in resume_info.get("skills", [])]
    matched = [s for s in req_skills if s in cand_skills]
    missing = [s for s in req_skills if s not in cand_skills]
    score = int((len(matched) / max(len(req_skills), 1)) * 100)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "strengths": [],
        "suitability_score": score,
        "explanation": f"Rule-based analysis: matched {len(matched)} of {len(req_skills)} required skills.",
        "improvement_suggestions": [f"Learn {s}" for s in missing[:3]]
    }


def generate_interview_questions(resume_info: dict, job_title: str) -> list:
    """Generate tailored interview questions for a candidate."""
    skills = resume_info.get("skills", [])
    projects = resume_info.get("projects", [])

    prompt = f"""Generate 8 targeted technical interview questions for a candidate applying for '{job_title}'.

Candidate skills: {skills}
Candidate projects: {[p.get('name', '') for p in projects]}

Return ONLY a JSON object with:
- "questions": list of 8 interview question strings

Make questions specific, technical, and relevant to the candidate's background."""

    raw = _call_llm(prompt)
    if raw:
        data = _parse_json_from_text(raw)
        if data and "questions" in data:
            return data["questions"]

    # Fallback
    return [
        f"Tell me about your experience with {skills[0] if skills else 'your primary skill'}.",
        "Describe a challenging project you worked on and how you solved it.",
        "How do you approach debugging complex problems?",
        "What is your greatest technical strength?",
        "Describe your experience working in a team environment.",
        "How do you keep up with new technologies?",
        "What motivates you to work in this domain?",
        "Where do you see yourself in 5 years?"
    ]


def compute_ats_score(resume_text: str, jd_info: dict) -> float:
    """Compute an ATS score (0-100) based on keyword matching, formatting signals."""
    keywords = jd_info.get("keywords", []) + jd_info.get("required_skills", [])
    if not keywords:
        return 50.0

    text_lower = resume_text.lower()
    matched = sum(1 for kw in keywords if kw.lower() in text_lower)
    keyword_score = (matched / len(keywords)) * 60  # up to 60 points

    # Formatting signals (heuristics)
    formatting_score = 0
    if len(resume_text) > 300:
        formatting_score += 10
    if any(h in resume_text.lower() for h in ["experience", "education", "skills", "projects"]):
        formatting_score += 15
    if any(c in resume_text for c in ["+", "@", "github", "linkedin"]):
        formatting_score += 10
    if len(resume_text.split()) > 150:
        formatting_score += 5

    return min(100.0, round(keyword_score + formatting_score, 1))
