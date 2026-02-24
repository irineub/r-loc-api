from fastapi import APIRouter, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import shutil
import os
import re
import mimetypes
import json

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
CONFIG_FILE = "system_config.json"

# Ensure PDF mime type is registered
mimetypes.add_type("application/pdf", ".pdf")


def _sanitize_filename(name: str) -> str:
    """Keep only safe characters; collapse spaces/dashes."""
    name = os.path.basename(name)
    name = re.sub(r'[^\w\-\.]+', '-', name, flags=re.UNICODE)
    name = re.sub(r'-{2,}', '-', name).strip('-')
    return name or 'file'


def _build_base_url(request: Request) -> str:
    """Build the correct public base URL, respecting reverse-proxy headers and ngrok config."""
    # Primeiro verifica se URL externa pública está configurada (Upload Config)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                upload_config = config.get("upload", {})
                if upload_config.get("public_url"):
                    return upload_config.get("public_url").rstrip('/')
                
                # Tratar retrocompatibilidade
                ngrok_config = config.get("ngrok", {})
                if ngrok_config.get("enabled") and ngrok_config.get("url"):
                    return ngrok_config.get("url").rstrip('/')
        except Exception as e:
            print(f"Error reading config for public URL: {e}")

    # Se não, continua com o comportamento padrão
    forwarded_host = request.headers.get('x-forwarded-host', '')
    forwarded_proto = request.headers.get('x-forwarded-proto', '')
    if forwarded_host:
        scheme = forwarded_proto or 'https'
        return f"{scheme}://{forwarded_host}"
    return str(request.base_url).rstrip('/')


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    original_name = file.filename or 'documento.pdf'
    safe_name = _sanitize_filename(original_name)
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    # Avoid overwriting with a timestamp suffix
    if os.path.exists(file_path):
        base, ext = os.path.splitext(safe_name)
        import time
        safe_name = f"{base}_{int(time.time())}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Use /files/ endpoint (served by FastAPI with correct Content-Type)
    # instead of /uploads/ (served by nginx which may have wrong mime type)
    base_url = _build_base_url(request)
    file_url = f"{base_url}/files/{safe_name}"

    return JSONResponse(content={"url": file_url})


@router.get("/files/{filename}")
async def serve_file(filename: str):
    """Serve uploaded files with correct Content-Type headers."""
    # Sanitize to prevent path traversal
    safe_name = _sanitize_filename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=safe_name,
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'}
    )
