from flask import Flask, send_file, abort
import os

app = Flask(__name__)
WORKLOADS_DIR = os.path.join(os.getcwd(), "workloads")

@app.route("/")
def home():
    return "Resposta via HTTP/1.1"

@app.route("/workloads/<path:rel_path>")
def serve_file(rel_path):
    file_path = os.path.join(WORKLOADS_DIR, rel_path.replace("/", os.sep))
    if not os.path.exists(file_path):
        abort(404, description="Arquivo não encontrado")
    mime_types = {
        ".html": "text/html",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4"
    }
    ext = os.path.splitext(file_path)[1].lower()
    mimetype = mime_types.get(ext, "application/octet-stream")
    return send_file(file_path, mimetype=mimetype)

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(host="127.0.0.1", port=int(port), ssl_context=("cert.pem", "key.pem"))