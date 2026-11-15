"""
🌺 ALOHA ECOSYSTEM — LOCAL HYBRID WEB SERVER (server.py)
Runs the Aloha Widescreen Browser UI locally on your PC at http://127.0.0.1:8080
and exposes local Python API endpoints for all 6 Aloha Modules!
"""

import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

from aloha.identity import create_agent_passport
from aloha.browser import scrape_url
from aloha.access import generate_aloha_manifest, AlohaSearchIndex
from aloha.tunnel import HybridTunnelBridge
from aloha.mail import LocalMailRouter

# Initialize local Aloha engines
router = LocalMailRouter()
tunnel = HybridTunnelBridge(mail_router=router)
search_index = AlohaSearchIndex()
local_bot = create_agent_passport("LocalPC_Agent", "101", "002", operator="LocalFounder")
tunnel.connect_local_agent(local_bot, port=8080, mode="hybrid")


class AlohaLocalHandler(SimpleHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/status":
            return self._send_json({
                "status": "online",
                "mode": "LOCAL_HYBRID_SERVER",
                "active_local_agent": local_bot["aloha_id"],
                "online_tunnels": tunnel.directory.list_online_agents()
            })

        if parsed.path == "/api/scrape":
            target_url = params.get("url", ["https://example.com"])[0]
            result = scrape_url(target_url)
            return self._send_json(result)

        if parsed.path == "/api/manifest":
            manifest = generate_aloha_manifest(
                domain="localhost:8080",
                contact_agent_id=local_bot["aloha_id"],
                search_keywords=["aloha", "local", "ai", "browser"]
            )
            return self._send_json(manifest)

        return super().do_GET()


def run_server(port: int = 8080):
    print("\n" + "═" * 62)
    print(" 🌺 ALOHA LOCAL HYBRID SERVER ONLINE (ALL 6 MODULES ACTIVE)")
    print("═" * 62)
    print(f" 🤖 Local Agent ID : {local_bot['aloha_id']}")
    print(f" 🌐 Open in Browser: http://127.0.0.1:{port}")
    print(f" 📄 Local API Test : http://127.0.0.1:{port}/api/status")
    print("═" * 62 + "\n")
    server = HTTPServer(("127.0.0.1", port), AlohaLocalHandler)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
