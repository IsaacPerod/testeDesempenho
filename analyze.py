import pandas as pd
import json

def analyze_results(file_path="results.json"):
    with open(file_path) as f:
        data = [json.loads(line) for line in f if line.strip()]

    metrics = [d['metrics'] for d in data if d['type'] == 'Point' and 'http_req_duration' in d['metrics']]
    df = pd.DataFrame(metrics)

    print("📊 Estatísticas de Latência (em ms):")
    print(df['http_req_duration'].describe())

    # Separar por protocolo (baseado na URL)
    df['protocol'] = df['url'].apply(lambda x: 'HTTP/1.1' if ':5000' in x else 'HTTP/3')
    print("\n📈 Latência por Protocolo:")
    print(df.groupby('protocol')['http_req_duration'].describe())

if __name__ == "__main__":
    analyze_results()