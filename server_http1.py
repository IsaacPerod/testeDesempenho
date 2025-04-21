from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Resposta via HTTP/1.1"

@app.route("/json")
def json_response():
    return jsonify({"message": "Hello, World!"})

@app.route("/file/<size>")
def serve_file(size):
    sizes = {"1mb": "1mb.bin", "10mb": "10mb.bin", "100mb": "100mb.bin"}
    if size not in sizes:
        return "Tamanho inválido", 400
    file_path = os.path.join("files", sizes[size])
    if not os.path.exists(file_path):
        return "Arquivo não encontrado", 404
    return send_file(file_path, mimetype="application/octet-stream")

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(host="127.0.0.1", port=int(port), threaded=True)