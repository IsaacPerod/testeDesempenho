import pandas as pd
import json
import sys
from contextlib import redirect_stdout

def analyze_results(http1_file="results_http1.json", http3_file="results_http3.json", output_file="analysis_results.txt"):
    try:
        # Carregar dados HTTP/1.1
        with open(http1_file, "r", encoding="utf-8") as f1:
            http1_data = json.load(f1)  # Carregar como um único JSON

        # Carregar dados HTTP/3
        with open(http3_file, "r", encoding="utf-8") as f3:
            http3_data = json.load(f3)  # Carregar como um único JSON

        # Processar métricas HTTP/1.1
        http1_metrics = [
            {
                "http_req_duration": d["metrics"]["http_req_duration"],
                "endpoint": d["url"].replace("http://127.0.0.1:5000", ""),  # Normalizar endpoint
                "protocol": "HTTP/1.1"
            }
            for d in http1_data if d.get("type") == "Point" and "http_req_duration" in d.get("metrics", {})
        ]

        # Processar métricas HTTP/3
        http3_metrics = [
            {
                "http_req_duration": d["elapsed_time"] * 1000,  # Converter segundos para ms
                "endpoint": d["endpoint"],
                "protocol": "HTTP/3"
            }
            for d in http3_data if "elapsed_time" in d and "endpoint" in d
        ]

        # Combinar os dados em um único DataFrame
        combined_data = http1_metrics + http3_metrics
        if not combined_data:
            raise ValueError("Nenhum dado válido encontrado nos arquivos de resultados")

        df = pd.DataFrame(combined_data)

        # Normalizar endpoints para comparação
        df["endpoint"] = df["endpoint"].replace({"/file/1mb": "/file/1mb.bin"})  # Corrigir inconsistência

        # Abrir arquivo para escrita
        with open(output_file, "w", encoding="utf-8") as f:
            # Redirecionar stdout para o arquivo (e manter console)
            def print_to_file_and_console(*args, **kwargs):
                print(*args, file=f, **kwargs)  # Escrever no arquivo
                print(*args, **kwargs)  # Escrever no console

            # Estatísticas gerais
            print_to_file_and_console("📊 Estatísticas Gerais de Latência (em ms):")
            print_to_file_and_console(df["http_req_duration"].describe())

            # Estatísticas por protocolo
            print_to_file_and_console("\n📈 Estatísticas de Latência por Protocolo:")
            print_to_file_and_console(df.groupby("protocol")["http_req_duration"].describe())

            # Estatísticas por endpoint
            print_to_file_and_console("\n📈 Estatísticas de Latência por Endpoint:")
            print_to_file_and_console(df.groupby(["protocol", "endpoint"])["http_req_duration"].describe())

            # Comparação entre HTTP/1.1 e HTTP/3
            print_to_file_and_console("\n📊 Comparação de Latência entre HTTP/1.1 e HTTP/3:")
            http1_mean = df[df["protocol"] == "HTTP/1.1"]["http_req_duration"].mean()
            http3_mean = df[df["protocol"] == "HTTP/3"]["http_req_duration"].mean()
            print_to_file_and_console(f"HTTP/1.1 Média de Latência: {http1_mean:.2f} ms")
            print_to_file_and_console(f"HTTP/3 Média de Latência: {http3_mean:.2f} ms")
            print_to_file_and_console(f"🔍 Diferença Média: {http1_mean - http3_mean:.2f} ms")

            # Comparação por endpoint
            print_to_file_and_console("\n📊 Comparação de Latência por Endpoint entre HTTP/1.1 e HTTP/3:")
            for endpoint in df["endpoint"].unique():
                if endpoint in ["/file/10mb", "/file/100mb"]:
                    continue  # Ignorar endpoints exclusivos do HTTP/1.1
                http1_time = df[(df["protocol"] == "HTTP/1.1") & (df["endpoint"] == endpoint)]["http_req_duration"].mean()
                http3_time = df[(df["protocol"] == "HTTP/3") & (df["endpoint"] == endpoint)]["http_req_duration"].mean()
                print_to_file_and_console(f"Endpoint {endpoint}:")
                print_to_file_and_console(f"  HTTP/1.1: {http1_time:.2f} ms")
                print_to_file_and_console(f"  HTTP/3: {http3_time:.2f} ms")
                print_to_file_and_console(f"  Diferença: {http1_time - http3_time:.2f} ms")

        print(f"✅ Resultados salvos em {output_file}")

    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e.filename}")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")
    except Exception as e:
        print(f"❌ Erro ao analisar os resultados: {e}")

if __name__ == "__main__":
    analyze_results()