import time
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519


class ProofOfAgentVerifier:
    """
    Security Layer File 1:
    Verifies Ed25519 cryptographic request signatures, checks timestamp freshness (max 300s window),
    and enforces single-use replay nonces to prevent Man-in-the-Middle (MITM) replay attacks.
    """

    def __init__(self, max_clock_skew_seconds: int = 300):
        self.max_skew = max_clock_skew_seconds
        self.seen_nonces: Dict[str, float] = {}

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
        Validates the 5 mandatory Aloha Proof-of-Agent cryptographic headers.
        """
        now = time.time()

        # 1. Anti-Replay Nonce Check
        if nonce_str in self.seen_nonces:
            return {"valid": False, "reason": "REPLAY_ATTACK_DETECTED: Nonce already used"}

        # Clean old nonces older than max skew
        self.seen_nonces = {n: t for n, t in self.seen_nonces.items() if now - t < self.max_skew}

        # 2. Timestamp Freshness Check
        try:
            ts = float(timestamp_str)
            if abs(now - ts) > self.max_skew:
                return {"valid": False, "reason": "TIMESTAMP_EXPIRED: Request outside allowable time window"}
        except ValueError:
            return {"valid": False, "reason": "INVALID_TIMESTAMP_FORMAT"}

        # 3. Ed25519 Cryptographic Signature Verification
        try:
            pub_bytes = base64.b64decode(public_key_b64)
            sig_bytes = base64.b64decode(signature_b64)
            verify_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)

            signed_message = f"{agent_id}:{timestamp_str}:{nonce_str}".encode("utf-8") + payload_bytes
            verify_key.verify(sig_bytes, signed_message)

            # Mark nonce as spent
            self.seen_nonces[nonce_str] = now

            return {
                "valid": True,
                "agent_id": agent_id,
                "reason": "SIGNATURE_VERIFIED_CLEAN",
                "timestamp": ts
            }
        except Exception as e:
            return {"valid": False, "reason": f"CRYPTOGRAPHIC_SIGNATURE_FAILED: {str(e)}"}
