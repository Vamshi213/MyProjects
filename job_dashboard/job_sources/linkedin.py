import requests
import xml.etree.ElementTree as ET
from .base import BaseJobSource
from .demo_data import search_demo


class LinkedInSource(BaseJobSource):
    name = "linkedin"
    display_name = "LinkedIn"
    logo_color = "#0077b5"
    _BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            params = {
                "keywords": query,
                "location": location or "Remote",
                "start": (page - 1) * 25,
                "count": 25,
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)",
                "Accept": "application/json",
            }
            resp = requests.get(self._BASE, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            # LinkedIn guest API returns JSON list of job cards
            jobs = []
            for item in resp.json():
                jobs.append(self.normalize(
                    job_id=self.make_job_id(str(item.get("id", "")), item.get("title", "")),
                    title=item.get("title", ""),
                    company=item.get("companyName", ""),
                    location=item.get("formattedLocation", location or "Remote"),
                    url=item.get("applyUrl") or f"https://www.linkedin.com/jobs/view/{item.get('id', '')}",
                    description=item.get("description", {}).get("text", "")[:500] if isinstance(item.get("description"), dict) else "",
                    tags=[],
                    posted_at=None,
                ))
            if jobs:
                return jobs
        except Exception:
            pass
        return self._from_demo(query, location)

    def _from_demo(self, query: str, location: str) -> list:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j.setdefault("source_display", self.display_name)
            j.setdefault("logo_color", self.logo_color)
        return jobs
