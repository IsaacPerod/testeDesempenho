import json
import csv
import os
from statistics import mean, stdev
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

def load_results(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Padroniza o campo de latência para "latency"
        for item in data:
            if "elapsed_time" in item:
                item["latency"] = item.pop("elapsed_time")
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Erro ao carregar {file_path}")
        return []

def analyze_comparison(
    http1_file=os.path.join("http1.1", "results_http1.json"),
    http3_file=os.path.join("http3", "results_http3.json")
):
    # Garante que a pasta results existe
    os.makedirs(RESULTS_DIR, exist_ok=True)

    http1_results = load_results(http1_file)
    http3_results = load_results(http3_file)
    
    if not http1_results or not http3_results:
        print("Resultados não encontrados ou inválidos.")
        return

    # Organizar dados por endpoint e protocolo
    all_data = {}
    for protocol, results in [("http1", http1_results), ("http3", http3_results)]:
        for item in results:
            endpoint = item.get("endpoint")
            if not endpoint:
                continue
            if endpoint not in all_data:
                all_data[endpoint] = {}
            if protocol not in all_data[endpoint]:
                all_data[endpoint][protocol] = []
            all_data[endpoint][protocol].append(item)

    # Salvar todos os dados em JSON estruturado
    with open(os.path.join(RESULTS_DIR, "analise_completa.json"), "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("Todos os dados salvos em results/analise_completa.json")

    # Salvar dados tabulares em CSV (um registro por endpoint/protocolo/execução)
    with open(os.path.join(RESULTS_DIR, "analise_completa.csv"), "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["endpoint", "protocolo", "latency", "status", "content_length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for endpoint, protos in all_data.items():
            for proto, items in protos.items():
                for item in items:
                    writer.writerow({
                        "endpoint": endpoint,
                        "protocolo": proto,
                        "latency": item.get("latency"),
                        "status": item.get("status"),
                        "content_length": item.get("content_length"),
                    })
    print("Todos os dados salvos em results/analise_completa.csv")

    # Salvar médias e desvios padrão por endpoint/protocolo
    resumo = []
    endpoints = sorted(all_data.keys())
    for endpoint in endpoints:
        for proto in ["http1", "http3"]:
            items = all_data[endpoint].get(proto, [])
            latencies = [item.get("latency") for item in items if item.get("latency") is not None]
            if latencies:
                resumo.append({
                    "endpoint": endpoint,
                    "protocolo": proto,
                    "media_latency": mean(latencies),
                    "desvio_latency": stdev(latencies) if len(latencies) > 1 else 0,
                    "n_amostras": len(latencies)
                })
    with open(os.path.join(RESULTS_DIR, "analise_resumo.csv"), "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["endpoint", "protocolo", "media_latency", "desvio_latency", "n_amostras"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in resumo:
            writer.writerow(row)
    print("Resumo estatístico salvo em results/analise_resumo.csv")

    # Gráfico de latência (linha)
    plt.figure(figsize=(12, 6))
    for protocol, color in [("http1", "#1f77b4"), ("http3", "#ff7f0e")]:
        endpoints = sorted(all_data.keys())
        latencies = []
        for ep in endpoints:
            items = all_data[ep].get(protocol, [])
            vals = [item.get("latency") for item in items if item.get("latency") is not None]
            latencies.append(mean(vals) if vals else 0)
        plt.plot(endpoints, latencies, label=f"{protocol.upper()} Latência", color=color, marker='o')
    plt.xlabel("Endpoint")
    plt.ylabel("Latência Média (s)")
    plt.title("Comparação de Latência: HTTP/1.1 vs HTTP/3")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "grafico_latencia_linha.png"), dpi=200, bbox_inches="tight")
    print("Gráfico salvo como results/grafico_latencia_linha.png")
    plt.show()

if __name__ == "__main__":
    analyze_comparison()