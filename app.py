from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return "Response via HTTP/3"

@app.get("/json")
async def json():
    return {"message": "Hello, World!"}

@app.get("/file/{size}")
async def file(size: str):
    sizes = {"1mb.bin": "1mb.bin", "10mb.bin": "10mb.bin", "100mb.bin": "100mb.bin"}
    if size in sizes:
        file_path = os.path.join("files", sizes[size])
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        return {"error": "File not found"}, 404
    return {"error": "Invalid size"}, 400