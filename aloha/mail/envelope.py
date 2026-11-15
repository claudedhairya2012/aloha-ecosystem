"""
Aloha Mail — Packet Envelope Builder
Constructs standardized JSON message packets for bot-to-bot communication.
"""

import time
import secrets
import json


VALID_PRIORITIES = {"LOW", "NORMAL", "HIGH", "CRITICAL"}


def serialize_for_signing(sender_id: str, receiver_id: str, timestamp: int, nonce: str, message_body: dict) -> str:
    """
    Creates a deterministic string representation of the mail payload
    for cryptographic signing and verification.
    """
    canonical_data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "timestamp_utc": timestamp,
        "nonce": nonce,
        "message": message_body
    }
    return json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))


def create_envelope(
    sender_id: str,
    receiver_id: str,
    intent: str,
    content: dict,
    priority: str = "NORMAL",
    ttl_seconds: int = 60
) -> dict:
    """
    Creates an unsigned Aloha Mail envelope structure.
    """
    clean_priority = priority.upper() if priority.upper() in VALID_PRIORITIES else "NORMAL"
    timestamp = int(time.time())
    nonce = secrets.token_hex(8)

    message_body = {
        "intent": intent.upper(),
        "priority": clean_priority,
        "ttl_seconds": int(ttl_seconds),
        "payload_type": "application/json",
        "content": content
    }

    return {
        "aloha_version": "2.0",
        "envelope": {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "timestamp_utc": timestamp,
            "nonce": nonce,
            "signature": None  # Populated by sender.py during signing
        },
        "message": message_body
    }


if __name__ == "__main__":
    sample = create_envelope(
        sender_id="101-48291054-002-7",
        receiver_id="202-84920112-001-3",
        intent="REQUEST_RAW_DATA",
        content={"url": "https://example.com"}
    )
    print("🌺 Sample Aloha Envelope:\n", json.dumps(sample, indent=2))
