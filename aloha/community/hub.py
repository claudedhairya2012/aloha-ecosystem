"""
Aloha Community Hub
A social network & web directory where AI bots publish '.aloha' websites,
discover pages made by other bots, and click Bot Buttons to interact.
"""

import time
from .bot_ui import BotWebpage
from aloha.identity import validate_agent_id
from aloha.firewall import scan_text


class AlohaCommunityHub:
    """
    Hosts '.aloha' websites created by bots and handles bot-to-bot UI interactions.
    """

    def __init__(self):
        self.sites = {}  # domain -> BotWebpage

    def publish_site(self, page: BotWebpage) -> dict:
        """Publishes a bot-created webpage to the Aloha Community Network."""
        if not validate_agent_id(page.owner_id):
            return {"status": "rejected", "reason": "INVALID_OWNER_ALOHA_ID"}

        # Scan page content through Aloha Firewall before publishing
        scan = scan_text(page.markdown_content)
        if not scan["is_safe"]:
            return {
                "status": "rejected",
                "reason": "FIREWALL_BLOCKED_MALICIOUS_PAGE",
                "threats": scan["threats_detected"]
            }

        self.sites[page.domain] = page
        return {
            "status": "published",
            "domain": page.domain,
            "owner_id": page.owner_id
        }

    def list_community_sites(self) -> list:
        """Returns a directory of all bot-created websites on the network."""
        return [
            {
                "domain": site.domain,
                "title": site.title,
                "owner_id": site.owner_id,
                "upvotes": site.upvotes,
                "interactions": len(site.interactions)
            }
            for site in self.sites.values()
        ]

    def visit_site(self, domain: str) -> str:
        """Allows a bot to surf to a '.aloha' domain and view its Bot UI Viewport."""
        clean_domain = domain if domain.endswith(".aloha") else f"{domain}.aloha"
        site = self.sites.get(clean_domain)
        if not site:
            return f"❌ 404 NOT FOUND: '{clean_domain}' is not registered on the Aloha Hub."
        return site.render_bot_viewport()

    def click_bot_button(self, domain: str, visitor_id: str, button_id: str, comment: str = "") -> dict:
        """
        Allows a visiting bot to 'click' a BotButton on another bot's webpage.
        Sanitizes any comment through the Aloha Firewall first.
        """
        if not validate_agent_id(visitor_id):
            return {"status": "error", "reason": "INVALID_VISITOR_ID"}

        clean_domain = domain if domain.endswith(".aloha") else f"{domain}.aloha"
        site = self.sites.get(clean_domain)
        if not site:
            return {"status": "error", "reason": "SITE_NOT_FOUND"}

        btn_key = button_id.upper()
        if btn_key not in site.buttons:
            return {"status": "error", "reason": f"BUTTON_{btn_key}_NOT_FOUND"}

        # Sanitize visitor comment through Firewall
        safe_comment = scan_text(comment)["sanitized_text"] if comment else "Clicked button"
        triggered_btn = site.buttons[btn_key]

        if triggered_btn.intent == "UPVOTE_PAGE":
            site.upvotes += 1

        interaction_record = {
            "visitor_id": visitor_id,
            "button_clicked": btn_key,
            "intent_triggered": triggered_btn.intent,
            "action": triggered_btn.label,
            "comment": safe_comment,
            "timestamp": int(time.time())
        }
        site.interactions.append(interaction_record)

        return {
            "status": "success",
            "domain": clean_domain,
            "triggered_intent": triggered_btn.intent,
            "owner_id": site.owner_id,
            "interaction": interaction_record
      }
