# 📊 Avaliação Comparativa de Desempenho: HTTP/3 vs HTTP/1.1

Este projeto realiza uma avaliação comparativa de desempenho entre os protocolos **HTTP/3** e **HTTP/1.1**, utilizando:

- Servidores e clientes em **Python**
- Análise de resultados com **matplotlib**

## 👤 Autores
- [Carllos-Mendes](https://github.com/Carllos-Mendes)
- [Daniel](https://github.com/Erysimn)
- [liviavbarbosa](https://github.com/liviavbarbosa)
- [LuizaVelasque](https://github.com/LuizaVelasque)
- [IsaacPerod](https://github.com/IsaacPerod)

## ⚙️ Requisitos e Ambiente

Para executar o projeto, instale as dependências listadas abaixo.  
As instruções são voltadas para **Windows**, mas podem ser adaptadas para outros sistemas operacionais.  
O projeto foi testado no ambiente **Windows com VS Code e PowerShell**.

----------------------------------

## 🐍 Guia de Instalação do Python

- **Versão recomendada:** Python 3.10.9  
  (devido a possíveis incompatibilidades do `aioquic` com versões mais recentes)

- **Download:** [Python 3.10.9](https://www.python.org/downloads/release/python-3109/)

- **Instalação:**  
  Durante a instalação, marque a opção `Add Python to PATH`.

- **Verificação:**
  ```powershell
  python --version
  ```
  **Esperado:** Python 3.10.9

⚠️ Se você estiver usando Python 3.13.1, mude para 3.10.9 caso ocorra erro como ConnectionError.

## 📦 Pacotes Python Utilizados

- `aioquic==0.9.25`: Suporte ao HTTP/3 e QUIC (`http3/server_http3.py` e `http3/cliente_http3.py`)
- `cryptography`: Manipulação de certificados
- `pyOpenSSL`: Suporte a SSL/TLS
- `flask`: Servidor HTTP/1.1 (`http1.1/server_http1.py`)
- `httpx`: Cliente HTTP/1.1 (`http1.1/cliente_http1.py`)
- `matplotlib`: Análise de resultados (`analyze.py`)

### ✅ Instalação dos Pacotes

1. **Crie um ambiente virtual (recomendado):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. **Instale os pacotes necessários:**
   ```powershell
   pip install aioquic==0.9.25 cryptography pyOpenSSL flask httpx matplotlib
   ```

## 🔑 OpenSSL

O OpenSSL é necessário para gerar os certificados (`cert.pem`, `key.pem`) usados pelos servidores.

### 📥 Versão:
- **Win64 OpenSSL v3.2.3 Light** (ou mais recente)

### ⚙️ Instalação:

1. Baixe o instalador **Win64 OpenSSL v3.2.3 Light** (~10MB).
   - [Win64 OpenSSL - Download](https://slproweb.com/products/Win32OpenSSL.html)

2. Instale o OpenSSL em **C:\Program Files\OpenSSL-Win64**.

3. Durante a instalação, marque a opção **"Copy OpenSSL DLLs to the Windows system directory"**.

4. **Adicione ao PATH manualmente (se necessário):**
    ```powershell
    $env:Path += ";C:\Program Files\OpenSSL-Win64\bin"
    setx PATH "$env:Path;C:\Program Files\OpenSSL-Win64\bin"
    ```
5. Feche e reabra o PowerShell.

6. **Verifique a instalação:**
   ```powershell
   openssl version
   ```
   **Esperado:** OpenSSL 3.2.3 10 Oct 2024 (ou similar).

### 📝 Gerar Certificados

No diretório do projeto, gere os certificados:
```powershell
cd C:\Faculdade\Redes\testeDesempenho
openssl req -x509 -newkey rsa:2048 -nodes -sha256 -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
```

## 📂 Estrutura do Projeto

Certifique-se de que o diretório do projeto contenha a seguinte estrutura de arquivos:

```plaintext
C:\Faculdade\Redes\testeDesempenho\
├── workloads\
│   ├── web\
│   │   ├── 10kb.html
│   │   ├── 25kb.html
│   │   └── 50kb.html
│   ├── audio\
│   │   ├── 1mb.mp3
│   │   ├── 3mb.mp3
│   │   └── 5mb.mp3
│   └── video\
│       ├── 20mb.mp4
│       ├── 35mb.mp4
│       └── 50mb.mp4
├── cert.pem
├── key.pem
├── http1.1\
│   ├── server_http1.py
│   ├── cliente_http1.py
│   └── results_http1.json
├── http3\
│   ├── server_http3.py
│   ├── cliente_http3.py
│   └── results_http3.json
├── analyze.py
├── results\
│   └── (arquivos de análise gerados)
```

### 📝 Arquivos de Teste:
Crie os arquivos de workload conforme necessário. Para arquivos binários de exemplo:
```powershell
cd C:\Faculdade\Redes\testeDesempenho
mkdir workloads
mkdir workloads\web workloads\audio workloads\video
fsutil file createnew workloads\audio\1mb.mp3 1048576
fsutil file createnew workloads\audio\3mb.mp3 3145728
fsutil file createnew workloads\audio\5mb.mp3 5242880
fsutil file createnew workloads\video\20mb.mp4 20971520
fsutil file createnew workloads\video\35mb.mp4 36700160
fsutil file createnew workloads\video\50mb.mp4 52428800
```
Crie os arquivos HTML manualmente ou usando scripts.

### 📝 Certificados:
Gere os certificados cert.pem e key.pem com o OpenSSL (como descrito acima).

----------------------------------

## 🏃 Como Executar

### 1. Configurar o Ambiente:

- Instale o **Python 3.10.9**, os pacotes Python e o **OpenSSL** conforme as instruções anteriores.
- Crie os arquivos de teste e os certificados.

### 2. Executar os Servidores:

```powershell
python http1.1/server_http1.py
python http3/server_http3.py
```

### 3. Executar os Clientes:

```powershell
python http1.1/cliente_http1.py
python http3/cliente_http3.py
```

### 4. Analisar os Resultados:
```powershell
python analyze.py
```

----------------------------------

## 🛠️ Notas de Depuração

### 🔥 Firewall:

O HTTP/3 utiliza **QUIC (UDP)** na porta **4433**. Certifique-se de liberar a no firewall:

```powershell
netsh advfirewall firewall add rule name="Allow UDP 4433" dir=in action=allow protocol=UDP localport=4433
```

#### ⚠️ ConnectionError no HTTP/3:
1. Verifique os certificados:
   ```powershell
   openssl x509 -in cert.pem -text -noout
   ```
2. **Dica:** Use Python 3.10.9 se houver problemas com aioquic no Python 3.13.1.