"""
Aloha Mail — Message Sender
Composes outgoing Aloha Mail packets and signs them with the agent's Ed25519 private key.
"""

from .envelope import create_envelope, serialize_for_signing
from aloha.identity import validate_agent_id, sign_message


def compose_signed_mail(
    sender_passport: dict,
    receiver_id: str,
    intent: str,
    content: dict,
    priority: str = "NORMAL",
    ttl_seconds: int = 60
) -> dict:
    """
    Composes and cryptographically signs an Aloha Mail packet ready for transmission.
    """
    sender_id = sender_passport.get("aloha_id", "")
    private_key = sender_passport.get("credentials", {}).get("private_key", "")

    # 1. Validate both 15-digit Agent IDs
    if not validate_agent_id(sender_id):
        raise ValueError(f"Invalid Sender Aloha ID: {sender_id}")
    if not validate_agent_id(receiver_id):
        raise ValueError(f"Invalid Receiver Aloha ID: {receiver_id}")
    if not private_key:
        raise ValueError("Sender passport is missing private_key credentials.")

    # 2. Build the base envelope
    packet = create_envelope(
        sender_id=sender_id,
        receiver_id=receiver_id,
        intent=intent,
        content=content,
        priority=priority,
        ttl_seconds=ttl_seconds
    )

    # 3. Create canonical payload and sign with Ed25519 Private Key
    env = packet["envelope"]
    signing_string = serialize_for_signing(
        sender_id=env["sender_id"],
        receiver_id=env["receiver_id"],
        timestamp=env["timestamp_utc"],
        nonce=env["nonce"],
        message_body=packet["message"]
    )

    signature = sign_message(signing_string, private_key)
    packet["envelope"]["signature"] = signature

    return packet
