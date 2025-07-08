import json
import csv
import os
from statistics import mean, stdev
import time
import matplotlib.pyplot as plt
import psutil

RESULTS_DIR = "results"

def load_results(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            if "elapsed_time" in item:
                item["latency"] = item.pop("elapsed_time")
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Erro ao carregar {file_path}")
        return []

def salvar_csv_analise_completa(all_data, metric_name):
    with open(os.path.join(RESULTS_DIR, f"analise_completa_{metric_name}.csv"), "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["endpoint", "protocolo", metric_name]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for endpoint, protos in all_data.items():
            for proto, items in protos.items():
                for item in items:
                    writer.writerow({
                        "endpoint": endpoint,
                        "protocolo": proto,
                        metric_name: item.get(metric_name),
                    })
    print(f"Dados de {metric_name} salvos em results/analise_completa_{metric_name}.csv")

def salvar_resumo(all_data, metric_name):
    resumo = []
    for endpoint in sorted(all_data.keys()):
        for proto in ["http1", "http3"]:
            items = all_data[endpoint].get(proto, [])
            valores = [item.get(metric_name) for item in items if item.get(metric_name) is not None]
            if valores:
                resumo.append({
                    "endpoint": endpoint,
                    "protocolo": proto,
                    f"media_{metric_name}": mean(valores),
                    f"desvio_{metric_name}": stdev(valores) if len(valores) > 1 else 0,
                    "n_amostras": len(valores)
                })
    with open(os.path.join(RESULTS_DIR, f"analise_resumo_{metric_name}.csv"), "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["endpoint", "protocolo", f"media_{metric_name}", f"desvio_{metric_name}", "n_amostras"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in resumo:
            writer.writerow(row)
    print(f"Resumo estatístico salvo em results/analise_resumo_{metric_name}.csv")

def coletar_cpu_ram_durante_teste(duracao_segundos=10, intervalo=0.5):
    cpu_usos = []
    ram_usos = []
    for _ in range(int(duracao_segundos / intervalo)):
        cpu_usos.append(psutil.cpu_percent(interval=None))  
        ram_usos.append(psutil.virtual_memory().used / (1024*1024))  
        time.sleep(intervalo)
    cpu_media = sum(cpu_usos) / len(cpu_usos)
    ram_media = sum(ram_usos) / len(ram_usos)
    return cpu_media, ram_media

def gerar_grafico(all_data, metric_name, y_label, title, output_name):
    plt.figure(figsize=(12, 6))
    for protocol, color in [("http1", "#1f77b4"), ("http3", "#ff7f0e")]:
        endpoints = sorted(all_data.keys())
        valores = []
        for ep in endpoints:
            items = all_data[ep].get(protocol, [])
            vals = [item.get(metric_name) for item in items if item.get(metric_name) is not None]
            valores.append(mean(vals) if vals else 0)
        plt.plot(endpoints, valores, label=f"{protocol.upper()} {metric_name.upper()}", color=color, marker='o')
    plt.xlabel("Endpoint")
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, output_name), dpi=200, bbox_inches="tight")
    print(f"Gráfico salvo como results/{output_name}")
    plt.show()

def analyze_comparison(
    http1_file=os.path.join("http1.1", "results_http1.json"),
    http3_file=os.path.join("http3", "results_http3.json")
):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    http1_results = load_results(http1_file)
    http3_results = load_results(http3_file)

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

    for endpoint, protos in all_data.items():
        for proto in protos:
            cpu_media, ram_media = coletar_cpu_ram_durante_teste(duracao_segundos=10, intervalo=0.5)
            for item in all_data[endpoint][proto]:
                item["cpu"] = cpu_media
                item["ram"] = ram_media

    with open(os.path.join(RESULTS_DIR, "analise_completa.json"), "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("Todos os dados salvos em results/analise_completa.json")

    # Gráficos e CSVs
    salvar_csv_analise_completa(all_data, "latency")
    salvar_resumo(all_data, "latency")
    gerar_grafico(
        all_data, "latency", "Latência Média (s)",
        "Comparação de Latência: HTTP/1.1 vs HTTP/3",
        "grafico_latencia_linha.png"
    )

    salvar_csv_analise_completa(all_data, "cpu")
    salvar_resumo(all_data, "cpu")
    gerar_grafico(
        all_data, "cpu", "Uso Médio de CPU (%)",
        "Comparação de Uso de CPU: HTTP/1.1 vs HTTP/3",
        "grafico_cpu_linha.png"
    )

    salvar_csv_analise_completa(all_data, "ram")
    salvar_resumo(all_data, "ram")
    gerar_grafico(
        all_data, "ram", "Uso Médio de RAM (MB)",
        "Comparação de Uso de Memória RAM: HTTP/1.1 vs HTTP/3",
        "grafico_ram_linha.png"
    )

if __name__ == "__main__":
    analyze_comparison()