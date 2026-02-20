from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Construct the full URL
    # Replace http with https if needed, depending on reverse proxy setup
    base_url = str(request.base_url)
    
    # If running behind a proxy that terminates SSL, request.base_url might be http
    # Uazapi might require https. For now we use what FastAPI sees.
    file_url = f"{base_url}uploads/{unique_filename}"

    return JSONResponse(content={"url": file_url})
