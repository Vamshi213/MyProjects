import os
import uuid
import hashlib
import concurrent.futures
from datetime import datetime
from pathlib import Path

import bleach
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from sqlalchemy import select, func, update

from config import Config
from models import db, Resume, SavedJob, SearchHistory
from job_sources import (
    RemoteOKSource,
    TheMuseSource,
    AdzunaSource,
    ArbeitnowSource,
    HackerNewsSource,
)
from job_sources.demo_data import search_demo

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)

Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

# ── Job sources ──────────────────────────────────────────────────────────────

def get_sources():
    return [
        RemoteOKSource(),
        TheMuseSource(),
        ArbeitnowSource(),
        # Adzuna: uses live API when keys are set, demo data otherwise
        AdzunaSource(
            app_id=app.config["ADZUNA_APP_ID"],
            api_key=app.config["ADZUNA_API_KEY"],
            country=app.config["ADZUNA_COUNTRY"],
        ),
        HackerNewsSource(),
    ]


# ── Helpers ──────────────────────────────────────────────────────────────────

ALLOWED_TAGS: list[str] = []


def sanitize(text: str) -> str:
    return bleach.clean(str(text), tags=ALLOWED_TAGS, strip=True)


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─── Job Search ──────────────────────────────────────────────────────────────

@app.route("/api/jobs/search")
def search_jobs():
    query = sanitize(request.args.get("q", "").strip())
    location = sanitize(request.args.get("location", "").strip())
    sources_param = request.args.get("sources", "")
    page = max(1, int(request.args.get("page", 1)))

    if not query:
        return jsonify({"error": "Search query is required"}), 400
    if len(query) > 200:
        return jsonify({"error": "Query too long"}), 400

    active_sources = get_sources()
    if sources_param:
        wanted = set(sources_param.split(","))
        active_sources = [s for s in active_sources if s.name in wanted]

    all_jobs: list[dict] = []

    def fetch(source):
        try:
            return source.search(query, location, page)
        except Exception:
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch, src): src.name for src in active_sources}
        for fut in concurrent.futures.as_completed(futures, timeout=15):
            all_jobs.extend(fut.result())

    # If all live sources returned nothing, serve the full demo dataset
    if not all_jobs:
        all_jobs = search_demo(query, location)

    seen: set[str] = set()
    unique: list[dict] = []
    for job in all_jobs:
        key = hashlib.md5(
            f"{job['title'].lower()}_{job['company'].lower()}".encode()
        ).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(job)

    try:
        sh = SearchHistory(query=query, location=location, results_count=len(unique))
        db.session.add(sh)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"jobs": unique, "total": len(unique), "query": query})


@app.route("/api/jobs/sources")
def list_sources():
    sources = get_sources()
    return jsonify(
        [{"name": s.name, "display_name": s.display_name, "logo_color": s.logo_color}
         for s in sources]
    )


# ─── Saved Jobs ──────────────────────────────────────────────────────────────

@app.route("/api/jobs/save", methods=["POST"])
def save_job():
    data = request.get_json(silent=True) or {}
    job_id = sanitize(data.get("job_id", ""))
    if not job_id:
        return jsonify({"error": "job_id required"}), 400

    existing = db.session.execute(
        select(SavedJob).where(SavedJob.job_id == job_id)
    ).scalar_one_or_none()
    if existing:
        return jsonify({"message": "Already saved", "job": existing.to_dict()}), 200

    job = SavedJob(
        job_id=job_id,
        title=sanitize(data.get("title", ""))[:512],
        company=sanitize(data.get("company", ""))[:256],
        location=sanitize(data.get("location", ""))[:256],
        url=sanitize(data.get("url", ""))[:1024],
        description=sanitize(data.get("description", ""))[:2000],
        source=sanitize(data.get("source", ""))[:64],
        salary_min=data.get("salary_min"),
        salary_max=data.get("salary_max"),
        salary_currency=sanitize(data.get("salary_currency", "USD"))[:10],
        tags=",".join(sanitize(t) for t in (data.get("tags") or []))[:512],
        status="saved",
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job saved", "job": job.to_dict()}), 201


@app.route("/api/jobs/saved")
def get_saved_jobs():
    status = request.args.get("status", "")
    stmt = select(SavedJob).order_by(SavedJob.created_at.desc())
    if status:
        stmt = stmt.where(SavedJob.status == status)
    jobs = db.session.execute(stmt).scalars().all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]})


@app.route("/api/jobs/saved/<int:job_id>", methods=["PATCH"])
def update_saved_job(job_id: int):
    job = db.get_or_404(SavedJob, job_id)
    data = request.get_json(silent=True) or {}
    allowed_statuses = {"saved", "applied", "interviewing", "rejected", "offer"}
    if "status" in data:
        new_status = sanitize(data["status"])
        if new_status not in allowed_statuses:
            return jsonify({"error": "Invalid status"}), 400
        job.status = new_status
        if new_status == "applied" and not job.applied_at:
            job.applied_at = datetime.utcnow()
    if "notes" in data:
        job.notes = sanitize(data["notes"])[:2000]
    db.session.commit()
    return jsonify({"job": job.to_dict()})


@app.route("/api/jobs/saved/<int:job_id>", methods=["DELETE"])
def delete_saved_job(job_id: int):
    job = db.get_or_404(SavedJob, job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ─── Resumes ─────────────────────────────────────────────────────────────────

@app.route("/api/resumes", methods=["GET"])
def list_resumes():
    resumes = db.session.execute(
        select(Resume).order_by(Resume.created_at.desc())
    ).scalars().all()
    return jsonify({"resumes": [r.to_dict() for r in resumes]})


@app.route("/api/resumes/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["resume"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use PDF, DOCX, DOC, or TXT"}), 400

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

    file.save(save_path)
    file_size = os.path.getsize(save_path)

    # Deactivate existing
    db.session.execute(update(Resume).values(is_active=False))

    resume = Resume(
        filename=unique_name,
        original_name=original_name,
        file_path=save_path,
        file_type=ext,
        file_size=file_size,
        is_active=True,
    )
    db.session.add(resume)
    db.session.commit()
    return jsonify({"message": "Resume uploaded", "resume": resume.to_dict()}), 201


@app.route("/api/resumes/<int:resume_id>/activate", methods=["PATCH"])
def activate_resume(resume_id: int):
    resume = db.get_or_404(Resume, resume_id)
    db.session.execute(update(Resume).values(is_active=False))
    resume.is_active = True
    db.session.commit()
    return jsonify({"resume": resume.to_dict()})


@app.route("/api/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id: int):
    resume = db.get_or_404(Resume, resume_id)
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except OSError:
        pass
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"message": "Resume deleted"})


@app.route("/api/resumes/<int:resume_id>/download")
def download_resume(resume_id: int):
    resume = db.get_or_404(Resume, resume_id)
    directory = os.path.dirname(resume.file_path)
    return send_from_directory(
        directory,
        resume.filename,
        as_attachment=True,
        download_name=resume.original_name,
    )


# ─── Stats ───────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def get_stats():
    total_saved = db.session.execute(
        select(func.count(SavedJob.id))
    ).scalar_one()

    by_status_rows = db.session.execute(
        select(SavedJob.status, func.count(SavedJob.id)).group_by(SavedJob.status)
    ).all()

    recent_searches = db.session.execute(
        select(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(10)
    ).scalars().all()

    active_resume = db.session.execute(
        select(Resume).where(Resume.is_active == True)  # noqa: E712
    ).scalar_one_or_none()

    return jsonify({
        "total_saved": total_saved,
        "by_status": {s: c for s, c in by_status_rows},
        "recent_searches": [
            {"query": sh.query, "results": sh.results_count}
            for sh in recent_searches
        ],
        "active_resume": active_resume.to_dict() if active_resume else None,
    })


# ─── Bootstrap DB ────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
