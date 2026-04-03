import requests
from .base import BaseJobSource
from .demo_data import search_demo


class DiceSource(BaseJobSource):
    name = "dice"
    display_name = "Dice"
    logo_color = "#ee3524"
    # Dice public search API (no auth required for basic search)
    _BASE = "https://job-search-api.simitgroup.com/v1/JobSearch"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            params = {
                "q": query,
                "countryCode2": "US",
                "pageSize": 20,
                "facets": "employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote",
                "fields": "id,jobId,title,companyDisplay,employmentType,postedDate,salary,remote,locations,descriptionFragment,applyDataRequired,link,employer",
                "page": page,
                "sort": "-score",
                "language": "en",
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)",
                "x-api-key": "1YAt0R9wBg4WfsF9VB2778F4QbIoEwAA",  # public demo key
            }
            resp = requests.get(self._BASE, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("data", []):
                locs = item.get("locations", [])
                loc_str = locs[0].get("displayName", "Remote") if locs else "Remote"
                salary = item.get("salary", {}) or {}
                results.append(self.normalize(
                    job_id=self.make_job_id(item.get("jobId", ""), item.get("title", "")),
                    title=item.get("title", ""),
                    company=item.get("companyDisplay") or item.get("employer", {}).get("name", ""),
                    location=loc_str,
                    url=item.get("link", f"https://www.dice.com/jobs/detail/{item.get('jobId', '')}"),
                    description=item.get("descriptionFragment", "")[:500],
                    tags=[item.get("employmentType", "")] if item.get("employmentType") else [],
                    salary_min=salary.get("minimum"),
                    salary_max=salary.get("maximum"),
                    posted_at=item.get("postedDate"),
                ))
            if results:
                return results
        except Exception:
            pass
        return self._from_demo(query, location)

    def _from_demo(self, query: str, location: str) -> list:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j.setdefault("source_display", self.display_name)
            j.setdefault("logo_color", self.logo_color)
        return jobs
