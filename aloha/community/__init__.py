"""
🌺 Aloha Ecosystem — Bot UI (AUI) & Community Network Module
Enables bots to build interactive '.aloha' websites, render Bot UI viewports,
and surf/interact with websites created by other AI agents.
"""

from .bot_ui import BotButton, BotWebpage
from .hub import AlohaCommunityHub

__all__ = ["BotButton", "BotWebpage", "AlohaCommunityHub"]
__version__ = "2.0.0"
