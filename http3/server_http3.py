# Exemplo simplificado de servidor HTTP/3 com aioquic
import asyncio
import logging
import os

from aioquic.asyncio import serve
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.protocol import QuicConnectionProtocol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WORKLOADS_DIR = os.path.join(os.getcwd(), "workloads")

class H3ServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None

    def quic_event_received(self, event):
        if self._http is None:
            self._http = H3Connection(self._quic)
        for http_event in self._http.handle_event(event):
            self.http_event_received(http_event)

    def http_event_received(self, event):
        from aioquic.h3.events import HeadersReceived
        if isinstance(event, HeadersReceived):
            path = None
            for name, value in event.headers:
                if name == b":path":
                    path = value.decode()
            if path and path.startswith("/workloads/"):
                rel_path = path[len("/workloads/"):]
                file_path = os.path.join(WORKLOADS_DIR, rel_path.replace("/", os.sep))
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        data = f.read()
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == ".html":
                        content_type = b"text/html"
                    elif ext == ".mp3":
                        content_type = b"audio/mpeg"
                    elif ext == ".mp4":
                        content_type = b"video/mp4"
                    else:
                        content_type = b"application/octet-stream"
                    headers = [
                        (b":status", b"200"),
                        (b"content-type", content_type),
                    ]
                    self._http.send_headers(event.stream_id, headers)
                    self._http.send_data(event.stream_id, data, end_stream=True)
                else:
                    headers = [
                        (b":status", b"404"),
                        (b"content-type", b"text/plain"),
                    ]
                    self._http.send_headers(event.stream_id, headers)
                    self._http.send_data(event.stream_id, "Arquivo não encontrado".encode("utf-8"), end_stream=True)
            else:
                headers = [
                    (b":status", b"200"),
                    (b"content-type", b"text/plain"),
                ]
                self._http.send_headers(event.stream_id, headers)
                self._http.send_data(event.stream_id, b"Resposta via HTTP/3", end_stream=True)

async def main():
    config = QuicConfiguration(is_client=False, alpn_protocols=H3_ALPN)
    config.load_cert_chain("cert.pem", "key.pem")
    server = await serve(
        "localhost", 4433,
        configuration=config,
        create_protocol=H3ServerProtocol,
    )
    logging.info("Servidor HTTP/3 ouvindo em localhost:4433")
    # Mantém o servidor rodando
    await asyncio.Event().wait()

if __name__ == "__main__":
    logging.info("Iniciando server_http3.py")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Erro fatal: {e}")