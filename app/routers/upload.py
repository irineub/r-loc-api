from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
import shutil
import os
import re

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    """Keep only safe characters; collapse spaces/dashes."""
    # Remove path separators and dangerous characters
    name = os.path.basename(name)
    # Allow letters, digits, dash, underscore, dot
    name = re.sub(r'[^\w\-\.]+', '-', name, flags=re.UNICODE)
    name = re.sub(r'-{2,}', '-', name).strip('-')
    return name or 'file'


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Use the original filename (sanitized) so WhatsApp shows a meaningful name
    original_name = file.filename or 'documento.pdf'
    safe_name = _sanitize_filename(original_name)
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    # If a file with this name already exists, add a short suffix to avoid collision
    if os.path.exists(file_path):
        base, ext = os.path.splitext(safe_name)
        import time
        safe_name = f"{base}_{int(time.time())}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Build a public URL. Behind a reverse proxy (nginx/caddy with HTTPS),
    # request.base_url may be http://127.0.0.1 — use X-Forwarded-Proto when available.
    forwarded_proto = request.headers.get('x-forwarded-proto', '')
    forwarded_host = request.headers.get('x-forwarded-host', '')

    if forwarded_host:
        scheme = forwarded_proto or 'https'
        file_url = f"{scheme}://{forwarded_host}/uploads/{safe_name}"
    else:
        base_url = str(request.base_url).rstrip('/')
        file_url = f"{base_url}/uploads/{safe_name}"

    return JSONResponse(content={"url": file_url})
