import hashlib
from abc import ABC, abstractmethod
from typing import Any


class BaseJobSource(ABC):
    name: str = "base"
    display_name: str = "Base"
    logo_color: str = "#6366f1"

    def __init__(self):
        self.session = None

    @abstractmethod
    def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        """Return a list of normalized job dicts."""
        pass

    def make_job_id(self, *parts: Any) -> str:
        raw = "_".join(str(p) for p in parts)
        return f"{self.name}_{hashlib.md5(raw.encode()).hexdigest()[:12]}"

    def normalize(
        self,
        *,
        title: str,
        company: str,
        location: str = "Remote",
        url: str = "",
        description: str = "",
        salary_min: float | None = None,
        salary_max: float | None = None,
        salary_currency: str = "USD",
        tags: list[str] | None = None,
        job_id: str | None = None,
        posted_at: str | None = None,
    ) -> dict:
        return {
            "job_id": job_id or self.make_job_id(title, company, url),
            "title": title,
            "company": company,
            "location": location or "Remote",
            "url": url,
            "description": description,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": salary_currency,
            "tags": tags or [],
            "source": self.name,
            "source_display": self.display_name,
            "logo_color": self.logo_color,
            "posted_at": posted_at,
        }
