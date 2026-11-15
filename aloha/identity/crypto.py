"""
Aloha Cryptographic Engine
Ed25519 digital signatures for agent message authentication.
"""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64
import hashlib


def generate_keypair() -> dict:
    """Generates a fresh Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return {
        "private_key": base64.b64encode(priv_bytes).decode("utf-8"),
        "public_key": base64.b64encode(pub_bytes).decode("utf-8"),
        "algorithm": "Ed25519"
    }


def fingerprint_key(public_key_b64: str) -> str:
    """Generates 16-character SHA-256 fingerprint of a public key."""
    digest = hashlib.sha256(public_key_b64.encode("utf-8")).hexdigest()
    return digest[:16]


def export_public_key(public_key_b64: str) -> str:
    """Exports public key in PEM string format."""
    pub_bytes = base64.b64decode(public_key_b64)
    key_obj = Ed25519PublicKey.from_public_bytes(pub_bytes)
    pem = key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode("utf-8")


def sign_message(message: str, private_key_b64: str) -> str:
    """Signs a message using the agent's base64 private key."""
    priv_bytes = base64.b64decode(private_key_b64)
    key_obj = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    signature = key_obj.sign(message.encode("utf-8"))
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(message: str, signature_b64: str, public_key_b64: str) -> bool:
    """Verifies a signature against a message and public key."""
    try:
        pub_bytes = base64.b64decode(public_key_b64)
        sig_bytes = base64.b64decode(signature_b64)
        key_obj = Ed25519PublicKey.from_public_bytes(pub_bytes)
        key_obj.verify(sig_bytes, message.encode("utf-8"))
        return True
    except (InvalidSignature, Exception):
        return False


if __name__ == "__main__":
    keys = generate_keypair()
    msg = "Test Aloha Message"
    sig = sign_message(msg, keys["private_key"])
    print("🌺 Signature Verification:", verify_signature(msg, sig, keys["public_key"]))
