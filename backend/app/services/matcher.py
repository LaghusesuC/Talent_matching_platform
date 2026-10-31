"""
Matching service: combines rule-based, semantic, and LLM scores into a final score.
Supports high-speed instant matching (rule + sentence-transformers semantic embeddings)
and deep LLM-augmented analysis.
"""
from app.services.embeddings import semantic_similarity
from app.services.llm import llm_match_analysis, compute_ats_score


def rule_based_score(resume_skills: list, required_skills: list) -> float:
    """Percentage of required skills found in the resume."""
    if not required_skills:
        return 75.0
    if not resume_skills:
        return 10.0
    resume_lower = [s.lower() for s in resume_skills]
    matched = [s for s in required_skills if s.lower() in resume_lower]
    return round((len(matched) / len(required_skills)) * 100, 2)


def compute_match(
    resume_text: str,
    jd_text: str,
    resume_info: dict,
    jd_info: dict,
    run_llm: bool = False,
) -> dict:
    """
    Match computation for candidate and job description.
    When run_llm=False (default for batch/upload), runs in milliseconds using
    fast skill intersection and Sentence-Transformers vector similarity.
    When run_llm=True, enriches with deep Gemini LLM analysis.
    """
    resume_skills = resume_info.get("skills", [])
    required_skills = jd_info.get("required_skills", [])
    rule_score = rule_based_score(resume_skills, required_skills)
    sem_score = semantic_similarity(resume_text, jd_text)
    ats_score = compute_ats_score(resume_text, jd_info)

    if run_llm:
        llm_result = llm_match_analysis(resume_text, jd_text, resume_info, jd_info)
        llm_score = float(llm_result.get("suitability_score", rule_score))
        final_score = round(0.4 * rule_score + 0.3 * sem_score + 0.3 * llm_score, 2)
        matched_skills = llm_result.get("matched_skills", [])
        missing_skills = llm_result.get("missing_skills", [])
        explanation = llm_result.get("explanation", "")
        improvement_suggestions = llm_result.get("improvement_suggestions", [])
    else:
        # Fast matching: instant set-based skill comparison and weighted scoring
        resume_lower_set = {s.lower() for s in resume_skills}
        matched_skills = [s for s in required_skills if s.lower() in resume_lower_set]
        missing_skills = [s for s in required_skills if s.lower() not in resume_lower_set]
        
        # Fast composite score
        llm_score = round(0.5 * rule_score + 0.5 * sem_score, 2)
        final_score = round(0.40 * rule_score + 0.35 * sem_score + 0.25 * ats_score, 2)

        match_count = len(matched_skills)
        req_count = len(required_skills)
        explanation = (
            f"Candidate matches {match_count} of {req_count} required technical competencies "
            f"with a {round(sem_score)}% semantic alignment to this role."
        ) if req_count else f"Semantic profile alignment: {round(sem_score)}% match."

        improvement_suggestions = [
            f"Showcase practical projects or certifications in {s}" for s in missing_skills[:4]
        ]
        if not improvement_suggestions:
            improvement_suggestions = [
                "Profile has strong coverage of required skills",
                "Ensure key impact metrics and project outcomes are highlighted"
            ]

    return {
        "rule_score": rule_score,
        "semantic_score": sem_score,
        "llm_score": llm_score,
        "final_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "explanation": explanation,
        "improvement_suggestions": improvement_suggestions,
        "ats_score": ats_score,
    }
