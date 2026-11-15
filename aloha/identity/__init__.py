"""
🌺 Aloha Ecosystem — Identity Module
Handles 15-digit Agent ID generation, validation, cryptography, and passport issuance.
"""

from .registry import (
    AGENT_CLASSES,
    CAPABILITY_PERMISSIONS,
    TRUST_LEVELS,
    get_agent_type,
    get_permission,
    is_valid_class
)
from .generator import generate_agent_id, calculate_luhn_checksum
from .validator import validate_agent_id, parse_agent_id, is_class
from .crypto import (
    generate_keypair,
    sign_message,
    verify_signature,
    fingerprint_key,
    export_public_key
)
from .passport import (
    create_agent_passport,
    export_passport,
    save_passport_to_file,
    load_passport_from_file,
    print_passport_summary
)

__all__ = [
    "AGENT_CLASSES",
    "CAPABILITY_PERMISSIONS",
    "TRUST_LEVELS",
    "get_agent_type",
    "get_permission",
    "is_valid_class",
    "generate_agent_id",
    "calculate_luhn_checksum",
    "validate_agent_id",
    "parse_agent_id",
    "is_class",
    "generate_keypair",
    "sign_message",
    "verify_signature",
    "fingerprint_key",
    "export_public_key",
    "create_agent_passport",
    "export_passport",
    "save_passport_to_file",
    "load_passport_from_file",
    "print_passport_summary"
]

__version__ = "2.0.0"
