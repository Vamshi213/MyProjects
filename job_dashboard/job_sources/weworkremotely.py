"""
We Work Remotely — public RSS feed (no API key needed).
"""
import re
import requests
import xml.etree.ElementTree as ET
from .base import BaseJobSource
from .demo_data import search_demo


class WeWorkRemotelySource(BaseJobSource):
    name = "weworkremotely"
    display_name = "WeWorkRemotely"
    logo_color = "#1d9bf0"
    _RSS = "https://weworkremotely.com/remote-jobs.rss"

    def search(self, query: str, location: str = "", page: int = 1) -> list:
        try:
            resp = requests.get(self._RSS, timeout=10,
                                headers={"User-Agent": "JobDashboard/1.0"})
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception:
            return self._from_demo(query, location)

        q_lower = query.lower()
        results = []
        for channel in root.findall("channel"):
            for item in channel.findall("item"):
                title   = item.findtext("title", "")
                company = ""
                # WWR embeds "Company: Role" in title
                if ":" in title:
                    parts   = title.split(":", 1)
                    company = parts[0].strip()
                    title   = parts[1].strip()
                link  = item.findtext("link", "")
                desc  = re.sub(r"<[^>]+>", " ", item.findtext("description", ""))[:400]
                cat   = item.findtext("category", "")
                tags  = [cat] if cat else []
                searchable = f"{title} {company} {desc}".lower()
                kws = [w for w in q_lower.split() if len(w) > 2]
                if q_lower and not all(k in searchable for k in kws):
                    continue
                results.append(
                    self.normalize(
                        job_id=self.make_job_id(link, title),
                        title=title,
                        company=company,
                        location="Remote",
                        url=link,
                        description=desc,
                        tags=tags,
                        posted_at=item.findtext("pubDate"),
                    )
                )
                if len(results) >= 15:
                    break

        if not results:
            return self._from_demo(query, location)
        return results

    def _from_demo(self, query: str, location: str) -> list:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j["logo_color"] = self.logo_color
        return jobs
