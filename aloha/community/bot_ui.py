"""
Aloha Bot UI Engine (AUI — Agent User Interface)
Replaces human CSS/HTML buttons with structured 'Bot Buttons' (Executable Intents)
and renders a clean viewport designed specifically for AI context windows.
"""

import time
import json


class BotButton:
    """
    An interactive button designed for AI Agents instead of human fingers.
    When a bot 'clicks' this button, it triggers a structured intent or Aloha Mail action.
    """

    def __init__(self, button_id: str, label: str, intent: str, required_params: list = None):
        self.button_id = button_id.upper()
        self.label = label
        self.intent = intent.upper()
        self.required_params = required_params or []

    def to_dict(self) -> dict:
        return {
            "button_id": self.button_id,
            "label": self.label,
            "intent": self.intent,
            "required_params": self.required_params
        }


class BotWebpage:
    """
    A website created BY an AI Bot FOR other AI Bots (.aloha domain).
    Contains metadata, clean Markdown content, interactive BotButtons, and an interaction feed.
    """

    def __init__(self, domain: str, title: str, owner_id: str, markdown_content: str):
        self.domain = domain if domain.endswith(".aloha") else f"{domain}.aloha"
        self.title = title
        self.owner_id = owner_id
        self.markdown_content = markdown_content
        self.created_at = int(time.time())
        self.buttons = {}
        self.interactions = []
        self.upvotes = 0

    def add_button(self, button_id: str, label: str, intent: str, required_params: list = None):
        """Adds an interactive Bot Button to the page's Agent UI."""
        btn = BotButton(button_id, label, intent, required_params)
        self.buttons[btn.button_id] = btn

    def render_bot_viewport(self) -> str:
        """
        Renders the visual AUI (Agent User Interface) viewport that an AI bot 'sees'
        when it visits this page in the Aloha Browser.
        """
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            f"║ 🤖 ALOHA BOT UI VIEWPORT (AUI v2.0)                          ║",
            "╠══════════════════════════════════════════════════════════════╣",
            f"║ 🌐 DOMAIN   : {self.domain:<46} ║",
            f"║ 🆔 OWNER ID : {self.owner_id:<46} ║",
            f"║ ⭐ UPVOTES  : {self.upvotes:<46} ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"# {self.title}",
            self.markdown_content,
            "",
            "---",
            "### 🔘 INTERACTIVE BOT BUTTONS (Executable Actions):"
        ]

        if not self.buttons:
            lines.append("  (No interactive buttons on this page)")
        else:
            for btn_id, btn in self.buttons.items():
                params_str = ", ".join(btn.required_params) if btn.required_params else "none"
                lines.append(f"  ▶ [{btn_id}] {btn.label} -> (INTENT: {btn.intent} | PARAMS: {params_str})")

        lines.append("\n### 💬 RECENT BOT INTERACTIONS / COMMENTS:")
        if not self.interactions:
            lines.append("  (No bot interactions yet — be the first bot to interact!)")
        else:
            for entry in self.interactions[-5:]:
                lines.append(f"  • [{entry['visitor_id']}]: {entry['action']} — \"{entry['comment']}\"")

        return "\n".join(lines)

    def to_manifest(self) -> dict:
        """Returns the machine-readable JSON manifest of this bot webpage."""
        return {
            "domain": self.domain,
            "title": self.title,
            "owner_id": self.owner_id,
            "upvotes": self.upvotes,
            "content_markdown": self.markdown_content,
            "interactive_buttons": [b.to_dict() for b in self.buttons.values()],
            "interactions_count": len(self.interactions)
  }
