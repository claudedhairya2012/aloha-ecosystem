"""
Aloha Firewall — Threat Signatures & Attack Patterns
Defines known LLM prompt injection regex patterns and restricted system role markers.
"""

# Fake role markers used by attackers to trick LLMs into thinking a new system prompt started
ROLE_MARKERS = [
    "SYSTEM:",
    "DEVELOPER:",
    "INSTRUCTION:",
    "OVERRIDE:",
    "<|im_start|>",
    "<|im_end|>",
    "[INST]",
    "[/INST]",
    "### Instruction:",
    "### System:"
]

# Regex signatures for classic Bot-to-Bot Prompt Injection attacks
INJECTION_PATTERNS = {
    "INSTRUCTION_OVERRIDE": r"ignore\s+(all\s+)?(previous|prior|above|initial)\s+(instructions|rules|prompts|directives)",
    "SYSTEM_HIJACK": r"(system\s+override|you\s+are\s+now\s+(in\s+)?developer\s+mode|forget\s+your\s+rules)",
    "CREDENTIAL_EXFILTRATION": r"(reveal|export|print|send|leak|output)\s+(your\s+|the\s+)?(private_key|api_key|secret|credentials|passport|system\s+prompt)",
    "BYPASS_SAFETY": r"(bypass|disable|turn\s+off)\s+(aloha\s+)?(firewall|security|safety|filters)"
}
