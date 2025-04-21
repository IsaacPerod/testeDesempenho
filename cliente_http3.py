import asyncio
import time
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.client import connect
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import HeadersReceived, DataReceived
import argparse

class HttpClient:
    def __init__(self):
        self.response_data = b""
        self.headers = []
        self.complete = False

    def handle_event(self, event):
        if isinstance(event, HeadersReceived):
            self.headers = event.headers
        elif isinstance(event, DataReceived):
            self.response_data += event.data
            self.complete = True

async def make_request(connection, h3_conn, endpoint):
    start_time = time.perf_counter()
    stream_id = connection._quic.get_next_available_stream_id()
    h3_conn.send_headers(
        stream_id=stream_id,
        headers=[
            (b":method", b"GET"),
            (b":scheme", b"https"),
            (b":authority", b"localhost"),
            (b":path", endpoint.encode()),
        ],
        end_stream=True,
    )
    connection._quic.send_stream_data(stream_id, b"", end_stream=True)

    client = HttpClient()
    while not client.complete:
        events = await connection._network.wait_for_events()
        for event in events:
            h3_events = h3_conn.handle_event(event)
            for h3_event in h3_events:
                client.handle_event(h3_event)
        await asyncio.sleep(0.01)

    latency = time.perf_counter() - start_time
    return {
        "endpoint": endpoint,
        "status": next((h[1].decode() for h in client.headers if h[0] == b":status"), "unknown"),
        "latency": latency,
        "content_length": len(client.response_data),
        "content": client.response_data.decode("utf-8", errors="ignore")[:100]
    }

async def main(host="localhost", port=4433):
    print(f"Tentando conectar a {host}:{port}")
    config = QuicConfiguration(is_client=True, alpn_protocols=H3_ALPN)
    config.verify_mode = ssl.CERT_NONE
    logging.info("Configuração do cliente carregada")

    try:
        async with connect(host, port, configuration=config, timeout=10) as connection:
            logging.info("Conexão estabelecida")
            h3_conn = H3Connection(connection._quic)
            endpoints = ["/", "/json", "/file/1mb.bin", "/file/10mb.bin", "/file/100mb.bin"]
            for endpoint in endpoints:
                try:
                    result = await make_request(connection, h3_conn, endpoint)
                    print(f"🔻 Endpoint: {result['endpoint']}")
                    print(f"📦 Status: {result['status']}")
                    print(f"⏱ Latência: {result['latency']:.3f} segundos")
                    print(f"📏 Tamanho: {result['content_length']} bytes")
                    print(f"📜 Conteúdo (primeiros 100 bytes): {result['content']}\n")
                except Exception as e:
                    logging.error(f"Erro ao acessar {endpoint}: {e}")
    except Exception as e:
        logging.error(f"Erro na conexão: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8443)  # Porta alterada para 8443
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))