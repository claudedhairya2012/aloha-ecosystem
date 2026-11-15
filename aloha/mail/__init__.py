"""
🌺 Aloha Ecosystem — Mail Protocol Module
Direct, cryptographically signed Agent-to-Agent messaging using 15-Digit IDs.
"""

from .envelope import create_envelope, serialize_for_signing
from .sender import compose_signed_mail
from .receiver import verify_incoming_mail, AgentInbox
from .router import LocalMailRouter

__all__ = [
    "create_envelope",
    "serialize_for_signing",
    "compose_signed_mail",
    "verify_incoming_mail",
    "AgentInbox",
    "LocalMailRouter"
]

__version__ = "2.0.0"
