import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.vision import process_image
from app.config import logger, NOTES_DIR
import uvicorn

app = FastAPI(title="Lectura API")


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Поддерживаются только JPG и PNG")

    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = await process_image(temp_path)
        if not text:
            raise HTTPException(status_code=500, detail="Ошибка обработки")

        note_filename = f"{os.path.splitext(file.filename)[0]}.md"
        note_path = os.path.join(NOTES_DIR, note_filename)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(text)

        return {
            "status": "success",
            "content": text,
            "saved_to": note_filename
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)