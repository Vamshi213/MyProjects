import requests
from .base import BaseJobSource


class ArbeitnowSource(BaseJobSource):
    name = "arbeitnow"
    display_name = "Arbeitnow"
    logo_color = "#0984e3"
    _BASE = "https://www.arbeitnow.com/api/job-board-api"

    def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        try:
            resp = requests.get(self._BASE, params={"page": page}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        query_lower = query.lower()
        results = []
        for item in data.get("data", []):
            title = item.get("title", "")
            company = item.get("company_name", "")
            tags = item.get("tags", []) or []
            desc = item.get("description", "")
            loc = item.get("location", "Remote")
            searchable = f"{title} {company} {' '.join(tags)} {desc}".lower()
            if query_lower and query_lower not in searchable:
                continue
            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("slug", ""), title, company),
                    title=title,
                    company=company,
                    location=loc,
                    url=item.get("url", ""),
                    description=desc[:500] if desc else "",
                    tags=tags[:6],
                    posted_at=item.get("created_at"),
                )
            )
            if len(results) >= 15:
                break
        return results
