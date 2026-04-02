import requests
from .base import BaseJobSource


class TheMuseSource(BaseJobSource):
    name = "themuse"
    display_name = "The Muse"
    logo_color = "#6c5ce7"
    _BASE = "https://www.themuse.com/api/public/jobs"

    def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        params = {"page": page, "descending": "true"}
        if query:
            params["category"] = query
        try:
            resp = requests.get(self._BASE, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        query_lower = query.lower()
        results = []
        for item in data.get("results", []):
            title = item.get("name", "")
            company = item.get("company", {}).get("name", "")
            locations = item.get("locations", [])
            loc = ", ".join(l.get("name", "") for l in locations) if locations else "Remote"
            levels = item.get("levels", [])
            tags = [lv.get("name", "") for lv in levels if lv.get("name")]
            refs = item.get("refs", {})
            url = refs.get("landing_page", "")
            desc = item.get("contents", "")
            # basic filter
            searchable = f"{title} {company} {' '.join(tags)}".lower()
            if query_lower and query_lower not in searchable:
                continue
            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("id", ""), title, company),
                    title=title,
                    company=company,
                    location=loc,
                    url=url,
                    description=desc[:500] if desc else "",
                    tags=tags,
                    posted_at=item.get("publication_date"),
                )
            )
        return results
