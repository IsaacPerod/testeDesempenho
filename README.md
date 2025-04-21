# 📊 Avaliação Comparativa de Desempenho: HTTP/3 vs HTTP/1.1

Este projeto realiza uma avaliação comparativa de desempenho entre os protocolos **HTTP/3** e **HTTP/1.1**, utilizando:

- Servidores e clientes em **Python**
- Testes de carga com **k6**
- Análise de resultados com **pandas**

## 👤 Autores
- [Carllos-Mendes](https://github.com/Carllos-Mendes)

- [Erysimn](https://github.com/Erysimn)

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
  ```bash
  python --version
  
**Esperado:** Python 3.10.9

⚠️ Se você estiver usando Python 3.13.1, mude para 3.10.9 caso ocorra erro como ConnectionError.

## 📦 Pacotes Python Utilizados

- `aioquic==0.9.25`: Suporte ao HTTP/3 e QUIC (usado em `server_http3.py` e `cliente_http3.py`)
- `cryptography`: Manipulação de certificados
- `pyOpenSSL`: Suporte a SSL/TLS
- `flask`: Servidor HTTP/1.1 (`server_http1.py`)
- `requests`: Cliente HTTP/1.1 (`cliente_http1.py`)
- `pandas`: Análise de resultados (`analyze.py`)
- *(Opcional)* `gunicorn`: Melhora a taxa de sucesso do HTTP/1.1 no k6

### ✅ Instalação dos Pacotes

1. **Crie um ambiente virtual (recomendado):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. **Instale os pacotes necessários:**
   ```powershell
   pip install aioquic==0.9.25 cryptography pyOpenSSL flask requests pandas
   ```
3. ***(Opcional para HTTP/1.1): Para melhorar a taxa de sucesso do HTTP/1.1:***
   ```powershell
   pip install gunicorn
   ```

## 🔑 OpenSSL

O OpenSSL é necessário para gerar os certificados (`cert.pem`, `key.pem`) usados pelo servidor HTTP/3.

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
cd C:\Faculdade\Redes\testeDesempenho # Substitua pelo seu caminho
openssl req -x509 -newkey rsa:2048 -nodes -sha256 -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
```

## 🚀 k6

O k6 é utilizado para realizar os testes de carga e comparar o desempenho entre **HTTP/3** e **HTTP/1.1**.

### 📥 Versão recomendada:
- **v0.54.0** (ou mais recente)

### ⚙️ Instalação:

1. Baixe o executável para **Windows 64-bit**:
   - [k6 Downloads](https://k6.io/docs/getting-started/installation/)

2. Mova o arquivo `k6.exe` para **C:\Program Files\k6\k6.exe**.

3. **Adicione ao PATH**:
   ```powershell
   $env:Path += ";C:\Program Files\k6"
   setx PATH "$env:Path;C:\Program Files\k6"
   
4. Verifique a instalação:
   ```powershell
   k6 version
   ```
**Esperado:** k6 v0.54.0 (ou similar).

----------------------------------

## 📂 Estrutura do Projeto

Certifique-se de que o diretório do projeto contenha a seguinte estrutura de arquivos:

```plaintext
C:\Faculdade\Redes\testeDesempenho\ # Substitua pelo seu caminho
├── files\
│   ├── 1mb.bin
│   ├── 10mb.bin
│   ├── 100mb.bin
├── cert.pem
├── key.pem
├── server_http1.py
├── server_http3.py
├── cliente_http1.py
├── cliente_http3.py
├── load-test.js
├── analyze.py
├── results.json
```

### 📝 Arquivos de Teste:
Crie os arquivos 1mb.bin, 10mb.bin e 100mb.bin se não existirem:
```powershell
cd C:\Faculdade\Redes\testeDesempenho
mkdir files
fsutil file createnew files\1mb.bin 1048576
fsutil file createnew files\10mb.bin 10485760
fsutil file createnew files\100mb.bin 104857600
```
### 📝 Certificados:
Gere os certificados cert.pem e key.pem com o OpenSSL (como descrito acima).

----------------------------------

## 🏃 Como Executar

### 1. Configurar o Ambiente:

- Instale o **Python 3.10.9**, os pacotes Python, o **OpenSSL** e o **k6** conforme as instruções anteriores.
- Crie os arquivos de teste e os certificados.

### 2. Executar os Servidores:

```powershell
python server_http1.py
python server_http3.py
```

### 3. Executar os Clientes:

```powershell
python cliente_http1.py
python cliente_http3.py
```

### 4. Executar Testes de Carga:
```powershell
& "C:\Program Files\k6\k6.exe" run load-test.js --out json=results.json --console-output
```

### 5. Analisar os Resultados:
```powershell
python analyze.py
```

### *6. (Opcional) Melhorar o HTTP/1.1:*
Para melhorar a taxa de sucesso no k6 (atualmente 38% para HTTP/1.1), você pode usar o gunicorn:
```powershell
gunicorn --workers 4 server_http1:app
```

----------------------------------

## 🛠️ Notas de Depuração

### 🔥 Firewall:

O HTTP/3 utiliza **QUIC (UDP)** na porta **4433**. Certifique-se de liberar a porta no firewall:

```powershell
netsh advfirewall firewall add rule name="Allow UDP 4433" dir=in action=allow protocol=UDP localport=4433
```

#### ⚠️ ConnectionError no HTTP/3:
1. Verifique os certificados:
   ```powershell
   openssl x509 -in cert.pem -text -noout
   ```
2. **Dica:** Use Python 3.10.9 se houver problemas com aioquic no Python 3.13.1.

3. Adicione logs detalhados ao server_http3.py (nível DEBUG) para diagnosticar o problema.

#### 🚫 k6 com 0% de Sucesso no HTTP/3:
1. Certifique-se de que o server_http3.py está rodando e acessível em localhost:4433:
   ```powershell
   netstat -ano | findstr :4433
   ```
2. Se precisar de ajuda com erros, compartilhe os logs dos servidores e clientes.
