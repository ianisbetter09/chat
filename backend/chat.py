from fastapi import APIRouter, UploadFile, File
import shutil
import os

router = APIRouter(prefix="/chat")

UPLOAD_DIR = "backend/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(user: str, room: str, file: UploadFile = File(...)):
    filepath = f"{UPLOAD_DIR}/{file.filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file": file.filename}
