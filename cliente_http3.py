import asyncio
import ssl
import logging
import time
import json
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import HeadersReceived, DataReceived, H3Event
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ProtocolNegotiated, ConnectionTerminated

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class QuicClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None
        self._responses = {}
        self._event_queue = asyncio.Queue()
        self._closed = False

    def quic_event_received(self, event):
        logging.debug(f"Recebido evento QUIC: {type(event)}")
        if isinstance(event, ProtocolNegotiated):
            if event.alpn_protocol == "h3":
                self._http = H3Connection(self._quic)
                logging.info("Protocolo HTTP/3 negociado")
                self.transmit()
        elif isinstance(event, ConnectionTerminated):
            logging.error(f"Conexão encerrada: code={event.error_code}, reason={event.reason_phrase}")
            self._closed = True
            self._event_queue.put_nowait(None)
        if self._http and not self._closed:
            for h3_event in self._http.handle_event(event):
                self.http_event_received(h3_event)

    def http_event_received(self, event):
        logging.debug(f"Recebido evento HTTP/3: {type(event)}, Detalhes: {event}")
        if isinstance(event, HeadersReceived):
            stream_id = event.stream_id
            if stream_id not in self._responses:
                self._responses[stream_id] = {"status": None, "content": b"", "headers": event.headers}
            for header, value in event.headers:
                if header == b":status":
                    self._responses[stream_id]["status"] = int(value.decode())
            logging.info(f"Cabeçalhos recebidos para stream {stream_id}: {event.headers}")
        elif isinstance(event, DataReceived):
            stream_id = event.stream_id
            if stream_id in self._responses:
                self._responses[stream_id]["content"] += event.data
                if event.stream_ended:
                    self._event_queue.put_nowait((stream_id, self._responses[stream_id]))
                    logging.debug(f"Stream {stream_id} concluído")
                    del self._responses[stream_id]
            else:
                logging.warning(f"Dados recebidos para stream desconhecido {stream_id}. Aguardando HeadersReceived.")
        else:
            logging.debug(f"Evento HTTP/3 não tratado: {type(event)}")

    async def get_response(self):
        result = await self._event_queue.get()
        if result is None:
            raise ConnectionError("Conexão encerrada pelo servidor")
        if not isinstance(result, tuple) or len(result) != 2:
            raise ValueError("Resposta inválida recebida")
        stream_id, response = result
        return response

async def make_request(client, h3_conn, endpoint):
    logging.info(f"Enviando requisição para {endpoint}")
    try:
        stream_id = client._quic.get_next_available_stream_id()
        logging.debug(f"Usando stream_id {stream_id} para {endpoint}")
        h3_conn.send_headers(
            stream_id=stream_id,
            headers=[
                (b":method", b"GET"),
                (b":scheme", b"https"),
                (b":authority", b"localhost"),
                (b":path", endpoint.encode()),
            ],
        )
        h3_conn.send_data(stream_id=stream_id, data=b"", end_stream=True)
        client.transmit()
        timeout = 60 if "file" in endpoint else 30
        response = await asyncio.wait_for(client.get_response(), timeout=timeout)
        response["endpoint"] = endpoint
        response["content_length"] = len(response["content"])
        response["content"] = response["content"][:100].decode("utf-8", errors="ignore")
        return response
    except asyncio.TimeoutError:
        logging.error(f"Tempo limite excedido para o endpoint {endpoint} (timeout={timeout}s)")
        raise
    except Exception as e:
        logging.error(f"Erro ao enviar requisição para {endpoint}: {e}")
        raise

import json  # Adicione esta importação

async def main(host="localhost", port=4433):
    print(f"Tentando conectar a {host}:{port}")
    config = QuicConfiguration(is_client=True, alpn_protocols=["h3"])
    config.verify_mode = ssl.CERT_NONE
    logging.info("Configuração do cliente carregada")

    client = None
    resultados = []  # Lista para armazenar os resultados
    try:
        async with connect(host, port, configuration=config, create_protocol=QuicClientProtocol) as client:
            if not isinstance(client, QuicClientProtocol):
                raise ConnectionError(f"Objeto inválido retornado: {type(client)}")
            logging.info("Conexão estabelecida")
            h3_conn = client._http
            if h3_conn is None:
                raise ConnectionError("Falha na negociação do protocolo HTTP/3")
            endpoints = ["/", "/json", "/file/1mb.bin"]
            for endpoint in endpoints:
                if client._closed:
                    logging.error("Conexão fechada, interrompendo requisições")
                    break
                start_time = time.perf_counter()
                logging.info(f"Iniciando requisição para {endpoint}")
                try:
                    result = await make_request(client, h3_conn, endpoint)
                    elapsed_time = time.perf_counter() - start_time
                    logging.info(f"Requisição para {endpoint} concluída em {elapsed_time:.2f} segundos")
                    print(f"🔻 Endpoint: {result['endpoint']}")
                    print(f"📦 Status: {result['status']}")
                    print(f"📏 Tamanho: {result['content_length']} bytes")
                    print(f"📜 Conteúdo (primeiros 100 bytes): {result['content']}\n")
                    
                    # Adiciona o resultado à lista
                    resultados.append({
                        "endpoint": result['endpoint'],
                        "status": result['status'],
                        "content_length": result['content_length'],
                        "content": result['content'],
                        "elapsed_time": elapsed_time
                    })
                except ConnectionError as e:
                    logging.error(f"Erro ao acessar {endpoint}: {e}")
                    break
                except asyncio.TimeoutError:
                    logging.error(f"Tempo limite ao acessar {endpoint}")
                    break
                except Exception as e:
                    logging.error(f"Erro ao acessar {endpoint}: {e}")
                    continue  # Continuar com o próximo endpoint
    except Exception as e:
        logging.error(f"Erro na conexão: {e}")
    finally:
        if client and not client._closed:
            try:
                client._quic.close()
                logging.info("Conexão fechada com sucesso")
            except AttributeError as e:
                logging.warning(f"Ignorando erro ao fechar conexão: {e}")
            except Exception as e:
                logging.error(f"Erro inesperado ao fechar conexão: {e}")
        logging.info("Encerrando cliente")
        
        # Salva os resultados em um arquivo JSON
        with open("results_http3.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        logging.info("Resultados salvos em 'results_http3.json'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HTTP/3 Client")
    parser.add_argument("--host", type=str, default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=4433, help="Server port")
    args = parser.parse_args()
    
    logging.info("Iniciando cliente_http3.py")
    try:
        asyncio.run(main(args.host, args.port))
    except Exception as e:
        logging.error(f"Erro fatal: {e}")