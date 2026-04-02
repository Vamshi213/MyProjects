import requests
from .base import BaseJobSource


class RemoteOKSource(BaseJobSource):
    name = "remoteok"
    display_name = "RemoteOK"
    logo_color = "#00c896"
    _BASE = "https://remoteok.com/api"

    def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        try:
            headers = {"User-Agent": "JobDashboard/1.0 (job-hunt-tool)"}
            resp = requests.get(self._BASE, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

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

        return results
