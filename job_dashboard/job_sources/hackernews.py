"""
Scrapes the latest HackerNews "Ask HN: Who is Hiring?" thread.
Uses only the official HN Firebase API (no ToS violation).
Falls back to curated demo dataset when network is unavailable.
"""
import re
import requests
from datetime import datetime
from typing import Optional, List

from .base import BaseJobSource
from .demo_data import search_demo


HN_API = "https://hacker-news.firebaseio.com/v0"
ALGOLIA_API = "https://hn.algolia.com/api/v1/search"


class HackerNewsSource(BaseJobSource):
    name = "hackernews"
    display_name = "HN: Who's Hiring"
    logo_color = "#fd7272"

    def _get_hiring_post_id(self) -> Optional[int]:
        try:
            params = {
                "query": "Ask HN: Who is hiring?",
                "tags": "story,ask_hn",
                "hitsPerPage": 5,
            }
            resp = requests.get(ALGOLIA_API, params=params, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            for hit in hits:
                if re.search(r"ask hn: who is hiring", hit.get("title", ""), re.I):
                    return hit.get("objectID")
        except Exception:
            pass
        return None

    def _parse_comment(self, text: str, query: str) -> Optional[dict]:
        if not text or query.lower() not in text.lower():
            return None
        lines = [l.strip() for l in text.replace("<p>", "\n").split("\n") if l.strip()]
        first_line = re.sub(r"<[^>]+>", "", lines[0]) if lines else ""
        parts = [p.strip() for p in first_line.split("|")]
        company = parts[0] if parts else "Unknown"
        role = parts[1] if len(parts) > 1 else query
        location = parts[2] if len(parts) > 2 else "Remote"
        clean_desc = re.sub(r"<[^>]+>", " ", text)[:600]
        return {"company": company, "title": role, "location": location, "description": clean_desc}

    def search(self, query: str, location: str = "", page: int = 1) -> List[dict]:
        post_id = self._get_hiring_post_id()
        if not post_id:
            return self._from_demo(query, location)
        try:
            resp = requests.get("{}/item/{}.json".format(HN_API, post_id), timeout=10)
            resp.raise_for_status()
            post = resp.json()
        except Exception:
            return self._from_demo(query, location)

        kids = (post.get("kids") or [])[:120]
        results = []
        for kid_id in kids:
            try:
                r = requests.get("{}/item/{}.json".format(HN_API, kid_id), timeout=5)
                item = r.json()
                parsed = self._parse_comment(item.get("text", ""), query)
                if parsed:
                    ts = item.get("time")
                    posted_at = datetime.utcfromtimestamp(ts).isoformat() if ts else None
                    results.append(
                        self.normalize(
                            job_id=self.make_job_id(kid_id, parsed["company"]),
                            title=parsed["title"],
                            company=parsed["company"],
                            location=parsed["location"],
                            url="https://news.ycombinator.com/item?id={}".format(kid_id),
                            description=parsed["description"],
                            posted_at=posted_at,
                        )
                    )
            except Exception:
                continue
            if len(results) >= 15:
                break

        if not results:
            return self._from_demo(query, location)
        return results

    def _from_demo(self, query: str, location: str) -> List[dict]:
        jobs = [j for j in search_demo(query, location) if j.get("source") == self.name]
        for j in jobs:
            j["logo_color"] = self.logo_color
        return jobs
