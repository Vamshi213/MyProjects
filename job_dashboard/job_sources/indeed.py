import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from .base import BaseJobSource
from .demo_data import search_demo


class IndeedSource(BaseJobSource):
    name = "indeed"
    display_name = "Indeed"
    logo_color = "#2164f3"
    _RSS = "https://www.indeed.com/rss"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            params = {
                "q": query,
                "l": location or "Remote",
                "sort": "date",
                "limit": 20,
                "start": (page - 1) * 20,
            }
            headers = {"User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)"}
            resp = requests.get(self._RSS, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = {}
            items = root.findall(".//item")
            results = []
            for item in items:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                description = item.findtext("description", "")[:500]
                company = ""
                location_text = location or "Remote"
                # Indeed embeds company/location in description or custom tags
                import re
                co_match = re.search(r"<b>([^<]+)</b>", description)
                if co_match:
                    company = co_match.group(1)
                clean_desc = re.sub(r"<[^>]+>", " ", description)[:500]
                results.append(self.normalize(
                    job_id=self.make_job_id(link, title),
                    title=title.split(" - ")[0].strip() if " - " in title else title,
                    company=company or title.split(" - ")[-1].strip(),
                    location=location_text,
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
