"""
Scrapes the latest HackerNews "Ask HN: Who is Hiring?" thread.
Uses only the official HN Firebase API (no ToS violation).
"""
import re
import requests
from datetime import datetime
from .base import BaseJobSource


HN_API = "https://hacker-news.firebaseio.com/v0"
ALGOLIA_API = "https://hn.algolia.com/api/v1/search"


class HackerNewsSource(BaseJobSource):
    name = "hackernews"
    display_name = "HN: Who's Hiring"
    logo_color = "#fd7272"

    def _get_hiring_post_id(self) -> int | None:
        """Find the most recent 'Ask HN: Who is Hiring?' post via Algolia HN search."""
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

    def _parse_comment(self, text: str, query: str) -> dict | None:
        if not text or query.lower() not in text.lower():
            return None
        # Try to extract company | role | location pattern
        lines = [l.strip() for l in text.replace("<p>", "\n").split("\n") if l.strip()]
        first_line = re.sub(r"<[^>]+>", "", lines[0]) if lines else ""
        parts = [p.strip() for p in first_line.split("|")]
        company = parts[0] if parts else "Unknown"
        role = parts[1] if len(parts) > 1 else query
        location = parts[2] if len(parts) > 2 else "Remote"
        clean_desc = re.sub(r"<[^>]+>", " ", text)[:600]
        return {
            "company": company,
            "title": role,
            "location": location,
            "description": clean_desc,
        }

    def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        post_id = self._get_hiring_post_id()
        if not post_id:
            return []
        try:
            resp = requests.get(f"{HN_API}/item/{post_id}.json", timeout=10)
            resp.raise_for_status()
            post = resp.json()
        except Exception:
            return []

        kids = (post.get("kids") or [])[:120]  # first 120 comments
        results = []
        for kid_id in kids:
            try:
                r = requests.get(f"{HN_API}/item/{kid_id}.json", timeout=5)
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
                            url=f"https://news.ycombinator.com/item?id={kid_id}",
                            description=parsed["description"],
                            posted_at=posted_at,
                        )
                    )
            except Exception:
                continue
            if len(results) >= 15:
                break
        return results
