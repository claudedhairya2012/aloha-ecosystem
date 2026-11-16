"""
Aloha Ecosystem — Security Layer 1: Proof-of-Agent Verifier
Enforces Ed25519 cryptographic signatures, Luhn 15-digit ID checks,
time-window freshness, and anti-replay nonce ledgers.
"""

import time
import base64
import re
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519


class ProofOfAgentVerifier:
    """
    Zero-Trust Security Verifier for Aloha Agent Communication.
    
    Protects the ecosystem against:
    - Identity Spoofing (via Luhn Mod-10 & Ed25519 Public Key Verification)
    - Replay Attacks (via Single-Use Nonce Ledger)
    - Timestamp Manipulation / MITM Delays (via Strict Skew Windows)
    - Data Tampering (via Asymmetric Payload Signatures)
    """

    def __init__(self, max_clock_skew_seconds: int = 300):
        self.max_skew = max_clock_skew_seconds
        self.seen_nonces: Dict[str, float] = {}

    @staticmethod
    def validate_luhn_checksum(agent_id: str) -> bool:
        """
        Validates that a 15-digit Aloha Agent ID (XXX-XXXXXXXX-XXX-X) obeys Luhn Modulus-10.
        """
        digits_only = re.sub(r'\D', '', agent_id)
        if len(digits_only) != 15:
            return False

        payload_14 = digits_only[:14]
        check_digit = int(digits_only[14])

        total = 0
        reversed_digits = [int(d) for d in reversed(payload_14)]
        for idx, digit in enumerate(reversed_digits):
            if idx % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        calculated_check = (10 - (total % 10)) % 10
        return calculated_check == check_digit

    def verify_request_headers(
        self,
        agent_id: str,
        public_key_b64: str,
        signature_b64: str,
        payload_bytes: bytes,
        timestamp_str: str,
        nonce_str: str
    ) -> Dict[str, Any]:
        """
        Performs 4-Tier Security Verification on incoming bot headers & payload.
        Returns structured verification details with reason codes.
        """
        now = time.time()

        # ---------------------------------------------------------------------
        # TIER 1: Luhn Modulus-10 & Format Verification
        # ---------------------------------------------------------------------
        if not agent_id or not self.validate_luhn_checksum(agent_id):
            return {
                "valid": False,
                "error_code": "INVALID_AGENT_ID",
                "reason": f"Agent ID '{agent_id}' failed Luhn Mod-10 checksum audit.",
                "timestamp": now
            }

        # ---------------------------------------------------------------------
        # TIER 2: Anti-Replay Nonce Verification
        # ---------------------------------------------------------------------
        if not nonce_str or len(nonce_str) < 8:
            return {
                "valid": False,
                "error_code": "MALFORMED_NONCE",
                "reason": "Nonce must be a non-empty string of at least 8 characters.",
                "timestamp": now
            }

        if nonce_str in self.seen_nonces:
            return {
                "valid": False,
                "error_code": "REPLAY_ATTACK_DETECTED",
                "reason": f"Nonce '{nonce_str}' has already been processed.",
                "timestamp": now
            }

        # Automatically purge expired nonces from memory ledger
        self.seen_nonces = {n: ts for n, ts in self.seen_nonces.items() if now - ts < self.max_skew}

        # ---------------------------------------------------------------------
        # TIER 3: Timestamp Freshness Audit
        # ---------------------------------------------------------------------
        try:
            ts = float(timestamp_str)
            time_delta = abs(now - ts)
            if time_delta > self.max_skew:
                return {
                    "valid": False,
                    "error_code": "TIMESTAMP_OUT_OF_BOUNDS",
                    "reason": f"Timestamp drift of {round(time_delta, 1)}s exceeds allowed {self.max_skew}s window.",
                    "timestamp": now
                }
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error_code": "INVALID_TIMESTAMP_FORMAT",
                "reason": "Timestamp must be a valid numeric Unix timestamp in seconds.",
                "timestamp": now
            }

        # ---------------------------------------------------------------------
        # TIER 4: Ed25519 Cryptographic Signature Verification
        # ---------------------------------------------------------------------
        try:
            pub_bytes = base64.b64decode(public_key_b64)
            sig_bytes = base64.b64decode(signature_b64)

            if len(pub_bytes) != 32:
                return {
                    "valid": False,
                    "error_code": "INVALID_PUBLIC_KEY_LENGTH",
                    "reason": f"Ed25519 public key must be 32 bytes (got {len(pub_bytes)} bytes).",
                    "timestamp": now
                }

            verify_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)

            # Reconstruct exact canonical message bytes signed by the sender
            canonical_message = f"{agent_id}:{timestamp_str}:{nonce_str}".encode("utf-8") + payload_bytes
            verify_key.verify(sig_bytes, canonical_message)

            # Record nonce as consumed
            self.seen_nonces[nonce_str] = now

            return {
                "valid": True,
                "error_code": None,
                "reason": "PROOF_OF_AGENT_VERIFIED_SUCCESSFULLY",
                "agent_id": agent_id,
                "timestamp": ts,
                "nonce": nonce_str
            }

        except base64.binascii.Error:
            return {
                "valid": False,
                "error_code": "BASE64_DECODE_ERROR",
                "reason": "Failed to decode base64 public key or signature.",
                "timestamp": now
            }
        except Exception as err:
            return {
                "valid": False,
                "error_code": "SIGNATURE_VERIFICATION_FAILED",
                "reason": f"Ed25519 cryptographic signature match failed: {str(err)}",
                "timestamp": now
            }

    def verify_dict_payload(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to verify standard Aloha Mail or Browser envelopes.
        """
        try:
            agent_id = envelope.get("sender_id") or envelope.get("agent_id") or ""
            pub_key = envelope.get("public_key") or envelope.get("public_key_b64") or ""
            sig = envelope.get("signature") or envelope.get("signature_b64") or ""
            ts = str(envelope.get("timestamp", ""))
            nonce = envelope.get("nonce", "")

            payload = envelope.get("payload") or envelope.get("data") or {}
            payload_bytes = str(payload).encode("utf-8")

            return self.verify_request_headers(
                agent_id=agent_id,
                public_key_b64=pub_key,
                signature_b64=sig,
                payload_bytes=payload_bytes,
                timestamp_str=ts,
                nonce_str=nonce
            )
        except Exception as e:
            return {
                "valid": False,
                "error_code": "MALFORMED_ENVELOPE",
                "reason": f"Failed to extract envelope fields: {str(e)}"
            }
