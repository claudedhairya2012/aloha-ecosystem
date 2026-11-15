"""
Aloha Tunnel — Active Connection Directory
Maps 15-Digit Agent IDs to their live local or cloud tunnel endpoints.
"""

import time
from aloha.identity import validate_agent_id


class TunnelDirectory:
    """
    Tracks which 15-Digit Agent IDs are currently online across Local and Cloud nodes.
    """

    def __init__(self):
        self.active_tunnels = {}  # aloha_id -> connection metadata

    def register_tunnel(
        self,
        aloha_id: str,
        mode: str = "hybrid",
        local_endpoint: str = "http://127.0.0.1:8080",
        cloud_relay: str = "wss://relay.aloha.network"
    ) -> dict:
        """Registers an active Local/Cloud tunnel for a 15-Digit Agent ID."""
        if not validate_agent_id(aloha_id):
            return {"status": "rejected", "reason": "INVALID_ALOHA_ID"}

        clean_mode = mode.lower() if mode.lower() in {"local", "cloud", "hybrid"} else "hybrid"
        session_record = {
            "aloha_id": aloha_id,
            "mode": clean_mode,
            "local_endpoint": local_endpoint,
            "cloud_relay": cloud_relay if clean_mode in {"cloud", "hybrid"} else None,
            "status": "CONNECTED",
            "connected_at_utc": int(time.time()),
            "last_heartbeat_utc": int(time.time())
        }

        self.active_tunnels[aloha_id] = session_record
        return {"status": "registered", "tunnel": session_record}

    def heartbeat(self, aloha_id: str) -> bool:
        """Updates the heartbeat timestamp to keep a local-to-cloud tunnel alive."""
        if aloha_id in self.active_tunnels:
            self.active_tunnels[aloha_id]["last_heartbeat_utc"] = int(time.time())
            return True
        return False

    def lookup_agent(self, aloha_id: str) -> dict:
        """Finds how to route data to a specific 15-Digit Agent ID."""
        tunnel = self.active_tunnels.get(aloha_id)
        if not tunnel:
            return {"online": False, "aloha_id": aloha_id, "reason": "AGENT_OFFLINE"}
        return {"online": True, "tunnel": tunnel}

    def disconnect_tunnel(self, aloha_id: str) -> bool:
        """Closes an active tunnel session."""
        if aloha_id in self.active_tunnels:
            del self.active_tunnels[aloha_id]
            return True
        return False

    def list_online_agents(self) -> list:
        """Returns all currently connected local and cloud agents."""
        return list(self.active_tunnels.values())
