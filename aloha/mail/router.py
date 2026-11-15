"""
Aloha Mail — Local Network Router
Routes signed Aloha Mail packets between registered agents.
"""

from .receiver import AgentInbox


class LocalMailRouter:
    """
    In-memory message switchboard that maps 15-Digit Agent IDs
    to their public keys and local inboxes.
    """

    def __init__(self):
        self.public_key_directory = {}
        self.inboxes = {}

    def register_agent(self, passport: dict) -> str:
        """Registers an agent's 15-digit ID and public key on the router."""
        aloha_id = passport.get("aloha_id")
        pub_key = passport.get("credentials", {}).get("public_key")

        if not aloha_id or not pub_key:
            raise ValueError("Invalid passport provided for router registration.")

        self.public_key_directory[aloha_id] = pub_key
        if aloha_id not in self.inboxes:
            self.inboxes[aloha_id] = AgentInbox(owner_id=aloha_id)

        return aloha_id

    def route_mail(self, signed_packet: dict) -> dict:
        """Routes a signed Aloha packet from Sender to Receiver."""
        env = signed_packet.get("envelope", {})
        sender_id = env.get("sender_id")
        receiver_id = env.get("receiver_id")

        if sender_id not in self.public_key_directory:
            return {"status": "failed", "reason": "UNKNOWN_SENDER_ID"}

        if receiver_id not in self.inboxes:
            return {"status": "failed", "reason": "RECEIVER_NOT_FOUND"}

        sender_pub_key = self.public_key_directory[sender_id]
        receiver_inbox = self.inboxes[receiver_id]

        return receiver_inbox.deliver(signed_packet, sender_pub_key)

    def fetch_inbox(self, aloha_id: str) -> list:
        """Retrieves unread messages for a given 15-digit Agent ID."""
        if aloha_id not in self.inboxes:
            return []
        return self.inboxes[aloha_id].get_unread()
