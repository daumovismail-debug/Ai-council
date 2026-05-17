"""
GitHub webhook server.
Listens on port 9000, verifies HMAC signature, runs deploy.sh on push to main.
"""
import hashlib
import hmac
import json
import logging
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").encode()
DEPLOY_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy.sh")
PORT = int(os.getenv("WEBHOOK_PORT", "9000"))


def verify_signature(payload: bytes, signature_header: str) -> bool:
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set — skipping signature check")
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default access log
        logger.info(fmt, *args)

    def do_POST(self):
        if self.path != "/webhook":
            self._respond(404, "Not found")
            return

        length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(length)

        sig = self.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(payload, sig):
            logger.warning("Invalid webhook signature")
            self._respond(401, "Unauthorized")
            return

        event = self.headers.get("X-GitHub-Event", "")
        if event != "push":
            self._respond(200, f"Ignored event: {event}")
            return

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            self._respond(400, "Bad JSON")
            return

        ref = data.get("ref", "")
        if ref != "refs/heads/main":
            self._respond(200, f"Ignored ref: {ref}")
            return

        logger.info("Push to main received — running deploy")
        self._respond(200, "Deploying")
        self._run_deploy()

    def _respond(self, code: int, message: str) -> None:
        body = message.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _run_deploy(self) -> None:
        try:
            result = subprocess.run(
                ["bash", DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=120,
            )
            logger.info("Deploy stdout: %s", result.stdout)
            if result.returncode != 0:
                logger.error("Deploy stderr: %s", result.stderr)
        except Exception as e:
            logger.error("Deploy failed: %s", e)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    logger.info("Webhook server listening on port %s", PORT)
    server.serve_forever()
