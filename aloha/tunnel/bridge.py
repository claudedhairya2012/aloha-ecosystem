"""
Aloha Tunnel — Local-to-Cloud Hybrid Bridge
Routes signed Aloha Mail packets seamlessly between Local Agents and Cloud Relays.
"""

import time
from .registry import TunnelDirectory
from aloha.firewall import inspect_mail_packet


class HybridTunnelBridge:
    """
    Connects the Local Mail Router on a developer's PC with the Cloud Network.
    Automatically inspects cross-network traffic through the Aloha Firewall.
    """

    def __init__(self, mail_router=None):
        self.directory = TunnelDirectory()
        self.mail_router = mail_router
        self.cloud_outbox = []
        self.transfer_log = []

    def connect_local_agent(self, passport: dict, port: int = 8080, mode: str = "hybrid") -> dict:
        """
        Registers a local bot on both the Local Mail Router and the Hybrid Tunnel Directory.
        """
        aloha_id = passport.get("aloha_id", "")
        if self.mail_router:
            self.mail_router.register_agent(passport)

        endpoint = f"http://127.0.0.1:{port}/agent/{aloha_id}"
        return self.directory.register_tunnel(
            aloha_id=aloha_id,
            mode=mode,
            local_endpoint=endpoint
        )

    def transmit_packet(self, signed_packet: dict) -> dict:
        """
        Transmits a packet across Local or Cloud boundaries:
        1. Runs Aloha Firewall inspection
        2. Checks if receiver is on the Local PC or on the Cloud Relay
        3. Delivers accordingly
        """
        # 1. Inspect packet with Aloha Cognitive Firewall
        audit = inspect_mail_packet(signed_packet)
        if not audit["is_safe"]:
            return {
                "status": "blocked_by_firewall",
                "threats_detected": audit["threats_detected"],
                "sender_id": audit["sender_id"]
            }

        env = signed_packet.get("envelope", {})
        receiver_id = env.get("receiver_id", "")
        sender_id = env.get("sender_id", "")

        # 2. Check receiver tunnel status
        lookup = self.directory.lookup_agent(receiver_id)

        # 3. Route locally if available on local router
        if self.mail_router and receiver_id in self.mail_router.inboxes:
            delivery = self.mail_router.route_mail(signed_packet)
            route_type = "LOCAL_DIRECT"
        else:
            # Queue for Cloud Relay forwarding
            self.cloud_outbox.append(signed_packet)
            delivery = {"status": "forwarded_to_cloud_relay", "receiver_id": receiver_id}
            route_type = "CLOUD_TUNNEL_RELAY"

        record = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "route_type": route_type,
            "receiver_online": lookup.get("online", False),
            "delivery_result": delivery,
            "timestamp_utc": int(time.time())
        }
        self.transfer_log.append(record)
        return record
