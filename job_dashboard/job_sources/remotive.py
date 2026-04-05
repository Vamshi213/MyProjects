import requests
from .base import BaseJobSource
from .demo_data import search_demo


class RemotiveSource(BaseJobSource):
    name = "remotive"
    display_name = "Remotive"
    logo_color = "#4a90e2"
    _BASE = "https://remotive.com/api/remote-jobs"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            resp = requests.get(
                self._BASE,
                params={"search": query, "limit": 20},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return self._from_demo(query, location)

        results = []
        for item in data.get("jobs", []):
            tags = item.get("tags", []) or []
            desc = item.get("description", "")
            # strip html tags from description
            import re
            clean_desc = re.sub(r"<[^>]+>", " ", desc)[:500]
            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("id", ""), item.get("title", "")),
                    title=item.get("title", ""),
                    company=item.get("company_name", ""),
                    location="Remote",
                    url=item.get("url", ""),
                    description=clean_desc,
                    tags=tags[:8],
                    salary_min=item.get("salary"),
                    posted_at=item.get("publication_date"),
                )
            )
        if not results:
            return self._from_demo(query, location)
        return results

    def _from_demo(self, query: str, location: str) -> list:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j["logo_color"] = self.logo_color
        return jobs
