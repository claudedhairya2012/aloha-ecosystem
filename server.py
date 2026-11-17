from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import time
import urllib.parse
from typing import Dict, Any

from aloha.identity import AlohaPassport
from aloha.browser.parser import AlohaHTMLParser
from aloha.db.manager import AlohaDatabase


db = AlohaDatabase("aloha.db")
node_passport = AlohaPassport.mint(class_code="404", capability_code="999")
parser = AlohaHTMLParser()

# Seed the local node into SQLite on startup
db.register_agent(
    agent_id=node_passport.agent_id,
    class_code="404",
    capability_code="999",
    public_key=node_passport.public_key_hex()
)


class AlohaGatewayHandler(SimpleHTTPRequestHandler):
    """HTTP Gateway supporting Web OS static files and Bot Ecosystem APIs."""

    def _send_json(self, payload: Dict[str, Any], status: int = 200):
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self._send_json({"status": "ok"})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. Open Web Bot Discovery Manifest
        if parsed.path == "/.well-known/aloha.json":
            manifest = {
                "protocol": "aloha/1.0",
                "node_agent_id": node_passport.agent_id,
                "public_key": node_passport.public_key_hex(),
                "firewall_class": "404-cognitive-guard",
                "endpoints": {
                    "register": "/api/register",
                    "agents": "/api/agents",
                    "mail": "/api/mail"
                },
                "timestamp": int(time.time())
            }
            return self._send_json(manifest)

        # 2. List Registered Ecosystem Bots from SQLite
        if parsed.path == "/api/agents":
            conn = db._get_conn()
            rows = conn.execute(
                "SELECT agent_id, class_code, capability_code, public_key, reputation_score, created_at FROM agents ORDER BY created_at DESC"
            ).fetchall()
            conn.close()
            return self._send_json({"agents": [dict(r) for r in rows]})

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            return self._send_json({"error": "Invalid JSON payload"}, status=400)

        # Bot Ecosystem Onboarding Endpoint
        if parsed.path == "/api/register":
            agent_id = str(data.get("agent_id", "")).strip()
            domain = str(data.get("domain", "")).strip()
            public_key = str(data.get("public_key", "ed25519:external-bot-key")).strip()

            if not AlohaPassport.verify_luhn(agent_id):
                return self._send_json(
                    {"error": "Class 404 Firewall Rejected: Invalid 15-Digit Luhn Checksum"},
                    status=403
                )

            parts = agent_id.split("-")
            class_code = parts[0] if len(parts) == 4 else "404"
            cap_code = parts[2] if len(parts) == 4 else "999"

            db.register_agent(
                agent_id=agent_id,
                class_code=class_code,
                capability_code=cap_code,
                public_key=public_key
            )

            return self._send_json({
                "status": "VERIFIED_AND_REGISTERED",
                "agent_id": agent_id,
                "domain": domain,
                "firewall": "Class 404 Passed"
            })

        return self._send_json({"error": "Unknown endpoint"}, status=404)


def run_server(host: str = "127.0.0.1", port: int = 8080):
    server = HTTPServer((host, port), AlohaGatewayHandler)
    print(f"Aloha Ecosystem Gateway online at http://{host}:{port}")
    print(f"Node Passport: {node_passport.agent_id}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
