import requests
import re
from .base import BaseJobSource
from .demo_data import search_demo


class JobicySource(BaseJobSource):
    name = "jobicy"
    display_name = "Jobicy"
    logo_color = "#10b981"
    _BASE = "https://jobicy.com/api/v2/remote-jobs"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            resp = requests.get(
                self._BASE,
                params={"tag": query, "count": 20},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return self._from_demo(query, location)

        results = []
        for item in data.get("jobs", []):
            tags = item.get("jobIndustry", []) or []
            if isinstance(tags, str):
                tags = [tags]
            tags += item.get("jobType", []) or []
            desc = re.sub(r"<[^>]+>", " ", item.get("jobDescription", ""))[:500]
            sal = item.get("annualSalaryMin")
            sal_max = item.get("annualSalaryMax")
            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("id", ""), item.get("jobTitle", "")),
                    title=item.get("jobTitle", ""),
                    company=item.get("companyName", ""),
                    location=item.get("jobGeo", "Remote"),
                    url=item.get("url", ""),
                    description=desc,
                    tags=tags[:6],
                    salary_min=float(sal) if sal else None,
                    salary_max=float(sal_max) if sal_max else None,
                    salary_currency=item.get("salaryCurrency", "USD"),
                    posted_at=item.get("pubDate"),
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
