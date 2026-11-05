"""Servidor TCP opcional para demonstrar comunicação entre processos."""
import json
import logging
import os
import socketserver

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/socket_events.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8",
)


class EventHandler(socketserver.StreamRequestHandler):
    def handle(self):
        raw = self.rfile.readline(4096)
        try:
            event = json.loads(raw.decode("utf-8"))
            # Não registrar dados pessoais; apenas tipo do evento e identificador.
            logging.info("evento=%s id=%s", event.get("event"), event.get("occurrence_id"))
            self.wfile.write(b"OK\n")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            logging.warning("mensagem TCP invalida")
            self.wfile.write(b"INVALID\n")


if __name__ == "__main__":
    host = os.getenv("TCP_HOST", "127.0.0.1")
    port = int(os.getenv("TCP_PORT", "5050"))
    with socketserver.ThreadingTCPServer((host, port), EventHandler) as server:
        print(f"Servidor TCP ativo em {host}:{port}. Pressione Ctrl+C para encerrar.")
        server.serve_forever()
