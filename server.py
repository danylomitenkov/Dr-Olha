#!/usr/bin/env python3
import http.server
import socket
import socketserver
import sys

PORT = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Отключаем агрессивный кеш браузера для быстрой разработки
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    ip = get_local_ip()
    print("=" * 65)
    print("  ⚔️  ХРОНИКИ НЕСТВЕДА • D&D КВЕСТ-ПРИКЛЮЧЕНИЕ  ⚔️")
    print("=" * 65)
    print(f"\n🎮 ССЫЛКА ДЛЯ ЖЕНЫ (Чистый игровой режим):")
    print(f"   👉 http://{ip}:{PORT}")
    print(f"\n🗝️ ССЫЛКА ДЛЯ МАСТЕРА ИГРЫ (С открытым DM Терминалом):")
    print(f"   👉 http://{ip}:{PORT}?dm=1")
    print("\n   (Также на компьютере: http://localhost:8080)")
    print("-" * 65)
    print("💡 Подсказка: Чтобы запустить квест на улице без домашнего Wi-Fi:")
    print("   1. Либо раздай Wi-Fi точку с телефона на ноутбук;")
    print("   2. Либо залей index.html на Netlify Drop / GitHub Pages за 1 минуту;")
    print("   3. Либо отправь файл index.html прямо в Telegram.")
    print("=" * 65)
    print(f"Сервер запущен на порту {PORT}... (Нажми Ctrl+C для остановки)\n")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
            sys.exit(0)

if __name__ == '__main__':
    main()
