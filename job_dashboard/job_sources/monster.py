import requests
import xml.etree.ElementTree as ET
from .base import BaseJobSource
from .demo_data import search_demo


class MonsterSource(BaseJobSource):
    name = "monster"
    display_name = "Monster"
    logo_color = "#6e0b96"
    # Monster jobs RSS / public feed
    _RSS = "https://www.monster.com/jobs/search/rss"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            params = {
                "q": query,
                "where": location or "Remote",
                "pg": page,
            }
            headers = {"User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)"}
            resp = requests.get(self._RSS, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            results = []
            import re
            for item in items:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc_raw = item.findtext("description", "")
                clean_desc = re.sub(r"<[^>]+>", " ", desc_raw)[:500]
                # Monster puts "Company - Location" in title sometimes
                parts = title.rsplit(" - ", 1)
                job_title = parts[0].strip() if len(parts) > 1 else title
                company = item.findtext("{http://jobs.monster.com/}company", "")
                loc = item.findtext("{http://jobs.monster.com/}location", location or "Remote")
                results.append(self.normalize(
                    job_id=self.make_job_id(link, title),
                    title=job_title,
                    company=company or "Company",
                    location=loc,
                    url=link,
                    description=clean_desc,
                    tags=[],
                    posted_at=item.findtext("pubDate"),
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
