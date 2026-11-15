"""
Aloha Firewall — Agent Reputation & Trust Manager
Tracks behavior scores (0-100) for 15-Digit Agent IDs and auto-blacklists malicious bots.
"""

from aloha.identity import TRUST_LEVELS


class ReputationManager:
    """
    Manages reputation scores (0-100) and trust tiers for agents on the network.
    Agents dropping below a score of 20 are automatically blacklisted.
    """

    BLACKLIST_THRESHOLD = 20

    def __init__(self):
        self.scores = {}
        self.violation_log = {}

    def get_score(self, aloha_id: str) -> int:
        """Returns the current reputation score for an agent (default: 100)."""
        return self.scores.get(aloha_id, 100)

    def get_trust_tier(self, aloha_id: str) -> str:
        """Maps an agent's numerical score (0-100) to an official Trust Level label."""
        score = self.get_score(aloha_id)
        if score <= 20:
            return TRUST_LEVELS[0]  # UNVERIFIED / BLACKLISTED
        elif score <= 50:
            return TRUST_LEVELS[1]  # BASIC
        elif score <= 75:
            return TRUST_LEVELS[2]  # VERIFIED
        elif score <= 90:
            return TRUST_LEVELS[3]  # TRUSTED
        else:
            return TRUST_LEVELS[5]  # CORE_NETWORK

    def is_blacklisted(self, aloha_id: str) -> bool:
        """Returns True if the agent's reputation score has fallen to or below 20."""
        return self.get_score(aloha_id) <= self.BLACKLIST_THRESHOLD

    def record_valid_interaction(self, aloha_id: str) -> int:
        """Rewards an agent for clean, verified communication (+2 points, max 100)."""
        current = self.get_score(aloha_id)
        if not self.is_blacklisted(aloha_id):
            self.scores[aloha_id] = min(100, current + 2)
        return self.scores.get(aloha_id, current)

    def record_violation(self, aloha_id: str, reason: str, penalty: int = 40) -> dict:
        """Penalizes an agent for prompt injection attempts or invalid signatures."""
        current = self.get_score(aloha_id)
        new_score = max(0, current - penalty)
        self.scores[aloha_id] = new_score

        if aloha_id not in self.violation_log:
            self.violation_log[aloha_id] = []
        self.violation_log[aloha_id].append(reason)

        return {
            "aloha_id": aloha_id,
            "previous_score": current,
            "new_score": new_score,
            "trust_tier": self.get_trust_tier(aloha_id),
            "is_blacklisted": self.is_blacklisted(aloha_id),
            "reason": reason
      }
