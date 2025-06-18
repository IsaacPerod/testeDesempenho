import asyncio
import logging
import ssl
import os
import json
import time

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import HeadersReceived, DataReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ProtocolNegotiated, ConnectionTerminated

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuicClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None
        self._responses = {}
        self._event = asyncio.Event()

    def quic_event_received(self, event):
        if isinstance(event, ProtocolNegotiated):
            logging.info("Protocolo HTTP/3 negociado")
        if self._http is None:
            self._http = H3Connection(self._quic)
        for http_event in self._http.handle_event(event):
            self.http_event_received(http_event)
        if isinstance(event, ConnectionTerminated):
            logging.error(f"Conexão encerrada: code={event.error_code}, reason={event.reason_phrase}")
            self._event.set()

    def http_event_received(self, event):
        if isinstance(event, HeadersReceived):
            stream_id = event.stream_id
            self._responses[stream_id] = {
                "headers": event.headers,
                "data": b""
            }
        elif isinstance(event, DataReceived):
            stream_id = event.stream_id
            if stream_id in self._responses:
                self._responses[stream_id]["data"] += event.data
                if event.stream_ended:
                    self._event.set()

    async def get_response(self, stream_id, timeout=500):
        try:
            await asyncio.wait_for(self._event.wait(), timeout)
        except asyncio.TimeoutError:
            logging.error("Timeout esperando resposta do servidor")
        resp = self._responses.get(stream_id, None)
        self._event.clear()
        return resp

async def make_request(client, h3_conn, endpoint):
    logging.info(f"Enviando requisição para {endpoint}")
    start_time = time.perf_counter()
    stream_id = h3_conn._quic.get_next_available_stream_id()
    headers = [
        (b":method", b"GET"),
        (b":scheme", b"https"),
        (b":authority", b"localhost"),
        (b":path", endpoint.encode()),
    ]
    h3_conn.send_headers(stream_id, headers, end_stream=True)
    resp = await client.get_response(stream_id)
    latency = time.perf_counter() - start_time
    if resp:
        status = None
        for name, value in resp["headers"]:
            if name == b":status":
                status = value.decode()
        content_length = len(resp["data"])
        content = resp["data"][:100].decode("utf-8", errors="replace")
        return {
            "endpoint": endpoint,
            "status": status,
            "latency": latency,
            "content_length": content_length,
            "content": content
        }
    else:
        return {
            "endpoint": endpoint,
            "status": "timeout",
            "latency": latency,
            "content_length": 0,
            "content": ""
        }

async def main(host="localhost", port=4433):
    print(f"Tentando conectar a {host}:{port}")
    config = QuicConfiguration(is_client=True, alpn_protocols=["h3"])
    config.verify_mode = ssl.CERT_NONE
    logging.info("Configuração do cliente carregada")
    endpoints = [
        "/workloads/web/10kb.html", "/workloads/web/25kb.html", "/workloads/web/50kb.html",
        "/workloads/audio/1mb.mp3", "/workloads/audio/3mb.mp3", "/workloads/audio/5mb.mp3",
        "/workloads/video/20mb.mp4", "/workloads/video/35mb.mp4", "/workloads/video/50mb.mp4"
    ]
    results = []
    async with connect(host, port, configuration=config, create_protocol=QuicClientProtocol) as client:
        logging.info("Conexão estabelecida")
        h3_conn = client._http
        for endpoint in endpoints:
            result = await make_request(client, h3_conn, endpoint)
            results.append(result)
        logging.info("Encerrando cliente")
    HTTP3_DIR = "http3"
    os.makedirs(HTTP3_DIR, exist_ok=True)
    with open(os.path.join(HTTP3_DIR, "results_http3.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logging.info("Resultados salvos em 'http3/results_http3.json'")

if __name__ == "__main__":
    logging.info("Iniciando cliente_http3.py")
    asyncio.run(main())