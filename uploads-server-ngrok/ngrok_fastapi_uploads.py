from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Ngrok Uploads Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho absoluto para a pasta uploads baseada na raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Garante que a pasta existe (embora na API principal ela já seja criada)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Monta o diretório uploads para servir os arquivos estáticos
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Ngrok Uploads Server is running"}

if __name__ == "__main__":
    import uvicorn
    # Roda na porta 8030
    uvicorn.run("ngrok_fastapi_uploads:app", host="0.0.0.0", port=8030, reload=True)
