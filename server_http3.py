import asyncio
import os
import logging
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.server import serve
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import HeadersReceived
from aioquic.quic.events import StreamDataReceived, ConnectionTerminated

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class HttpServerProtocol:
    def __init__(self):
        self.h3_conn = None
        logging.info("Inicializando HttpServerProtocol")

    def handle_stream(self, stream_id, event):
        logging.info(f"Recebido evento em stream_id {stream_id}: {type(event)}")
        if isinstance(event, HeadersReceived):
            path = next((h[1].decode() for h in event.headers if h[0] == b":path"), "/")
            headers = [(b":status", b"200"), (b"content-type", b"text/plain")]
            data = b"Response via HTTP/3"
            logging.info(f"Processando path: {path}")

            if path == "/json":
                headers = [(b":status", b"200"), (b"content-type", b"application/json")]
                data = b'{"message": "Hello, World!"}'
            elif path.startswith("/file/"):
                size = path.split("/")[-1]
                sizes = {"1mb.bin": "1mb.bin", "10mb.bin": "10mb.bin", "100mb.bin": "100mb.bin"}
                if size in sizes:
                    file_path = os.path.join("files", sizes[size])
                    if os.path.exists(file_path):
                        headers = [(b":status", b"200"), (b"content-type", b"application/octet-stream")]
                        with open(file_path, "rb") as f:
                            data = f.read()
                        logging.info(f"Servindo arquivo: {file_path}")
                    else:
                        headers = [(b":status", b"404")]
                        data = b"File not found"
                        logging.warning(f"Arquivo não encontrado: {file_path}")
                else:
                    headers = [(b":status", b"400")]
                    data = b"Invalid size"
                    logging.warning(f"Tamanho inválido: {size}")

            self.h3_conn.send_headers(stream_id, headers)
            self.h3_conn.send_data(stream_id, data, end_stream=True)

    def quic_event_received(self, event):
        logging.info(f"Evento QUIC recebido: {type(event)}")
        if isinstance(event, StreamDataReceived):
            if not self.h3_conn:
                self.h3_conn = H3Connection(event.connection)
                self.h3_conn.send_settings()
            for h3_event in self.h3_conn.handle_event(event):
                self.handle_stream(event.stream_id, h3_event)
        elif isinstance(event, ConnectionTerminated):
            logging.error(f"Conexão encerrada: code={event.error_code}, reason={event.reason_phrase}")

async def main():
    logging.info("Carregando configuração do servidor")
    try:
        config = QuicConfiguration(
            alpn_protocols=["h3"], is_client=False,
            max_datagram_frame_size=65536
        )
        config.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
        logging.info("Certificados carregados com sucesso")
        server = HttpServerProtocol()
        logging.info("Iniciando servidor na porta 4433")
        await serve(
            "localhost", 4433,
            configuration=config,
            stream_handler=lambda stream_id, event, h3_conn: server.quic_event_received(event)
        )
        logging.info("Servidor rodando")
        await asyncio.Future()
    except Exception as e:
        logging.error(f"Erro ao iniciar servidor: {e}")
        raise

if __name__ == "__main__":
    logging.info("Iniciando server_http3.py")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Erro fatal: {e}")