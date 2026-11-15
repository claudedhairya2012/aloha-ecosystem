"""
🌺 Aloha Ecosystem — Local-to-Cloud Hybrid Tunnel Module (Module 5)
Bridges local AI agents (running on a laptop/PC) with cloud agents and relays.
"""

from .registry import TunnelDirectory
from .bridge import HybridTunnelBridge

__all__ = ["TunnelDirectory", "HybridTunnelBridge"]
__version__ = "2.0.0"
