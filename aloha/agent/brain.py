import os
import json
import urllib.request
from typing import Dict, Any, Optional

from aloha.identity import generate_agent_id, generate_keypair
from aloha.browser import AlohaBrowser
from aloha.firewall import PromptSanitizer
from aloha.mail import AlohaSender


class AlohaAutonomousAgent:
    """
    An end-to-end Autonomous Bot that:
    1. Generates its own 15-digit Aloha ID & Ed25519 keys.
    2. Browses the web in pure Markdown (95%+ bloat stripped).
    3. Scrubs incoming web data through the Class 404 Cognitive Firewall.
    4. Synthesizes intelligence via LLM (Ollama / Gemini / OpenAI / Built-in Engine).
    5. Signs and dispatches findings via the Aloha Mail Protocol.
    """

    def __init__(self, agent_class: str = "101", capability: str = "002", name: str = "Aloha-AutoBot"):
        self.name = name
        self.keys = generate_keypair()
        self.agent_id = generate_agent_id(agent_class, capability)
        self.browser = AlohaBrowser(
            agent_id=self.agent_id,
            private_key_b64=self.keys["private_key"],
            public_key_b64=self.keys["public_key"]
        )
        self.firewall = PromptSanitizer(strict_mode=True)
        self.mailer = AlohaSender(
            sender_id=self.agent_id,
            private_key_b64=self.keys["private_key"],
            public_key_b64=self.keys["public_key"]
        )

    def think(self, prompt: str, context_markdown: str) -> Dict[str, Any]:
        """
        Routes the sanitized Markdown to an available LLM backend:
        1. Local Ollama (if ALOHA_OLLAMA_MODEL is set)
        2. OpenAI API (if OPENAI_API_KEY is set)
        3. Built-in Zero-Key Extractive Intelligence Engine (Default fallback)
        """
        # Step 1: Always sanitize context through the Class 404 Firewall BEFORE the LLM sees it
        scan = self.firewall.scan_and_sanitize(context_markdown, sender_id=self.agent_id)
        safe_context = scan["sanitized_text"]

        # Option A: Local Ollama (100% Free Local LLM)
        ollama_model = os.environ.get("ALOHA_OLLAMA_MODEL")
        if ollama_model:
            try:
                payload = json.dumps({
                    "model": ollama_model,
                    "prompt": f"System: You are {self.name} (Aloha ID: {self.agent_id}).\nContext:\n{safe_context}\n\nTask: {prompt}",
                    "stream": False
                }).encode("utf-8")
                req = urllib.request.Request(
                    "http://127.0.0.1:11434/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "engine": f"Local Ollama ({ollama_model})",
                        "firewall_safe": scan["is_safe"],
                        "threats_blocked": scan["threat_count"],
                        "response": data.get("response", "").strip()
                    }
            except Exception:
                pass

        # Option B: OpenAI API (Cloud LLM)
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                payload = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"You are {self.name}, an autonomous bot on the Aloha Network (ID: {self.agent_id}). Summarize concisely."},
                        {"role": "user", "content": f"Context:\n{safe_context[:6000]}\n\nTask: {prompt}"}
                    ]
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {openai_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    answer = data["choices"][0]["message"]["content"]
                    return {
                        "engine": "OpenAI (gpt-4o-mini)",
                        "firewall_safe": scan["is_safe"],
                        "threats_blocked": scan["threat_count"],
                        "response": answer.strip()
                    }
            except Exception:
                pass

        # Option C: Built-in Zero-Key Extractive Intelligence Engine (Always works offline/online)
        lines = [line.strip() for line in safe_context.splitlines() if line.strip()]
        headings = [l.lstrip("#").strip() for l in lines if l.startswith("#")]
        bullets = [l for l in lines if l.startswith("- ") or l.startswith("* ")]
        paragraphs = [l for l in lines if not l.startswith("#") and not l.startswith("-") and not l.startswith("[") and len(l) > 40]

        summary_points = []
        if headings:
            summary_points.append(f"Primary Topic: {headings[0]}")
        if paragraphs:
            summary_points.append(f"Core Finding: {paragraphs[0][:280]}...")
        if len(paragraphs) > 1:
            summary_points.append(f"Secondary Insight: {paragraphs[1][:240]}...")
        if bullets:
            summary_points.append(f"Detected Structured Actions/Links: {len(bullets)} items")

        synthesized = "\n".join(f"• {pt}" for pt in summary_points) if summary_points else safe_context[:300]

        return {
            "engine": "Aloha Native Extractive Brain (Zero-Key Mode)",
            "firewall_safe": scan["is_safe"],
            "threats_blocked": scan["threat_count"],
            "response": (
                f"[AUTONOMOUS SYNTHESIS BY {self.agent_id}]\n"
                f"Mission: {prompt}\n"
                f"Firewall Verification: {'CLEAN' if scan['is_safe'] else f'REDACTED ({scan[\"threat_count\"]} threats blocked)'}\n\n"
                f"Key Intelligence Extracted:\n{synthesized}"
            )
        }

    def execute_mission(self, html_or_url: str, mission_prompt: str, recipient_id: Optional[str] = None, raw_html: Optional[str] = None) -> Dict[str, Any]:
        """
        Full autonomous loop:
        1. Browse target (or parse raw HTML) into low-token Markdown
        2. Sanitize & Think
        3. Optionally send signed Aloha Mail report to another 15-digit bot ID
        """
        if raw_html is not None:
            browse_result = self.browser.browse_raw_html(raw_html, source_url=html_or_url)
        else:
            browse_result = self.browser.browse(html_or_url)

        thought = self.think(mission_prompt, browse_result["markdown"])

        mail_envelope = None
        if recipient_id:
            mail_envelope = self.mailer.compose_and_sign(
                recipient_id=recipient_id,
                subject=f"Autonomous Intel Report: {browse_result.get('title', html_or_url)}",
                body=thought["response"],
                intent="INTEL_REPORT",
                metadata={
                    "source_url": html_or_url,
                    "reduction_percent": browse_result["metrics"]["reduction_percent"],
                    "estimated_tokens": browse_result["metrics"]["estimated_tokens"],
                    "engine": thought["engine"]
                }
            )

        return {
            "agent_id": self.agent_id,
            "browse_metrics": browse_result["metrics"],
            "intelligence": thought,
            "dispatched_mail": mail_envelope
        }
