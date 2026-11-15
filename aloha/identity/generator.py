"""
Aloha Agent ID Generator
Generates cryptographically secure 15-Digit Agent IDs using Luhn checksums.
Format: XXX - XXXXXXXX - XXX - X
"""

import secrets
from .registry import AGENT_CLASSES, CAPABILITY_PERMISSIONS


def calculate_luhn_checksum(payload: str) -> int:
    """
    Luhn Modulus-10 checksum algorithm (same standard used by credit cards).
    Prevents forgery and typo errors.
    """
    digits = [int(d) for d in payload if d.isdigit()]
    checksum = 0
    for index, digit in enumerate(digits[::-1]):
        if index % 2 == 0:
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit
    return (10 - (checksum % 10)) % 10


def generate_agent_id(agent_class: str = "101", capability: str = "001") -> str:
    """
    Generates a 15-Digit Aloha Agent ID.
    Example: 101-48291054-002-7
    """
    prefix = str(agent_class).zfill(3)
    if prefix not in AGENT_CLASSES:
        prefix = "101"

    cap_code = str(capability).zfill(3)
    if cap_code not in CAPABILITY_PERMISSIONS:
        cap_code = "001"

    # Cryptographically secure 8-digit identity
    identity_hash = str(secrets.randbelow(90000000) + 10000000)

    payload = prefix + identity_hash + cap_code
    checksum = calculate_luhn_checksum(payload)

    return f"{prefix}-{identity_hash}-{cap_code}-{checksum}"


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from aloha.identity.generator import generate_agent_id

    print("🌺 Generated Agent ID:", generate_agent_id("101", "001"))
