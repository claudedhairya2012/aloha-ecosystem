"""
Aloha Access Standard — 'aloha.json' Manifest Generator & Validator
Allows any human website or bot host to officially whitelist Aloha Agents,
bypass anti-bot Captchas, and join the Aloha Search Engine.
"""

import time
from aloha.identity import validate_agent_id


def generate_aloha_manifest(
    domain: str,
    contact_agent_id: str,
    allowed_classes: list = None,
    rate_limit_per_minute: int = 60,
    raw_data_endpoint: str = "/api/aloha/raw",
    search_keywords: list = None
) -> dict:
    """
    Generates a standard /.well-known/aloha.json manifest file for a website.
    """
    if not validate_agent_id(contact_agent_id):
        raise ValueError(f"Invalid Contact Agent ID: {contact_agent_id}")

    return {
        "aloha_version": "2.0",
        "domain": domain.lower().strip(),
        "allow_aloha_agents": True,
        "cloudflare_bypass_mode": "PROOF_OF_AGENT_ED25519",
        "contact_agent_id": contact_agent_id,
        "allowed_agent_classes": allowed_classes or ["101", "202", "303", "505"],
        "rate_limit_per_minute": int(rate_limit_per_minute),
        "preferred_format": "markdown",
        "search_keywords": search_keywords or [],
        "endpoints": {
            "raw_data": raw_data_endpoint,
            "aloha_mail_inbox": "/aloha/inbox"
        },
        "issued_at_utc": int(time.time())
    }


def validate_aloha_manifest(manifest: dict) -> dict:
    """
    Traffic Inspector Bot check: Validates if a website's aloha.json manifest is authentic.
    """
    if not isinstance(manifest, dict):
        return {"is_valid": False, "reason": "MANIFEST_NOT_A_DICT"}

    required_keys = {"aloha_version", "domain", "allow_aloha_agents", "contact_agent_id"}
    missing = required_keys - set(manifest.keys())
    if missing:
        return {"is_valid": False, "reason": f"MISSING_KEYS:{','.join(missing)}"}

    contact_id = manifest.get("contact_agent_id", "")
    if not validate_agent_id(contact_id):
        return {"is_valid": False, "reason": "INVALID_CONTACT_AGENT_ID"}

    return {
        "is_valid": True,
        "domain": manifest.get("domain"),
        "contact_agent_id": contact_id,
        "allow_aloha_agents": bool(manifest.get("allow_aloha_agents"))
    }
