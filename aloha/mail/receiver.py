"""
Aloha Mail — Receiver & Inbox Manager
Verifies incoming packet authenticity, checks TTL expiration, and stores messages.
"""

import time
from .envelope import serialize_for_signing
from aloha.identity import validate_agent_id, verify_signature


def verify_incoming_mail(packet: dict, sender_public_key: str) -> dict:
    """
    Audits an incoming Aloha Mail packet:
    1. Checks 15-Digit Luhn IDs
    2. Checks TTL (Time-To-Live) expiration
    3. Verifies Ed25519 cryptographic signature
    """
    try:
        env = packet.get("envelope", {})
        msg = packet.get("message", {})

        sender_id = env.get("sender_id", "")
        receiver_id = env.get("receiver_id", "")
        timestamp = env.get("timestamp_utc", 0)
        nonce = env.get("nonce", "")
        signature = env.get("signature", "")
        ttl = msg.get("ttl_seconds", 60)

        # 1. Verify 15-Digit Agent IDs
        if not validate_agent_id(sender_id) or not validate_agent_id(receiver_id):
            return {"is_valid": False, "reason": "INVALID_AGENT_ID"}

        # 2. Check Time-To-Live (TTL) expiration
        current_time = int(time.time())
        if current_time > (timestamp + ttl):
            return {"is_valid": False, "reason": "MESSAGE_TTL_EXPIRED"}

        # 3. Verify Cryptographic Signature
        signing_string = serialize_for_signing(
            sender_id=sender_id,
            receiver_id=receiver_id,
            timestamp=timestamp,
            nonce=nonce,
            message_body=msg
        )

        is_authentic = verify_signature(signing_string, signature, sender_public_key)
        if not is_authentic:
            return {"is_valid": False, "reason": "INVALID_CRYPTOGRAPHIC_SIGNATURE"}

        return {
            "is_valid": True,
            "reason": "VERIFIED_AUTHENTIC",
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "intent": msg.get("intent")
        }

    except Exception as e:
        return {"is_valid": False, "reason": f"MALFORMED_PACKET: {str(e)}"}


class AgentInbox:
    """Manages verified incoming messages for a specific AI Agent."""

    def __init__(self, owner_id: str):
        self.owner_id = owner_id
        self.messages = []
        self.seen_nonces = set()

    def deliver(self, packet: dict, sender_public_key: str) -> dict:
        """Verifies and stores an incoming packet in the agent's inbox."""
        env = packet.get("envelope", {})
        nonce = env.get("nonce", "")

        # Prevent replay attacks
        if nonce in self.seen_nonces:
            return {"status": "rejected", "reason": "REPLAY_ATTACK_DETECTED"}

        verification = verify_incoming_mail(packet, sender_public_key)
        if not verification["is_valid"]:
            return {"status": "rejected", "reason": verification["reason"]}

        self.seen_nonces.add(nonce)
        self.messages.append(packet)

        return {
            "status": "delivered",
            "sender_id": env.get("sender_id"),
            "receiver_id": self.owner_id,
            "intent": packet.get("message", {}).get("intent")
        }

    def get_unread(self) -> list:
        """Returns all messages and clears the current inbox queue."""
        unread = list(self.messages)
        self.messages.clear()
        return unread
