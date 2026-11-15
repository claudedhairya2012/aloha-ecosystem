"""
Aloha Agent ID Validator & Decoder
Verifies authenticity and decodes metadata of any 15-digit Aloha ID.
"""

from .generator import calculate_luhn_checksum
from .registry import AGENT_CLASSES, CAPABILITY_PERMISSIONS, get_agent_type, get_permission


def validate_agent_id(aloha_id: str) -> bool:
    """Validates if an Aloha ID passes Luhn checksum verification."""
    if not aloha_id or not isinstance(aloha_id, str):
        return False

    clean_id = aloha_id.replace("-", "").strip()

    if len(clean_id) != 15 or not clean_id.isdigit():
        return False

    payload = clean_id[:14]
    provided_checksum = int(clean_id[14])
    expected_checksum = calculate_luhn_checksum(payload)

    return provided_checksum == expected_checksum


def parse_agent_id(aloha_id: str) -> dict:
    """Decodes a 15-digit Aloha ID into full metadata profile."""
    is_valid = validate_agent_id(aloha_id)
    clean_id = aloha_id.replace("-", "").strip() if aloha_id else ""

    if not is_valid:
        return {
            "aloha_id": aloha_id,
            "is_authentic": False,
            "status": "INVALID_OR_TAMPERED_ID"
        }

    prefix = clean_id[:3]
    identity_hash = clean_id[3:11]
    cap_code = clean_id[11:14]
    checksum = clean_id[14]

    return {
        "aloha_id": aloha_id,
        "is_authentic": True,
        "status": "VERIFIED",
        "metadata": {
            "agent_class_code": prefix,
            "agent_type": get_agent_type(prefix),
            "identity_hash": identity_hash,
            "capability_code": cap_code,
            "permissions": get_permission(cap_code),
            "checksum_digit": checksum
        }
    }


def is_class(aloha_id: str, class_code: str) -> bool:
    """Checks if an ID belongs to a specific agent class."""
    if not validate_agent_id(aloha_id):
        return False
    clean_id = aloha_id.replace("-", "").strip()
    return clean_id[:3] == str(class_code).zfill(3)


if __name__ == "__main__":
    test_id = "101-48291054-002-7"
    print("🌺 Validation Test:", validate_agent_id(test_id))
