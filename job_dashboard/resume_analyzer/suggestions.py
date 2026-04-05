"""
Senior-recruiter suggestion engine.

Produces actionable, role-specific recommendations to get into the top 1%:
- Weak bullet rewrites
- Missing skills to add
- Bullet point templates for the role
- Top 1% differentiation signals
- ATS quick wins
"""
import re
from typing import Dict, List

from .skills_db import (
    WEAK_TO_STRONG_MAP,
    ROLE_BULLET_TEMPLATES,
    TOP_1_PERCENT_SIGNALS,
    HIGH_VALUE_CERTS,
)


def generate_suggestions(parsed: Dict, score_result: Dict, job: Dict) -> Dict:
    role = _detect_role(job)

    return {
        "role_detected": role,
        "quick_wins":          _quick_wins(parsed, score_result),
        "missing_skills":      _missing_skills_advice(score_result["missing_skills"]),
        "bullet_rewrites":     _bullet_rewrites(parsed),
        "bullet_templates":    ROLE_BULLET_TEMPLATES.get(role, ROLE_BULLET_TEMPLATES.get("software engineer", [])),
        "top_1_percent":       TOP_1_PERCENT_SIGNALS.get(role, []),
        "cert_suggestions":    _cert_suggestions(parsed, role),
        "ats_fixes":           _ats_fixes(parsed, score_result),
        "recruiter_red_flags": _recruiter_red_flags(parsed),
        "power_verbs":         _power_verb_swaps(parsed),
    }


# ── Role detection ────────────────────────────────────────────────────────────

def _detect_role(job: Dict) -> str:
    title = (job.get("title", "") + " " + job.get("description", "")).lower()
    role_map = [
        ("engineering manager", ["engineering manager", "em ", "head of engineering"]),
        ("machine learning engineer", ["machine learning", "ml engineer", "mlops", "ai engineer"]),
        ("data engineer", ["data engineer", "data pipeline", "etl", "data platform"]),
        ("security engineer", ["security engineer", "appsec", "infosec", "devsecops"]),
        ("devops engineer", ["devops", "platform engineer", "sre", "site reliability", "infrastructure engineer"]),
        ("frontend engineer", ["frontend", "front-end", "react developer", "ui engineer"]),
        ("backend engineer", ["backend", "back-end", "api engineer", "server-side"]),
        ("product manager", ["product manager", "pm ", "product owner", "head of product"]),
        ("software engineer", ["software engineer", "software developer", "full stack", "fullstack"]),
    ]
    for role, keywords in role_map:
        if any(k in title for k in keywords):
            return role
    return "software engineer"


# ── Quick wins ────────────────────────────────────────────────────────────────

def _quick_wins(parsed: Dict, score_result: Dict) -> List[str]:
    wins = []
    if score_result["ats_score"] < 60:
        wins.append("Add a dedicated Skills section listing your tech stack — ATS scanners look for this first")
    if not re.search(r"github\.com", parsed.get("text_lower", "")):
        wins.append("Add your GitHub profile URL — 73% of top tech candidates include it and it's instant credibility")
    if not re.search(r"linkedin\.com", parsed.get("text_lower", "")):
        wins.append("Add your LinkedIn URL — recruiters verify profiles before reaching out")
    if parsed.get("metric_count", 0) < 3:
        wins.append("Add at least 3 quantified achievements (%, $, X times) — resumes with metrics get 40% more callbacks")
    if len(parsed.get("weak_verbs_found", [])) > 2:
        wins.append(f"Replace weak verbs ({', '.join(parsed['weak_verbs_found'][:3])}) with strong action verbs")
    if parsed.get("word_count", 0) < 350:
        wins.append("Resume is too short — expand bullet points with context, tools used, and impact")
    if not parsed.get("certifications"):
        wins.append("Consider adding a relevant certification (AWS, CKA, etc.) — it filters you into screened pools")
    if score_result["keyword_coverage"] < 50:
        wins.append("Mirror the job description language — use the same tech/skill names verbatim for ATS")
    return wins[:6]


# ── Missing skills ────────────────────────────────────────────────────────────

def _missing_skills_advice(missing: List[str]) -> List[Dict]:
    advice = []
    priority_map = {
        # Cloud
        "aws": ("high", "Most in-demand cloud platform. Add if you've used any AWS service even in side projects"),
        "kubernetes": ("high", "Required for most platform/backend roles. Even basic kubectl knowledge counts"),
        "docker": ("high", "Ubiquitous — if you containerised anything, list it"),
        "terraform": ("medium", "Infrastructure-as-code is expected for senior roles"),
        # Languages
        "go": ("medium", "Growing fast in backend/infra. List if you've used it"),
        "rust": ("medium", "High signal for systems/infra roles"),
        "typescript": ("high", "Expected for all modern JS roles — if you use JS, upgrade to TS on your resume"),
        # Data
        "dbt": ("medium", "Standard for data engineering stacks"),
        "kafka": ("medium", "Event streaming knowledge is expected for distributed systems"),
        # ML
        "pytorch": ("high", "Industry standard for ML — required for ML roles"),
        "llm": ("high", "LLM experience is the top differentiator for AI/ML roles right now"),
        "rag": ("high", "RAG is the most requested AI skill in 2024–2025"),
    }
    for skill in missing[:15]:
        pri, note = priority_map.get(skill, ("low", f"Required by this job — add if applicable"))
        advice.append({"skill": skill, "priority": pri, "advice": note})
    # Sort: high first
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(advice, key=lambda x: order.get(x["priority"], 3))


# ── Bullet rewrites ───────────────────────────────────────────────────────────

def _bullet_rewrites(parsed: Dict) -> List[Dict]:
    """Find bullets with weak verbs and suggest rewrites."""
    text = parsed.get("text", "")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    bullet_lines = [l for l in lines if re.match(r"^[•\-·◦▸→*]\s", l) or
                    re.match(r"^\s*[-•·]\s", l)]

    rewrites = []
    for line in bullet_lines[:30]:  # check first 30 bullets
        line_lower = line.lower()
        for weak, strong in WEAK_TO_STRONG_MAP.items():
            if weak in line_lower:
                improved = re.sub(re.escape(weak), strong, line, flags=re.IGNORECASE, count=1)
                if not _has_metrics_inline(line):
                    improved += " — add a metric: (e.g. reduced X by Y%, improved Z from A to B)"
                rewrites.append({
                    "original": line[:120],
                    "improved": improved[:160],
                    "issue": f"Weak verb '{weak}' → replace with '{strong}'",
                })
                break
        if len(rewrites) >= 5:
            break
    return rewrites


def _has_metrics_inline(line: str) -> bool:
    return bool(re.search(r"\d+[%xX]|\$[\d,]+|\d+[kmb]\b", line, re.IGNORECASE))


# ── ATS fixes ────────────────────────────────────────────────────────────────

def _ats_fixes(parsed: Dict, score_result: Dict) -> List[str]:
    fixes = []
    tl = parsed.get("text_lower", "")

    if score_result["keyword_coverage"] < 60:
        fixes.append("Use exact keywords from the job description — ATS systems match verbatim strings")
    if not re.search(r"\b(skills?|technologies?|tech stack)\b", tl):
        fixes.append("Add a 'Skills' or 'Tech Stack' section — it's the #1 ATS target section")
    if not re.search(r"\b(summary|objective|profile)\b", tl):
        fixes.append("Add a 2-line summary at the top with your title and top 3 strengths")
    if parsed.get("word_count", 0) < 300:
        fixes.append("Expand your resume — ATS scores drop below 300 words due to low keyword density")
    if len(score_result.get("missing_skills", [])) > 8:
        fixes.append("You're missing many required skills — tailor your resume for this specific role")
    return fixes


# ── Recruiter red flags ────────────────────────────────────────────────────────

def _recruiter_red_flags(parsed: Dict) -> List[str]:
    flags = []
    if parsed.get("metric_count", 0) == 0:
        flags.append("Zero quantified achievements — recruiters skip resumes with no numbers")
    if len(parsed.get("weak_verbs_found", [])) > 3:
        flags.append("Too many passive/weak verbs signal low ownership and impact")
    if parsed.get("word_count", 0) > 1200:
        flags.append("Resume is too long — senior recruiters spend 6-7 seconds; cut to 1-2 pages")
    if not parsed.get("has_links"):
        flags.append("No GitHub or portfolio — hard to verify technical claims without proof")
    yoe = parsed.get("years_experience", 0)
    if yoe == 0:
        flags.append("Cannot detect work experience dates — ensure years are clearly formatted (e.g. 2020–2023)")
    return flags


# ── Power verb swaps ──────────────────────────────────────────────────────────

def _power_verb_swaps(parsed: Dict) -> List[Dict]:
    return [
        {"weak": w, "strong": WEAK_TO_STRONG_MAP.get(w, "use a stronger action verb")}
        for w in parsed.get("weak_verbs_found", [])
    ]


# ── Cert suggestions ──────────────────────────────────────────────────────────

def _cert_suggestions(parsed: Dict, role: str) -> List[str]:
    existing = set(parsed.get("certifications", []))
    role_cert_map = {
        "devops engineer":         HIGH_VALUE_CERTS["cloud"],
        "backend engineer":        HIGH_VALUE_CERTS["cloud"],
        "software engineer":       HIGH_VALUE_CERTS["cloud"],
        "data engineer":           HIGH_VALUE_CERTS["data"],
        "machine learning engineer": HIGH_VALUE_CERTS["ml"],
        "security engineer":       HIGH_VALUE_CERTS["security"],
    }
    suggestions = role_cert_map.get(role, HIGH_VALUE_CERTS["cloud"])
    return [c for c in suggestions if c not in existing][:3]
