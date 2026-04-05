import requests
from typing import List
from .base import BaseJobSource
from .demo_data import search_demo


class RemoteOKSource(BaseJobSource):
    name = "remoteok"
    display_name = "RemoteOK"
    logo_color = "#00c896"
    _BASE = "https://remoteok.com/api"

    def search(self, query: str, location: str = "", page: int = 1) -> List[dict]:
        try:
            headers = {"User-Agent": "JobDashboard/1.0 (job-hunt-tool)"}
            resp = requests.get(self._BASE, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            # Network/proxy unavailable – serve from curated dataset
            return self._from_demo(query, location)

        query_lower = query.lower()
        results = []
        for item in data:
            if not isinstance(item, dict) or "position" not in item:
                continue
            title = item.get("position", "")
            company = item.get("company", "")
            tags = item.get("tags", []) or []
            desc = item.get("description", "")
            searchable = f"{title} {company} {' '.join(tags)} {desc}".lower()
            if query_lower and query_lower not in searchable:
                continue

            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("id", ""), title, company),
                    title=title,
                    company=company,
                    location="Remote",
                    url=item.get("url", ""),
                    description=desc[:500] if desc else "",
                    tags=tags[:8],
                    salary_min=item.get("salary_min"),
                    salary_max=item.get("salary_max"),
                    posted_at=item.get("date"),
                )
            )
            if len(results) >= 20:
                break

        # Fall back if live API returned nothing for this query
        if not results:
            return self._from_demo(query, location)
        return results

    def _from_demo(self, query: str, location: str) -> List[dict]:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j["logo_color"] = self.logo_color
        return jobs
