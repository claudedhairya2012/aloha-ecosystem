"""
Aloha Open Search Engine Indexer
Allows any bot or website to join the Aloha Search Engine Index
and enables unlimited keyword/topic search across indexed raw data.
"""

import time
from .manifest import validate_aloha_manifest
from aloha.firewall import scan_text
from aloha.browser import scrape_url


class AlohaSearchIndex:
    """
    AI-Native Search Engine Index.
    Stores clean Markdown/JSON nodes submitted by bots or scraped from the web.
    """

    def __init__(self):
        self.nodes = {}  # domain_or_url -> indexed node dict

    def join_network_via_manifest(self, manifest: dict, initial_markdown: str = "") -> dict:
        """
        Allows a website or bot to officially join the Aloha Search Engine
        by submitting its 'aloha.json' manifest and initial raw content.
        """
        check = validate_aloha_manifest(manifest)
        if not check["is_valid"]:
            return {"status": "rejected", "reason": check["reason"]}

        # Scan content with Aloha Firewall before indexing
        fw = scan_text(initial_markdown)
        if not fw["is_safe"]:
            return {
                "status": "rejected",
                "reason": "FIREWALL_BLOCKED_CONTENT",
                "threats": fw["threats_detected"]
            }

        domain = manifest["domain"]
        self.nodes[domain] = {
            "domain": domain,
            "owner_id": manifest["contact_agent_id"],
            "keywords": [k.lower() for k in manifest.get("search_keywords", [])],
            "markdown": fw["sanitized_text"],
            "verified_aloha_json": True,
            "indexed_at_utc": int(time.time())
        }
        return {"status": "indexed", "domain": domain, "total_indexed": len(self.nodes)}

    def index_live_url(self, url: str, owner_id: str, keywords: list = None) -> dict:
        """
        Scrapes any live web URL via Module 2 (Raw Browser Engine)
        and adds its clean Markdown directly into the Aloha Search Engine!
        """
        scraped = scrape_url(url)
        if scraped.get("status") != "success":
            return {"status": "error", "reason": scraped.get("error_message", "Scrape failed")}

        title = scraped.get("metadata", {}).get("title") or url
        content = scraped.get("content", "")
        fw = scan_text(content)

        self.nodes[url] = {
            "domain": url,
            "title": title,
            "owner_id": owner_id,
            "keywords": [k.lower() for k in (keywords or title.split())],
            "markdown": fw["sanitized_text"],
            "metrics": scraped.get("metrics", {}),
            "verified_aloha_json": False,
            "indexed_at_utc": int(time.time())
        }
        return {"status": "indexed", "url": url, "metrics": scraped.get("metrics", {})}

    def search(self, query: str) -> list:
        """
        Searches all indexed Aloha nodes by keyword, domain, or content match.
        """
        q = query.lower().strip()
        if not q:
            return list(self.nodes.values())

        results = []
        for domain, node in self.nodes.items():
            haystack = f"{domain} {node.get('title', '')} {' '.join(node.get('keywords', []))} {node.get('markdown', '')}".lower()
            if q in haystack:
                results.append(node)
        return results
