import httpx
import time
import asyncio
import argparse
import json  # Adicionado para salvar os resultados
import os

HTTP1_DIR = "http1.1"
os.makedirs(HTTP1_DIR, exist_ok=True)

async def make_request(client, endpoint):
    start_time = time.perf_counter()
    response = await client.get(f"https://127.0.0.1:5000{endpoint}")  # sem verify aqui!
    latency = time.perf_counter() - start_time
    return {
        "endpoint": endpoint,
        "status": response.status_code,
        "latency": latency,
        "content_length": len(response.content),
        "content": response.text[:100]  # Limita para evitar impressão longa
    }

async def main(host="127.0.0.1", port=5000):
    endpoints = [
        "/workloads/web/10kb.html", "/workloads/web/25kb.html", "/workloads/web/50kb.html",
        "/workloads/audio/1mb.mp3", "/workloads/audio/3mb.mp3", "/workloads/audio/5mb.mp3",
        "/workloads/video/20mb.mp4", "/workloads/video/35mb.mp4", "/workloads/video/50mb.mp4"
    ]
    results = []
    async with httpx.AsyncClient(verify=False) as client:  # <- aqui!
        for endpoint in endpoints:
            try:
                result = await make_request(client, endpoint)
                print(f"🔻 Endpoint: {result['endpoint']}")
                print(f"📦 Status: {result['status']}")
                print(f"⏱ Latência: {result['latency']:.3f} segundos")
                print(f"📏 Tamanho: {result['content_length']} bytes")
                print(f"📜 Conteúdo (primeiros 100 bytes): {result['content']}\n")
                results.append({
                    "endpoint": result["endpoint"],
                    "status": result["status"],
                    "content_length": result["content_length"],
                    "content": result["content"],
                    "latency": result["latency"]
                })
            except Exception as e:
                print(f"❌ Erro ao acessar {endpoint}: {e}\n")
    with open(os.path.join(HTTP1_DIR, "results_http1.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("✅ Resultados salvos em 'results_http1.json'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))