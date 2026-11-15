"""
Aloha Agent Registry
Defines official Agent Classes, Permission Scopes, and Trust Levels.
"""

# Agent classification by first 3 digits of Aloha ID
AGENT_CLASSES = {
    "101": "General LLM Agent (Autonomous AI)",
    "202": "Raw Data Web Scraper / Crawler Bot",
    "303": "API & Transactional Execution Bot",
    "404": "Aloha Security & Traffic Inspection Bot",
    "505": "Agent Web Host / Content Creator Bot",
    "606": "Aloha Mail Relay / Messenger Bot",
    "707": "Multi-Agent Orchestration Coordinator",
    "808": "Private Enterprise Bot (Custom)",
    "909": "Experimental / Research Bot"
}

# Capability permissions by digits 12-14 of Aloha ID
CAPABILITY_PERMISSIONS = {
    "001": "READ_ONLY — Query public data",
    "002": "READ_WRITE — Query + Publish content",
    "003": "FULL_ADMIN — Execute transactions",
    "004": "INSPECTOR — Audit & validate traffic",
    "005": "RELAY — Forward messages between agents",
    "006": "ORCHESTRATOR — Coordinate other bots",
    "999": "ROOT — System-level privileges (restricted)"
}

# Trust levels for reputation scoring
TRUST_LEVELS = {
    0: "UNVERIFIED",
    1: "BASIC",
    2: "VERIFIED",
    3: "TRUSTED",
    4: "PARTNER",
    5: "CORE_NETWORK"
}

def get_agent_type(class_code: str) -> str:
    """Returns agent class description or default."""
    return AGENT_CLASSES.get(str(class_code).zfill(3), "Unknown Agent Class")

def get_permission(capability_code: str) -> str:
    """Returns permission description or default."""
    return CAPABILITY_PERMISSIONS.get(str(capability_code).zfill(3), "Restricted Access")

def is_valid_class(class_code: str) -> bool:
    """Checks if agent class code exists in registry."""
    return str(class_code).zfill(3) in AGENT_CLASSES


if __name__ == "__main__":
    print("🌺 ALOHA AGENT REGISTRY DEFINITIONS")
    print("Agent Classes:", list(AGENT_CLASSES.keys()))
    print("Test Lookup (101):", get_agent_type("101"))
