"""
🌺 Aloha Ecosystem — Complete 6-Module Core Package
1. identity  : 15-Digit Agent IDs & Ed25519 Passports
2. browser   : 10x Faster Raw Data Browser Engine
3. mail      : Signed Agent-to-Agent Aloha Mail
4. firewall  : Cognitive Prompt Injection Firewall
5. community : Bot UI (AUI) & .aloha Community Hub
6. tunnel    : Local-to-Cloud Hybrid Bridge
7. access    : aloha.json Standard & Open Search Indexer
"""

from . import identity
from . import browser
from . import mail
from . import firewall
from . import community
from . import tunnel
from . import access

__all__ = [
    "identity",
    "browser",
    "mail",
    "firewall",
    "community",
    "tunnel",
    "access"
]

__version__ = "2.0.0"
__author__ = "Aloha Ecosystem Team"
