"""
Aloha Agent Passport Issuer
Creates, exports, and manages complete agent credentials.
"""

import time
import json
from .generator import generate_agent_id
from .validator import parse_agent_id
from .crypto import generate_keypair, fingerprint_key
from .registry import TRUST_LEVELS


def create_agent_passport(
    agent_name: str,
    agent_class: str = "101",
    capability: str = "001",
    operator: str = "anonymous"
) -> dict:
    """Registers a new bot and issues a full Aloha Agent Passport."""
    new_id = generate_agent_id(agent_class, capability)
    decoded = parse_agent_id(new_id)
    keys = generate_keypair()
    fp = fingerprint_key(keys["public_key"])

    passport = {
        "network": "Aloha Agent Network",
        "protocol_version": "2.0.0",
        "registered_name": agent_name,
        "operator": operator,
        "aloha_id": new_id,
        "issued_at_utc": int(time.time()),
        "trust_level": 0,
        "trust_label": TRUST_LEVELS.get(0, "UNVERIFIED"),
        "reputation_score": 100,
        "profile": decoded["metadata"],
        "credentials": {
            "public_key": keys["public_key"],
            "private_key": keys["private_key"],
            "key_fingerprint": fp,
            "algorithm": keys["algorithm"]
        }
    }
    return passport


def export_passport(passport: dict, include_private_key: bool = False) -> dict:
    """Exports a public-safe copy of a passport (strips private key by default)."""
    public_copy = json.loads(json.dumps(passport))
    if not include_private_key and "credentials" in public_copy:
        public_copy["credentials"].pop("private_key", None)
    return public_copy


def save_passport_to_file(passport: dict, filepath: str) -> bool:
    """Saves passport to a JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(passport, f, indent=2)
        return True
    except Exception:
        return False


def load_passport_from_file(filepath: str) -> dict:
    """Loads passport from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def print_passport_summary(passport: dict) -> None:
    """Prints a nicely formatted summary of an Agent Passport."""
    profile = passport.get("profile", {})
    creds = passport.get("credentials", {})
    
    print("=" * 55)
    print(" 🌺 ALOHA AGENT PASSPORT")
    print("=" * 55)
    print(f" Name        : {passport.get('registered_name', 'Unknown')}")
    print(f" Aloha ID    : {passport.get('aloha_id', 'N/A')}")
    print(f" Agent Class : {profile.get('agent_type', 'N/A')}")
    print(f" Permissions : {profile.get('permissions', 'N/A')}")
    print(f" Trust Level : {passport.get('trust_label', 'UNVERIFIED')} ({passport.get('trust_level', 0)})")
    print(f" Reputation  : {passport.get('reputation_score', 100)}/100")
    print(f" Key Finger  : {creds.get('key_fingerprint', 'N/A')}")
    print("=" * 55)


if __name__ == "__main__":
    pass_data = create_agent_passport("DemoBot", "101", "001")
    print_passport_summary(pass_data)
