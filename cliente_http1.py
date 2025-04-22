import httpx
import time
import asyncio
import argparse
import json  # Adicionado para salvar os resultados

async def make_request(client, endpoint):
    start_time = time.perf_counter()
    response = await client.get(f"http://127.0.0.1:5000{endpoint}")
    latency = time.perf_counter() - start_time
    return {
        "endpoint": endpoint,
        "status": response.status_code,
        "latency": latency,
        "content_length": len(response.content),
        "content": response.text[:100]  # Limita para evitar impressão longa
    }

async def main(host="127.0.0.1", port=5000):
    endpoints = ["/", "/json", "/file/1mb"]
    results = []  # Lista para armazenar os resultados
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                result = await make_request(client, endpoint)
                print(f"🔻 Endpoint: {result['endpoint']}")
                print(f"📦 Status: {result['status']}")
                print(f"⏱ Latência: {result['latency']:.3f} segundos")
                print(f"📏 Tamanho: {result['content_length']} bytes")
                print(f"📜 Conteúdo (primeiros 100 bytes): {result['content']}\n")
                
                # Adiciona o resultado à lista
                results.append({
                    "type": "Point",
                    "metrics": {"http_req_duration": result["latency"] * 1000},  # Converte para ms
                    "url": f"http://{host}:{port}{result['endpoint']}"
                })
            except Exception as e:
                print(f"❌ Erro ao acessar {endpoint}: {e}\n")
    
    # Salva os resultados em um arquivo JSON
    with open("results_http1.json", "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    print("✅ Resultados salvos em 'results_http1.json'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))