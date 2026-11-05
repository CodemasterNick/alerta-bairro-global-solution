import json
import os
import socket


def notify_tcp(event):
    """Envia um evento JSON para o servidor TCP local; falha sem interromper a API."""
    host = os.getenv("TCP_HOST", "127.0.0.1")
    port = int(os.getenv("TCP_PORT", "5050"))
    try:
        message = json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n"
        with socket.create_connection((host, port), timeout=1.5) as client:
            client.sendall(message)
    except OSError:
        # O servidor TCP é um módulo demonstrativo opcional.
        pass
