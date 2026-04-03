from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(256), unique=True, nullable=False)
    title = db.Column(db.String(512), nullable=False)
    company = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256))
    url = db.Column(db.String(1024))
    description = db.Column(db.Text)
    source = db.Column(db.String(64))
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    salary_currency = db.Column(db.String(10))
    tags = db.Column(db.String(512))
    status = db.Column(
        db.String(32), default="saved"
    )  # saved, applied, interviewing, rejected, offer
    notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "description": self.description,
            "source": self.source,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "tags": self.tags.split(",") if self.tags else [],
            "status": self.status,
            "notes": self.notes,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat(),
        }


class SearchHistory(db.Model):
    __tablename__ = "search_history"

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256))
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
