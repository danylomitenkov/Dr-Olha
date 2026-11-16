#!/usr/bin/env python3
import http.server
import json
import os
import socket
import socketserver
import sys
import time

PORT = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTS_FILE = os.path.join(BASE_DIR, "quests.json")


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class QuestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/quests":
            if os.path.exists(QUESTS_FILE):
                try:
                    with open(QUESTS_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        self._send_json(200, {"quests": data, "session": None, "broadcast": None, "updatedAt": 0, "resetNonce": 0})
                    else:
                        self._send_json(200, {
                            "quests": data.get("quests"),
                            "session": data.get("session"),
                            "broadcast": data.get("broadcast"),
                            "updatedAt": data.get("updatedAt", 0),
                            "resetNonce": data.get("resetNonce", 0),
                        })
                    return
                except Exception as exc:
                    self._send_json(500, {"error": str(exc)})
                    return
            self._send_json(200, {"quests": None, "session": None, "broadcast": None, "updatedAt": 0, "resetNonce": 0})
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] == "/api/quests":
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(content_length)
                payload = json.loads(raw_body.decode("utf-8"))
                quests = payload.get("quests")
                if not isinstance(quests, list):
                    self._send_json(400, {"error": "Invalid quests payload"})
                    return
                record = {
                    "quests": quests,
                    "session": payload.get("session"),
                    "broadcast": payload.get("broadcast"),
                    "updatedAt": payload.get("updatedAt", int(time.time() * 1000)),
                    "resetNonce": payload.get("resetNonce", 0),
                }
                with open(QUESTS_FILE, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
                self._send_json(200, {"ok": True, "count": len(quests), "updatedAt": record["updatedAt"]})
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
            return
        self._send_json(404, {"error": "Not found"})


def main():
    ip = get_local_ip()
    print("=" * 68)
    print("  ⚔️  ХРОНИКИ НЕСТВЕДА • D&D КВЕСТ-ПРИКЛЮЧЕНИЕ  ⚔️")
    print("=" * 68)
    print(f"\n🎮 ССЫЛКА ДЛЯ ИГРОКА (Чистый режим без спойлеров и без DM-доступа):")
    print(f"   👉 http://{ip}:{PORT}")
    print(f"\n🗝️ СЕКРЕТНАЯ ССЫЛКА ДЛЯ МАСТЕРА (DM Terminal, ПИН-код: 2026):")
    print(f"   👉 http://{ip}:{PORT}?dm=master2026")
    print(f"\n   (Локально на ноутбуке: http://localhost:{PORT}?dm=master2026)")
    print("-" * 68)
    print("💡 Для игры на улице по GPS (нужен HTTPS):")
    print("   1. Перетащи index.html (или скачанный olha-quest.html) на https://app.netlify.com/drop")
    print("   2. Или подними туннель: ssh -R 80:localhost:8080 nokey@localhost.run")
    print("=" * 68)
    print(f"Сервер слушает порт {PORT}... (Ctrl+C для остановки)\n")

    with ReusableTCPServer(("", PORT), QuestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
            sys.exit(0)


if __name__ == "__main__":
    main()
