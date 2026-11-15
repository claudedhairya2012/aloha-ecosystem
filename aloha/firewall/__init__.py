"""
🌺 Aloha Ecosystem — Cognitive Firewall Module
Protects AI Agents from Prompt Injection attacks, system role hijacks, and rogue bots.
"""

from .patterns import ROLE_MARKERS, INJECTION_PATTERNS
from .sanitizer import (
    strip_role_markers,
    scan_text,
    sanitize_payload,
    inspect_mail_packet
)
from .reputation import ReputationManager

__all__ = [
    "ROLE_MARKERS",
    "INJECTION_PATTERNS",
    "strip_role_markers",
    "scan_text",
    "sanitize_payload",
    "inspect_mail_packet",
    "ReputationManager"
]

__version__ = "2.0.0"
