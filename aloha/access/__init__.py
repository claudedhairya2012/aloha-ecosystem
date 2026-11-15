"""
🌺 Aloha Ecosystem — Access Standard & Search Index Module (Module 6)
Implements the 'aloha.json' web standard for Cloudflare/Captcha bypass
and provides an open, extensible Search Engine Index for AI Agents.
"""

from .manifest import generate_aloha_manifest, validate_aloha_manifest
from .indexer import AlohaSearchIndex

__all__ = [
    "generate_aloha_manifest",
    "validate_aloha_manifest",
    "AlohaSearchIndex"
]

__version__ = "2.0.0"
