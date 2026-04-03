"""
ATS + Senior Recruiter scoring engine.

Produces two independent scores:
- ats_score     (0-100): How well the resume passes automated screening
- recruiter_score (0-100): How compelling it reads to a senior recruiter

Combined into an overall_score weighted 40% ATS / 60% recruiter.
"""
import re
import math
from typing import Dict, List, Tuple

from .skills_db import ALL_SKILLS, STRONG_VERBS, WEAK_VERBS


# ── Public API ────────────────────────────────────────────────────────────────

def score_resume(parsed: Dict, job: Dict) -> Dict:
    """
    Score a parsed resume against a job posting.
    Returns detailed score breakdown.
    """
    job_text = _build_job_text(job)
    job_lower = job_text.lower()

    jd_keywords   = _extract_jd_keywords(job_lower)
    jd_skills     = _extract_jd_skills(job_lower)
    resume_skills = set(parsed.get("skills", []))

    ats     = _ats_score(parsed, jd_keywords, jd_skills, resume_skills)
    rec     = _recruiter_score(parsed, jd_skills, resume_skills)
    overall = round(ats["score"] * 0.40 + rec["score"] * 0.60)

    matched_skills  = sorted(resume_skills & jd_skills)
    missing_skills  = sorted(jd_skills - resume_skills)
    bonus_skills    = sorted(resume_skills - jd_skills)[:10]

    return {
        "overall_score":    overall,
        "ats_score":        ats["score"],
        "recruiter_score":  rec["score"],
        "ats_breakdown":    ats["breakdown"],
        "recruiter_breakdown": rec["breakdown"],
        "matched_skills":   matched_skills,
        "missing_skills":   missing_skills[:20],
        "bonus_skills":     bonus_skills,
        "keyword_coverage": ats["keyword_coverage"],
        "grade":            _grade(overall),
    }


# ── ATS Score ─────────────────────────────────────────────────────────────────

def _ats_score(parsed: Dict, jd_keywords: List[str], jd_skills: set, resume_skills: set) -> Dict:
    text_lower = parsed.get("text_lower", "")
    breakdown  = {}

    # 1. Keyword match (30 pts)
    kw_matches = sum(1 for kw in jd_keywords if kw in text_lower)
    kw_ratio   = kw_matches / max(len(jd_keywords), 1)
    kw_pts     = round(kw_ratio * 30)
    breakdown["keyword_match"] = {
        "score": kw_pts, "max": 30,
        "detail": f"{kw_matches}/{len(jd_keywords)} job keywords found",
    }

    # 2. Skills match (30 pts)
    matched = resume_skills & jd_skills
    sk_ratio = len(matched) / max(len(jd_skills), 1)
    sk_pts   = round(sk_ratio * 30)
    breakdown["skills_match"] = {
        "score": sk_pts, "max": 30,
        "detail": f"{len(matched)}/{len(jd_skills)} required skills matched",
    }

    # 3. Contact & sections (20 pts)
    section_score = 0
    checks = {
        "email":      bool(re.search(r"[\w._%+-]+@[\w.-]+\.\w+", parsed.get("text", ""))),
        "phone":      bool(re.search(r"\+?[\d\s\-().]{10,}", parsed.get("text", ""))),
        "linkedin":   "linkedin" in parsed.get("text_lower", ""),
        "github":     "github" in parsed.get("text_lower", ""),
        "skills_sec": bool(re.search(r"\bskills?\b", parsed.get("text_lower", ""))),
        "experience": bool(re.search(r"\b(experience|employment|work history)\b", parsed.get("text_lower", ""))),
        "education":  bool(re.search(r"\b(education|degree|university|college)\b", parsed.get("text_lower", ""))),
    }
    for k, v in checks.items():
        if v:
            section_score += {"email": 4, "phone": 2, "linkedin": 3, "github": 3,
                               "skills_sec": 3, "experience": 3, "education": 2}.get(k, 1)
    section_score = min(section_score, 20)
    breakdown["profile_completeness"] = {
        "score": section_score, "max": 20,
        "detail": f"{sum(checks.values())}/7 profile sections present",
    }

    # 4. Format / length (20 pts)
    wc  = parsed.get("word_count", 0)
    fmt = 20
    if wc < 200:
        fmt = 6
    elif wc < 350:
        fmt = 12
    elif wc > 1200:
        fmt = 14
    breakdown["format_length"] = {
        "score": fmt, "max": 20,
        "detail": f"{wc} words — {'good length' if 350 <= wc <= 1000 else 'needs more detail' if wc < 350 else 'slightly long'}",
    }

    total = kw_pts + sk_pts + section_score + fmt
    return {
        "score": min(total, 100),
        "breakdown": breakdown,
        "keyword_coverage": round(kw_ratio * 100),
    }


# ── Recruiter Score ───────────────────────────────────────────────────────────

def _recruiter_score(parsed: Dict, jd_skills: set, resume_skills: set) -> Dict:
    breakdown = {}

    # 1. Quantified impact (25 pts)
    mc   = parsed.get("metric_count", 0)
    q_pts = min(25, mc * 4)
    breakdown["quantified_impact"] = {
        "score": q_pts, "max": 25,
        "detail": f"{mc} metrics/numbers found" + (" — needs more quantification" if mc < 4 else ""),
    }

    # 2. Action verb quality (20 pts)
    strong = len(parsed.get("strong_verbs_found", []))
    weak   = len(parsed.get("weak_verbs_found", []))
    verb_score = min(20, strong * 3) - weak * 2
    verb_score = max(0, min(verb_score, 20))
    breakdown["action_verbs"] = {
        "score": verb_score, "max": 20,
        "detail": f"{strong} strong verbs, {weak} weak verbs",
    }

    # 3. Technical depth (20 pts)
    tech_depth = min(20, len(resume_skills) * 1.2)
    tech_depth = round(min(tech_depth, 20))
    breakdown["technical_depth"] = {
        "score": tech_depth, "max": 20,
        "detail": f"{len(resume_skills)} technical skills identified",
    }

    # 4. Years of experience signal (15 pts)
    yoe  = parsed.get("years_experience", 0)
    ye_pts = min(15, yoe * 2)
    breakdown["experience_signal"] = {
        "score": ye_pts, "max": 15,
        "detail": f"~{yoe} years experience detected",
    }

    # 5. Links & proof (10 pts)
    link_pts = 0
    tl = parsed.get("text_lower", "")
    if "github.com" in tl:   link_pts += 5
    if "linkedin.com" in tl:  link_pts += 3
    if any(k in tl for k in ("portfolio", "website", "blog")):
        link_pts += 2
    link_pts = min(link_pts, 10)
    breakdown["proof_links"] = {
        "score": link_pts, "max": 10,
        "detail": "GitHub/LinkedIn/portfolio links",
    }

    # 6. Education & certs (10 pts)
    edu  = parsed.get("education", {})
    certs = parsed.get("certifications", [])
    edu_pts = {"phd": 10, "masters": 8, "bachelors": 6, "bootcamp": 3}.get(
        edu.get("highest", ""), 4)
    if edu.get("has_cs_degree"):
        edu_pts = min(10, edu_pts + 1)
    if certs:
        edu_pts = min(10, edu_pts + len(certs))
    breakdown["education_certs"] = {
        "score": edu_pts, "max": 10,
        "detail": f"Highest: {edu.get('highest', 'unknown')}, {len(certs)} cert(s)",
    }

    total = q_pts + verb_score + tech_depth + ye_pts + link_pts + edu_pts
    return {"score": min(total, 100), "breakdown": breakdown}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_job_text(job: Dict) -> str:
    return " ".join([
        job.get("title", ""),
        job.get("description", ""),
        " ".join(job.get("tags", [])),
    ])


def _extract_jd_keywords(jd_lower: str) -> List[str]:
    """Extract meaningful keywords from job description (no stopwords)."""
    stopwords = {
        "and", "the", "with", "for", "you", "our", "are", "will", "have",
        "that", "this", "from", "they", "your", "but", "not", "been",
        "their", "who", "can", "all", "an", "to", "a", "in", "of", "on",
        "at", "by", "as", "we", "or", "if", "it", "be", "is", "us",
        "work", "team", "role", "job", "company", "experience", "ability",
        "strong", "good", "great", "looking", "help", "use", "new",
        "across", "within", "into", "through", "about",
    }
    words = re.findall(r"\b[a-z][a-z+#./-]{2,}\b", jd_lower)
    return [w for w in words if w not in stopwords]


def _extract_jd_skills(jd_lower: str) -> set:
    """Extract skills mentioned in the job description."""
    found = set()
    for skill in ALL_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, jd_lower):
            found.add(skill)
    return found


def _grade(score: int) -> Dict:
    if score >= 85:
        return {"letter": "A", "label": "Excellent Match", "color": "#3fb950"}
    elif score >= 70:
        return {"letter": "B", "label": "Good Match", "color": "#58a6ff"}
    elif score >= 55:
        return {"letter": "C", "label": "Fair Match", "color": "#d29922"}
    elif score >= 40:
        return {"letter": "D", "label": "Weak Match", "color": "#e3893b"}
    else:
        return {"letter": "F", "label": "Poor Match", "color": "#f85149"}
