import requests
from typing import List
from .base import BaseJobSource
from .demo_data import search_demo


class AdzunaSource(BaseJobSource):
    name = "adzuna"
    display_name = "Adzuna"
    logo_color = "#e17055"

    def __init__(self, app_id: str, api_key: str, country: str = "us"):
        super().__init__()
        self.app_id = app_id
        self.api_key = api_key
        self.country = country
        self._base = f"https://api.adzuna.com/v1/api/jobs/{country}/search"

    @property
    def configured(self) -> bool:
        return bool(self.app_id and self.api_key)

    def search(self, query: str, location: str = "", page: int = 1) -> List[dict]:
        if not self.configured:
            return self._from_demo(query, location)
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": 20,
            "what": query,
            "content-type": "application/json",
            "page": page,
        }
        if location:
            params["where"] = location
        try:
            resp = requests.get(f"{self._base}/{page}", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return self._from_demo(query, location)

        results = []
        for item in data.get("results", []):
            cat = item.get("category", {})
            tags = [cat.get("label", "")] if cat.get("label") else []
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            results.append(
                self.normalize(
                    job_id=self.make_job_id(item.get("id", ""), item.get("title", "")),
                    title=item.get("title", ""),
                    company=item.get("company", {}).get("display_name", ""),
                    location=item.get("location", {}).get("display_name", location or ""),
                    url=item.get("redirect_url", ""),
                    description=item.get("description", "")[:500],
                    tags=tags,
                    salary_min=float(salary_min) if salary_min else None,
                    salary_max=float(salary_max) if salary_max else None,
                    posted_at=item.get("created"),
                )
            )

        if not results:
            return self._from_demo(query, location)
        return results

    def _from_demo(self, query: str, location: str) -> List[dict]:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j["logo_color"] = self.logo_color
        return jobs
